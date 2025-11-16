"""
User Blocking System for Chat and Social Features
Allows users to block others from contacting or disturbing them.
"""

import json
import os
from typing import Dict, List, Set
from datetime import datetime

class UserBlockingSystem:
    """Manages user blocking functionality for chat and social features."""
    
    def __init__(self):
        self.data_dir = "data"
        self.blocked_users_file = os.path.join(self.data_dir, "blocked_users.json")
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize data files if they don't exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.blocked_users_file):
            with open(self.blocked_users_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def _load_blocked_users(self) -> Dict:
        """Load blocked users data from file."""
        try:
            with open(self.blocked_users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_blocked_users(self, data: Dict):
        """Save blocked users data to file."""
        with open(self.blocked_users_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def block_user(self, blocker_username: str, blocked_username: str) -> Dict:
        """Block a user from contacting the blocker."""
        if blocker_username == blocked_username:
            return {"success": False, "message": "You cannot block yourself"}
        
        blocked_data = self._load_blocked_users()
        
        if blocker_username not in blocked_data:
            blocked_data[blocker_username] = []
        
        if blocked_username not in blocked_data[blocker_username]:
            blocked_data[blocker_username].append({
                "blocked_user": blocked_username,
                "blocked_at": datetime.now().isoformat(),
                "reason": "User blocked via chat system"
            })
            
            self._save_blocked_users(blocked_data)
            
            # Send email notification about blocking action
            self._send_block_notification_email(blocker_username, blocked_username, "blocked")
            
            return {"success": True, "message": f"Successfully blocked {blocked_username}"}
        else:
            return {"success": False, "message": f"{blocked_username} is already blocked"}
    
    def unblock_user(self, blocker_username: str, blocked_username: str) -> Dict:
        """Unblock a previously blocked user."""
        blocked_data = self._load_blocked_users()
        
        if blocker_username not in blocked_data:
            return {"success": False, "message": f"{blocked_username} is not blocked"}
        
        # Remove from blocked list
        blocked_data[blocker_username] = [
            block for block in blocked_data[blocker_username] 
            if block["blocked_user"] != blocked_username
        ]
        
        # Clean up empty lists
        if not blocked_data[blocker_username]:
            del blocked_data[blocker_username]
        
        self._save_blocked_users(blocked_data)
        
        # Send email notification about unblocking action
        self._send_block_notification_email(blocker_username, blocked_username, "unblocked")
        
        return {"success": True, "message": f"Successfully unblocked {blocked_username}"}
    
    def is_user_blocked(self, blocker_username: str, potential_blocked_username: str) -> bool:
        """Check if a user is blocked by another user."""
        blocked_data = self._load_blocked_users()
        
        if blocker_username not in blocked_data:
            return False
        
        blocked_users = [block["blocked_user"] for block in blocked_data[blocker_username]]
        return potential_blocked_username in blocked_users
    
    def get_blocked_users(self, username: str) -> List[Dict]:
        """Get list of users blocked by a specific user."""
        blocked_data = self._load_blocked_users()
        
        if username not in blocked_data:
            return []
        
        return blocked_data[username]
    
    def get_users_who_blocked(self, username: str) -> List[str]:
        """Get list of users who have blocked this user."""
        blocked_data = self._load_blocked_users()
        blockers = []
        
        for blocker, blocked_list in blocked_data.items():
            blocked_users = [block["blocked_user"] for block in blocked_list]
            if username in blocked_users:
                blockers.append(blocker)
        
        return blockers
    
    def can_users_interact(self, user1: str, user2: str) -> bool:
        """Check if two users can interact (neither has blocked the other)."""
        return not (self.is_user_blocked(user1, user2) or self.is_user_blocked(user2, user1))
    
    def filter_blocked_users_from_list(self, requesting_user: str, user_list: List[str]) -> List[str]:
        """Filter out blocked users from a list."""
        return [user for user in user_list if self.can_users_interact(requesting_user, user)]
    
    def _send_block_notification_email(self, blocker_username: str, blocked_username: str, action: str):
        """Send email notification for blocking/unblocking actions."""
        try:
            from modules.email_service import EmailService
            from modules.auth_manager import AuthManager
            
            email_service = EmailService()
            auth_manager = AuthManager()
            
            # Get blocker's email for confirmation
            blocker_data = auth_manager.get_user_by_username(blocker_username)
            if blocker_data and blocker_data.get('email'):
                blocker_name = f"{blocker_data.get('first_name', '')} {blocker_data.get('last_name', '')}".strip()
                if not blocker_name:
                    blocker_name = blocker_username
                
                title = f"User {action.title()}"
                message = f"You have {action} user '{blocked_username}' from contacting you in chats and social features."
                
                result = email_service.send_team_notification_email(
                    blocker_data['email'],
                    blocker_name,
                    title,
                    message
                )
                
                if not result['success']:
                    print(f"Failed to send blocking notification email: {result['message']}")
        except Exception as e:
            print(f"Email service error in blocking system: {str(e)}")
    
    def get_block_statistics(self) -> Dict:
        """Get statistics about blocking activity."""
        blocked_data = self._load_blocked_users()
        
        total_blockers = len(blocked_data)
        total_blocks = sum(len(blocks) for blocks in blocked_data.values())
        
        return {
            "total_users_who_blocked": total_blockers,
            "total_blocks": total_blocks,
            "average_blocks_per_user": total_blocks / max(total_blockers, 1)
        }