"""
Demo Account Manager for MSJSTOCKTRADER

Manages demo account access and automatic reset functionality.
Only allows one demo user at a time and resets the account every 5 minutes.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

class DemoManager:
    """Manages demo account session and automatic reset functionality."""
    
    def __init__(self):
        self.data_dir = "data"
        self.demo_session_file = os.path.join(self.data_dir, "demo_session.json")
        self.demo_backup_file = os.path.join(self.data_dir, "demo_backup.json")
        self._ensure_data_directory()
        self._initialize_demo_backup()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _initialize_demo_backup(self):
        """Initialize demo account backup if it doesn't exist."""
        if not os.path.exists(self.demo_backup_file):
            # Default demo account state
            demo_backup = {
                "user_data": {
                    "user_id": "demo_user",
                    "username": "demo",
                    "email": "demo@example.com",
                    "first_name": "Demo",
                    "last_name": "User",
                    "role": "trader",
                    "password_hash": "$2b$12$demo_password_hash_placeholder",
                    "created_at": "2025-01-01T00:00:00",
                    "is_super_admin": False
                },
                "portfolio_data": {
                    "cash": 100000.0,
                    "positions": {},
                    "watchlist": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
                    "total_value": 100000.0,
                    "daily_pnl": 0.0
                },
                "trading_history": [],
                "friends": [],
                "chat_data": {
                    "private_chats": [],
                    "group_chats": [],
                    "messages": []
                }
            }
            
            with open(self.demo_backup_file, 'w') as f:
                json.dump(demo_backup, f, indent=2)
    
    def _load_demo_session(self) -> Dict:
        """Load demo session data."""
        if os.path.exists(self.demo_session_file):
            try:
                with open(self.demo_session_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}
    
    def _save_demo_session(self, session_data: Dict):
        """Save demo session data."""
        with open(self.demo_session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def can_access_demo(self, user_session_id: str) -> Dict:
        """Check if user can access demo account."""
        session_data = self._load_demo_session()
        current_time = datetime.now()
        
        # Check if demo is currently in use
        if "current_user" in session_data:
            session_start = datetime.fromisoformat(session_data["session_start"])
            
            # Check if session has expired (5 minutes)
            if current_time - session_start > timedelta(minutes=5):
                # Reset demo account
                self._reset_demo_account()
                session_data = {}
            elif session_data["current_user"] != user_session_id:
                # Demo is in use by another user
                time_remaining = timedelta(minutes=5) - (current_time - session_start)
                minutes_remaining = int(time_remaining.total_seconds() // 60)
                
                return {
                    "success": False,
                    "message": f"Demo account is currently in use. Try again in {minutes_remaining} minutes.",
                    "time_remaining": minutes_remaining
                }
        
        # Grant access to demo
        session_data = {
            "current_user": user_session_id,
            "session_start": current_time.isoformat(),
            "last_activity": current_time.isoformat()
        }
        self._save_demo_session(session_data)
        
        return {
            "success": True,
            "message": "Demo access granted",
            "session_expires": (current_time + timedelta(minutes=5)).isoformat()
        }
    
    def update_demo_activity(self, user_session_id: str):
        """Update last activity for demo user."""
        session_data = self._load_demo_session()
        
        if session_data.get("current_user") == user_session_id:
            session_data["last_activity"] = datetime.now().isoformat()
            self._save_demo_session(session_data)
    
    def release_demo_access(self, user_session_id: str):
        """Release demo account access."""
        session_data = self._load_demo_session()
        
        if session_data.get("current_user") == user_session_id:
            # Reset demo account when user logs out
            self._reset_demo_account()
            
            # Clear session
            if os.path.exists(self.demo_session_file):
                os.remove(self.demo_session_file)
    
    def _reset_demo_account(self):
        """Reset demo account to default state."""
        try:
            # Load backup data
            with open(self.demo_backup_file, 'r') as f:
                backup_data = json.load(f)
            
            # Reset user data
            self._reset_user_data(backup_data["user_data"])
            
            # Reset portfolio data
            self._reset_portfolio_data(backup_data["portfolio_data"])
            
            # Reset positions
            self._reset_positions()
            
            # Reset trading history
            self._reset_trading_history()
            
            # Reset friends and chat data
            self._reset_social_data()
            
        except Exception as e:
            print(f"Error resetting demo account: {e}")
    
    def _reset_user_data(self, backup_user_data: Dict):
        """Reset demo user data."""
        users_file = os.path.join(self.data_dir, "users.json")
        
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r') as f:
                    users = json.load(f)
                
                # Update demo user
                if "demo" in users:
                    users["demo"].update(backup_user_data)
                    
                    with open(users_file, 'w') as f:
                        json.dump(users, f, indent=2)
            except Exception as e:
                print(f"Error resetting user data: {e}")
    
    def start_demo_session(self, user_session_id: str) -> Dict:
        """Start a demo session for a user."""
        access_result = self.can_access_demo(user_session_id)
        if access_result.get('success', False):
            self.update_demo_activity(user_session_id)
            return {"success": True, "message": "Demo session started successfully"}
        else:
            return {"success": False, "message": access_result.get('message', 'Cannot access demo')}
    
    def check_demo_reset(self) -> Dict:
        """Check when the next demo reset will occur."""
        session_data = self._load_demo_session()
        
        if 'demo_start_time' in session_data:
            demo_start = datetime.fromisoformat(session_data['demo_start_time'])
            next_reset = demo_start + timedelta(minutes=5)
            
            if datetime.now() >= next_reset:
                # Reset is due
                self._reset_demo_account()
                return {"next_reset_in": "0 minutes - Reset completed"}
            else:
                # Calculate time until next reset
                time_until_reset = next_reset - datetime.now()
                minutes_left = int(time_until_reset.total_seconds() / 60)
                seconds_left = int(time_until_reset.total_seconds() % 60)
                return {"next_reset_in": f"{minutes_left}m {seconds_left}s"}
        else:
            return {"next_reset_in": "No active demo session"}
    
    def _reset_portfolio_data(self, backup_portfolio_data: Dict):
        """Reset demo portfolio data."""
        portfolio_file = os.path.join(self.data_dir, "portfolios.json")
        
        if os.path.exists(portfolio_file):
            try:
                with open(portfolio_file, 'r') as f:
                    portfolios = json.load(f)
                
                # Reset demo portfolio with consistent format
                # Use cash_balance for consistency with other users
                if "demo_user" in portfolios:
                    portfolios["demo_user"] = {
                        "cash_balance": 100000.0,
                        "created_at": "2025-01-01T00:00:00",
                        "last_updated": datetime.now().isoformat()
                    }
                else:
                    # Create if doesn't exist
                    portfolios["demo_user"] = {
                        "cash_balance": 100000.0,
                        "created_at": "2025-01-01T00:00:00",
                        "last_updated": datetime.now().isoformat()
                    }
                
                with open(portfolio_file, 'w') as f:
                    json.dump(portfolios, f, indent=2)
            except Exception as e:
                print(f"Error resetting portfolio data: {e}")
    
    def _reset_positions(self):
        """Reset demo positions to empty."""
        positions_file = os.path.join(self.data_dir, "positions.json")
        
        if os.path.exists(positions_file):
            try:
                with open(positions_file, 'r') as f:
                    positions = json.load(f)
                
                # Remove demo positions
                if "demo_user" in positions:
                    positions["demo_user"] = {}
                    
                    with open(positions_file, 'w') as f:
                        json.dump(positions, f, indent=2)
            except Exception as e:
                print(f"Error resetting positions: {e}")
    
    def _reset_trading_history(self):
        """Reset demo trading history."""
        trades_file = os.path.join(self.data_dir, "trades.json")
        
        if os.path.exists(trades_file):
            try:
                with open(trades_file, 'r') as f:
                    trades = json.load(f)
                
                # Handle both dict and list formats
                if isinstance(trades, dict):
                    # Remove demo_user key if it exists
                    if "demo_user" in trades:
                        del trades["demo_user"]
                elif isinstance(trades, list):
                    # Remove demo trades from list
                    trades = [trade for trade in trades if trade.get("user_id") != "demo_user"]
                
                with open(trades_file, 'w') as f:
                    json.dump(trades, f, indent=2)
            except Exception as e:
                print(f"Error resetting trading history: {e}")
    
    def _reset_social_data(self):
        """Reset demo social data (friends, chats)."""
        # Reset friends
        friends_file = os.path.join(self.data_dir, "friends.json")
        if os.path.exists(friends_file):
            try:
                with open(friends_file, 'r') as f:
                    friends = json.load(f)
                
                # Remove demo from all friend relationships
                friends = [f for f in friends if f.get("user1") != "demo_user" and f.get("user2") != "demo_user"]
                
                with open(friends_file, 'w') as f:
                    json.dump(friends, f, indent=2)
            except Exception as e:
                print(f"Error resetting friends data: {e}")
        
        # Reset chats
        chats_file = os.path.join(self.data_dir, "chats.json")
        if os.path.exists(chats_file):
            try:
                with open(chats_file, 'r') as f:
                    chats = json.load(f)
                
                # Remove chats involving demo user
                filtered_chats = {}
                for chat_id, chat_data in chats.items():
                    if "demo_user" not in chat_data.get("participants", []):
                        filtered_chats[chat_id] = chat_data
                
                with open(chats_file, 'w') as f:
                    json.dump(filtered_chats, f, indent=2)
            except Exception as e:
                print(f"Error resetting chats data: {e}")
    
    def get_demo_status(self) -> Dict:
        """Get current demo account status."""
        session_data = self._load_demo_session()
        
        if not session_data:
            return {
                "in_use": False,
                "available": True
            }
        
        current_time = datetime.now()
        session_start = datetime.fromisoformat(session_data["session_start"])
        time_remaining = timedelta(minutes=5) - (current_time - session_start)
        
        if time_remaining.total_seconds() <= 0:
            return {
                "in_use": False,
                "available": True
            }
        
        return {
            "in_use": True,
            "available": False,
            "time_remaining_minutes": int(time_remaining.total_seconds() // 60),
            "current_user": session_data.get("current_user")
        }