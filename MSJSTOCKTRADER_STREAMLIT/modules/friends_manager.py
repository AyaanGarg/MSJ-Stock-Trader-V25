import json
import os
import pandas as pd
from typing import Dict, List
from datetime import datetime
from modules.portfolio_manager import PortfolioManager
from modules.market_data import MarketData


class FriendsManager:
    """Manages friend relationships and social features."""
    
    def __init__(self):
        self.portfolio_manager = PortfolioManager()
        self.market_data = MarketData()
        self.users_file = "data/users.json"
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs("data", exist_ok=True)
    
    def _load_users(self) -> Dict:
        """Load users from file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def search_users(self, query: str, current_user_id: str) -> List[Dict]:
        """Search for users by username to add as friends."""
        users = self._load_users()
        results = []
        
        query_lower = query.lower()
        
        for user_key, user_data in users.items():
            if user_data['user_id'] == current_user_id:
                continue  # Skip current user
            
            username = user_data.get('username', '').lower()
            first_name = user_data.get('first_name', '').lower()
            last_name = user_data.get('last_name', '').lower()
            
            if (query_lower in username or 
                query_lower in first_name or 
                query_lower in last_name):
                
                results.append({
                    'user_id': user_data['user_id'],
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data.get('role', 'trader')
                })
        
        return results[:10]  # Limit to 10 results
    
    def send_friend_request(self, sender_id: str, target_username: str) -> Dict:
        """Send a friend request to another user."""
        users = self._load_users()
        
        # Find target user
        target_user = None
        target_key = None
        for key, user in users.items():
            if user['username'] == target_username:
                target_user = user
                target_key = key
                break
        
        if not target_user:
            return {"success": False, "message": "User not found"}
        
        # Find sender
        sender_user = None
        sender_key = None
        for key, user in users.items():
            if user['user_id'] == sender_id:
                sender_user = user
                sender_key = key
                break
        
        if not sender_user:
            return {"success": False, "message": "Sender not found"}
        
        # Check if already friends
        if 'friends' not in sender_user:
            sender_user['friends'] = []
        if 'friends' not in target_user:
            target_user['friends'] = []
        
        if target_username in sender_user['friends']:
            return {"success": False, "message": "Already friends"}
        
        # For simplicity, directly add as friends (skip pending requests)
        sender_user['friends'].append(target_username)
        target_user['friends'].append(sender_user['username'])
        
        self._save_users(users)
        
        return {
            "success": True, 
            "message": f"Successfully added {target_user['first_name']} {target_user['last_name']} as a friend!"
        }
    
    def remove_friend(self, user_id: str, friend_username: str) -> Dict:
        """Remove a friend from user's friend list."""
        users = self._load_users()
        
        # Find current user
        current_user = None
        current_key = None
        for key, user in users.items():
            if user['user_id'] == user_id:
                current_user = user
                current_key = key
                break
        
        if not current_user:
            return {"success": False, "message": "User not found"}
        
        # Find friend user
        friend_user = None
        friend_key = None
        for key, user in users.items():
            if user['username'] == friend_username:
                friend_user = user
                friend_key = key
                break
        
        if not friend_user:
            return {"success": False, "message": "Friend not found"}
        
        # Remove from both friends lists
        if 'friends' in current_user and friend_username in current_user['friends']:
            current_user['friends'].remove(friend_username)
        
        if 'friends' in friend_user and current_user['username'] in friend_user['friends']:
            friend_user['friends'].remove(current_user['username'])
        
        self._save_users(users)
        
        return {
            "success": True, 
            "message": f"Removed {friend_user['first_name']} {friend_user['last_name']} from friends"
        }
    
    def get_friends_list(self, user_id: str) -> pd.DataFrame:
        """Get user's friends list with their portfolio information."""
        users = self._load_users()
        
        # Find current user
        current_user = None
        for user in users.values():
            if user['user_id'] == user_id:
                current_user = user
                break
        
        if not current_user or 'friends' not in current_user:
            return pd.DataFrame()
        
        friends_data = []
        
        for friend_username in current_user['friends']:
            # Find friend user data
            friend_user = None
            for user in users.values():
                if user['username'] == friend_username:
                    friend_user = user
                    break
            
            if friend_user:
                # Get portfolio data
                portfolio_value = self.portfolio_manager.get_portfolio_value(friend_user['user_id'])
                cash_balance = self.portfolio_manager.get_cash_balance(friend_user['user_id'])
                daily_pnl = self.portfolio_manager.get_daily_pnl(friend_user['user_id'])
                
                friends_data.append({
                    'username': friend_user['username'],
                    'name': f"{friend_user['first_name']} {friend_user['last_name']}",
                    'portfolio_value': portfolio_value,
                    'cash_balance': cash_balance,
                    'total_value': portfolio_value + cash_balance,
                    'daily_pnl': daily_pnl,
                    'role': friend_user.get('role', 'trader')
                })
        
        return pd.DataFrame(friends_data)
    
    def get_friend_portfolio_details(self, user_id: str, friend_username: str) -> Dict:
        """Get detailed portfolio information for a specific friend."""
        users = self._load_users()
        
        # Verify friendship
        current_user = None
        for user in users.values():
            if user['user_id'] == user_id:
                current_user = user
                break
        
        if not current_user or 'friends' not in current_user:
            return {"success": False, "message": "Access denied"}
        
        if friend_username not in current_user['friends']:
            return {"success": False, "message": "Not in your friends list"}
        
        # Find friend
        friend_user = None
        for user in users.values():
            if user['username'] == friend_username:
                friend_user = user
                break
        
        if not friend_user:
            return {"success": False, "message": "Friend not found"}
        
        # Get detailed portfolio data
        positions_df = self.portfolio_manager.get_positions(friend_user['user_id'])
        portfolio_value = self.portfolio_manager.get_portfolio_value(friend_user['user_id'])
        cash_balance = self.portfolio_manager.get_cash_balance(friend_user['user_id'])
        performance = self.portfolio_manager.get_performance_summary(friend_user['user_id'])
        
        # Add current prices to positions
        if not positions_df.empty:
            positions_df['current_price'] = positions_df['symbol'].apply(
                lambda x: self.market_data.get_current_price(x)
            )
            positions_df['market_value'] = positions_df['quantity'] * positions_df['current_price']
            positions_df['unrealized_pnl'] = positions_df['market_value'] - (positions_df['quantity'] * positions_df['avg_price'])
        
        return {
            "success": True,
            "friend_info": {
                "username": friend_user['username'],
                "name": f"{friend_user['first_name']} {friend_user['last_name']}",
                "role": friend_user.get('role', 'trader')
            },
            "portfolio_summary": {
                "portfolio_value": portfolio_value,
                "cash_balance": cash_balance,
                "total_value": portfolio_value + cash_balance,
                "daily_pnl": performance.get('daily_pnl', 0),
                "total_pnl": performance.get('total_pnl', 0)
            },
            "positions": positions_df.to_dict('records') if not positions_df.empty else []
        }
    
    def get_leaderboard(self, user_id: str) -> pd.DataFrame:
        """Get leaderboard of user and their friends."""
        users = self._load_users()
        
        # Find current user
        current_user = None
        for user in users.values():
            if user['user_id'] == user_id:
                current_user = user
                break
        
        if not current_user:
            return pd.DataFrame()
        
        # Get friends list
        friends_list = current_user.get('friends', [])
        
        # Include current user and friends
        leaderboard_data = []
        
        # Add current user
        portfolio_value = self.portfolio_manager.get_portfolio_value(user_id)
        cash_balance = self.portfolio_manager.get_cash_balance(user_id)
        performance = self.portfolio_manager.get_performance_summary(user_id)
        
        leaderboard_data.append({
            'rank': 0,  # Will be calculated later
            'username': current_user['username'],
            'name': f"{current_user['first_name']} {current_user['last_name']}",
            'total_value': portfolio_value + cash_balance,
            'portfolio_value': portfolio_value,
            'cash_balance': cash_balance,
            'total_pnl': performance.get('total_pnl', 0),
            'daily_pnl': performance.get('daily_pnl', 0),
            'is_current_user': True
        })
        
        # Add friends
        for friend_username in friends_list:
            friend_user = None
            for user in users.values():
                if user['username'] == friend_username:
                    friend_user = user
                    break
            
            if friend_user:
                friend_portfolio_value = self.portfolio_manager.get_portfolio_value(friend_user['user_id'])
                friend_cash_balance = self.portfolio_manager.get_cash_balance(friend_user['user_id'])
                friend_performance = self.portfolio_manager.get_performance_summary(friend_user['user_id'])
                
                leaderboard_data.append({
                    'rank': 0,  # Will be calculated later
                    'username': friend_user['username'],
                    'name': f"{friend_user['first_name']} {friend_user['last_name']}",
                    'total_value': friend_portfolio_value + friend_cash_balance,
                    'portfolio_value': friend_portfolio_value,
                    'cash_balance': friend_cash_balance,
                    'total_pnl': friend_performance.get('total_pnl', 0),
                    'daily_pnl': friend_performance.get('daily_pnl', 0),
                    'is_current_user': False
                })
        
        # Convert to DataFrame and sort by total value
        df = pd.DataFrame(leaderboard_data)
        if not df.empty:
            df = df.sort_values('total_value', ascending=False).reset_index(drop=True)
            df['rank'] = range(1, len(df) + 1)
        
        return df
    
    def get_friends(self, user_id: str) -> List[str]:
        """Get list of friend usernames for a user."""
        users = self._load_users()
        
        # Find current user
        current_user = None
        for user in users.values():
            if user['user_id'] == user_id:
                current_user = user
                break
        
        if not current_user:
            return []
        
        return current_user.get('friends', [])