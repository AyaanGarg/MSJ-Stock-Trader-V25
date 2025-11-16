import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import uuid

class UserManager:
    """Manages user administration and statistics."""
    
    def __init__(self):
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
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def get_user_statistics(self) -> Dict:
        """Get user statistics for admin dashboard."""
        users = self._load_users()
        
        total_users = len(users)
        active_today = 0
        new_this_month = 0
        premium_users = 0
        
        today = datetime.now().date()
        month_start = datetime.now().replace(day=1).date()
        
        for user in users.values():
            # Count premium users
            if user.get('role') in ['premium', 'trader']:
                premium_users += 1
            
            # Count users active today
            if user.get('last_login'):
                last_login_date = datetime.fromisoformat(user['last_login']).date()
                if last_login_date == today:
                    active_today += 1
            
            # Count new users this month
            if user.get('created_at'):
                created_date = datetime.fromisoformat(user['created_at']).date()
                if created_date >= month_start:
                    new_this_month += 1
        
        return {
            'total_users': total_users,
            'active_today': active_today,
            'new_this_month': new_this_month,
            'premium_users': premium_users
        }
    
    def get_all_users(self) -> pd.DataFrame:
        """Get all users as DataFrame for admin management."""
        users = self._load_users()
        
        if not users:
            return pd.DataFrame(columns=['user_id', 'username', 'email', 'role', 'account_type', 'created_at', 'last_login', 'is_active'])
        
        users_list = []
        for username, user_data in users.items():
            users_list.append({
                'user_id': user_data.get('user_id', ''),
                'username': username,
                'email': user_data.get('email', ''),
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'role': user_data.get('role', 'basic'),
                'account_type': user_data.get('account_type', 'Individual'),
                'created_at': user_data.get('created_at', ''),
                'last_login': user_data.get('last_login', 'Never'),
                'is_active': user_data.get('is_active', True),
                'failed_login_attempts': user_data.get('failed_login_attempts', 0)
            })
        
        return pd.DataFrame(users_list)
    
    def suspend_user(self, user_id: str) -> Dict:
        """Suspend a user account."""
        users = self._load_users()
        
        # Find user by ID
        for username, user_data in users.items():
            if user_data.get('user_id') == user_id:
                user_data['is_active'] = False
                user_data['suspended_at'] = datetime.now().isoformat()
                users[username] = user_data
                self._save_users(users)
                return {"success": True, "message": f"User {username} suspended successfully"}
        
        return {"success": False, "message": "User not found"}
    
    def activate_user(self, user_id: str) -> Dict:
        """Activate a suspended user account."""
        users = self._load_users()
        
        # Find user by ID
        for username, user_data in users.items():
            if user_data.get('user_id') == user_id:
                user_data['is_active'] = True
                user_data['failed_login_attempts'] = 0
                if 'suspended_at' in user_data:
                    del user_data['suspended_at']
                users[username] = user_data
                self._save_users(users)
                return {"success": True, "message": f"User {username} activated successfully"}
        
        return {"success": False, "message": "User not found"}
    
    def delete_user(self, user_id: str) -> Dict:
        """Delete a user account (use with caution)."""
        users = self._load_users()
        
        # Find and delete user by ID
        for username, user_data in users.items():
            if user_data.get('user_id') == user_id:
                del users[username]
                self._save_users(users)
                
                # In a real application, you would also need to:
                # - Delete user's portfolio data
                # - Delete user's trading history
                # - Handle any open positions
                
                return {"success": True, "message": f"User {username} deleted successfully"}
        
        return {"success": False, "message": "User not found"}
    
    def update_user_role(self, user_id: str, new_role: str) -> Dict:
        """Update user role."""
        users = self._load_users()
        
        valid_roles = ["basic", "trader", "premium", "admin"]
        if new_role not in valid_roles:
            return {"success": False, "message": f"Invalid role. Must be one of: {valid_roles}"}
        
        # Find user by ID
        for username, user_data in users.items():
            if user_data.get('user_id') == user_id:
                old_role = user_data.get('role', 'basic')
                user_data['role'] = new_role
                user_data['role_updated_at'] = datetime.now().isoformat()
                users[username] = user_data
                self._save_users(users)
                return {"success": True, "message": f"User {username} role updated from {old_role} to {new_role}"}
        
        return {"success": False, "message": "User not found"}
    
    def get_user_activity(self, days: int = 30) -> pd.DataFrame:
        """Get user activity statistics."""
        users = self._load_users()
        
        # Create date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = [start_date + timedelta(days=i) for i in range(days)]
        
        activity_data = []
        
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            daily_logins = 0
            daily_registrations = 0
            
            for user in users.values():
                # Count logins
                if user.get('last_login'):
                    login_date = datetime.fromisoformat(user['last_login']).date()
                    if login_date == date.date():
                        daily_logins += 1
                
                # Count registrations
                if user.get('created_at'):
                    created_date = datetime.fromisoformat(user['created_at']).date()
                    if created_date == date.date():
                        daily_registrations += 1
            
            activity_data.append({
                'date': date_str,
                'logins': daily_logins,
                'registrations': daily_registrations
            })
        
        return pd.DataFrame(activity_data)
    
    def get_role_distribution(self) -> Dict:
        """Get distribution of user roles."""
        users = self._load_users()
        
        role_counts = {}
        
        for user in users.values():
            role = user.get('role', 'basic')
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return role_counts
    
    def search_users(self, query: str) -> pd.DataFrame:
        """Search users by username, email, or name."""
        users = self._load_users()
        
        matching_users = []
        query_lower = query.lower()
        
        for username, user_data in users.items():
            # Search in username, email, first name, last name
            searchable_fields = [
                username.lower(),
                user_data.get('email', '').lower(),
                user_data.get('first_name', '').lower(),
                user_data.get('last_name', '').lower()
            ]
            
            if any(query_lower in field for field in searchable_fields):
                matching_users.append({
                    'user_id': user_data.get('user_id', ''),
                    'username': username,
                    'email': user_data.get('email', ''),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'role': user_data.get('role', 'basic'),
                    'account_type': user_data.get('account_type', 'Individual'),
                    'is_active': user_data.get('is_active', True)
                })
        
        return pd.DataFrame(matching_users)
    
    def export_users_csv(self, filepath: str = "data/users_export.csv") -> Dict:
        """Export users data to CSV."""
        try:
            users_df = self.get_all_users()
            users_df.to_csv(filepath, index=False)
            return {"success": True, "message": f"Users exported to {filepath}"}
        except Exception as e:
            return {"success": False, "message": f"Export failed: {str(e)}"}
    
    def get_user_details(self, user_id: str) -> Dict:
        """Get detailed information about a specific user."""
        users = self._load_users()
        
        for username, user_data in users.items():
            if user_data.get('user_id') == user_id:
                return {
                    "success": True,
                    "user_data": user_data,
                    "username": username
                }
        
        return {"success": False, "message": "User not found"}