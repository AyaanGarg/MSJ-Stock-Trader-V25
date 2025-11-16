import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
import re
from modules.user_blocking_system import UserBlockingSystem

class ChatManager:
    """Manages chat functionality including private messages, group chats, and public channels."""
    
    def __init__(self):
        self.data_dir = "data"
        self.chats_file = "data/chats.json"
        self.messages_file = "data/messages.json"
        self.notifications_file = "data/notifications.json"
        self.public_channels_file = "data/public_channels.json"
        self.timeouts_file = "data/chat_timeouts.json"
        self.rate_limits_file = "data/rate_limits.json"
        self.blocking_system = UserBlockingSystem()
        self._ensure_data_directory()
        self._initialize_data()
        self._initialize_bad_words()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _initialize_data(self):
        """Initialize chat data files."""
        if not os.path.exists(self.chats_file):
            self._save_json(self.chats_file, {})
        
        if not os.path.exists(self.messages_file):
            self._save_json(self.messages_file, {})
        
        if not os.path.exists(self.notifications_file):
            self._save_json(self.notifications_file, {})
        
        if not os.path.exists(self.public_channels_file):
            # Initialize with a general trading channel
            default_channels = {
                "general": {
                    "id": "general",
                    "name": "General Trading",
                    "description": "General discussion about trading and market news",
                    "created_at": datetime.now().isoformat(),
                    "created_by": "system",
                    "type": "public"
                },
                "market-alerts": {
                    "id": "market-alerts",
                    "name": "Market Alerts",
                    "description": "Share market insights and trading alerts",
                    "created_at": datetime.now().isoformat(),
                    "created_by": "system",
                    "type": "public"
                },
                "portfolio-showcase": {
                    "id": "portfolio-showcase",
                    "name": "Portfolio Showcase",
                    "description": "Share your portfolio performance and achievements",
                    "created_at": datetime.now().isoformat(),
                    "created_by": "system",
                    "type": "public"
                }
            }
            self._save_json(self.public_channels_file, default_channels)
        
        # Initialize timeouts and rate limits
        if not os.path.exists(self.timeouts_file):
            self._save_json(self.timeouts_file, {})
        
        if not os.path.exists(self.rate_limits_file):
            self._save_json(self.rate_limits_file, {})
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON data from file."""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, filename: str, data: Dict):
        """Save JSON data to file."""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _cleanup_old_messages(self):
        """Remove messages older than 24 hours."""
        messages = self._load_json(self.messages_file)
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=24)
        
        # Filter out messages older than 24 hours
        cleaned_messages = {}
        for chat_id, chat_messages in messages.items():
            if isinstance(chat_messages, list):
                cleaned_messages[chat_id] = [
                    msg for msg in chat_messages
                    if datetime.fromisoformat(msg['timestamp']) > cutoff_time
                ]
            else:
                cleaned_messages[chat_id] = chat_messages
        
        self._save_json(self.messages_file, cleaned_messages)
        
        # Also clean up old notifications
        notifications = self._load_json(self.notifications_file)
        for user_id, user_notifications in notifications.items():
            if isinstance(user_notifications, list):
                notifications[user_id] = [
                    notif for notif in user_notifications
                    if datetime.fromisoformat(notif['timestamp']) > cutoff_time
                ]
        
        self._save_json(self.notifications_file, notifications)
    
    def _initialize_bad_words(self):
        """Initialize bad word filter."""
        self.bad_words = [
            # Common profanity (partial list for demonstration)
            'damn', 'hell', 'crap', 'stupid', 'idiot', 'moron', 'dumb',
            'hate', 'kill', 'die', 'death', 'murder', 'violence',
            'scam', 'fraud', 'cheat', 'steal', 'illegal', 'drug',
            # Financial inappropriate terms
            'pump', 'dump', 'manipulation', 'insider', 'ponzi', 'pyramid'
        ]
        
        # Create regex pattern for bad words
        self.bad_word_pattern = re.compile(
            r'\b(?:' + '|'.join(re.escape(word) for word in self.bad_words) + r')\b',
            re.IGNORECASE
        )
    
    def _check_bad_words(self, text: str) -> bool:
        """Check if text contains bad words."""
        return bool(self.bad_word_pattern.search(text))
    
    def _is_user_admin(self, user_id: str) -> bool:
        """Check if user is admin or super admin."""
        try:
            from modules.auth_manager import AuthManager
            auth_manager = AuthManager()
            users = auth_manager._load_data(auth_manager.users_file)
            
            if user_id in users:
                user_role = users[user_id].get('role', 'basic')
                return user_role in ['admin', 'super_admin'] or users[user_id].get('is_super_admin', False)
            
            return False
        except:
            return False
    
    def _is_user_timed_out(self, user_id: str) -> bool:
        """Check if user is currently timed out."""
        timeouts = self._load_json(self.timeouts_file)
        
        if user_id not in timeouts:
            return False
        
        timeout_until = datetime.fromisoformat(timeouts[user_id]['timeout_until'])
        return datetime.now() < timeout_until
    
    def _timeout_user(self, user_id: str, reason: str = "Bad language"):
        """Timeout user for 24 hours."""
        timeouts = self._load_json(self.timeouts_file)
        
        timeout_until = datetime.now() + timedelta(hours=24)
        timeouts[user_id] = {
            'timeout_until': timeout_until.isoformat(),
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_json(self.timeouts_file, timeouts)
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is rate limited (30 seconds between messages)."""
        if self._is_user_admin(user_id):
            return False  # Admins bypass rate limits
        
        rate_limits = self._load_json(self.rate_limits_file)
        
        if user_id not in rate_limits:
            return False
        
        last_message_time = datetime.fromisoformat(rate_limits[user_id]['last_message'])
        time_since_last = datetime.now() - last_message_time
        
        return time_since_last.total_seconds() < 30
    
    def _update_rate_limit(self, user_id: str):
        """Update user's last message time for rate limiting."""
        rate_limits = self._load_json(self.rate_limits_file)
        
        rate_limits[user_id] = {
            'last_message': datetime.now().isoformat()
        }
        
        self._save_json(self.rate_limits_file, rate_limits)
    
    def get_timeout_info(self, user_id: str) -> Optional[Dict]:
        """Get timeout information for user."""
        timeouts = self._load_json(self.timeouts_file)
        
        if user_id not in timeouts:
            return None
        
        timeout_until = datetime.fromisoformat(timeouts[user_id]['timeout_until'])
        if datetime.now() >= timeout_until:
            # Timeout expired, remove it
            del timeouts[user_id]
            self._save_json(self.timeouts_file, timeouts)
            return None
        
        time_remaining = timeout_until - datetime.now()
        hours_remaining = int(time_remaining.total_seconds() // 3600)
        minutes_remaining = int((time_remaining.total_seconds() % 3600) // 60)
        
        return {
            'timeout_until': timeout_until.isoformat(),
            'reason': timeouts[user_id]['reason'],
            'hours_remaining': hours_remaining,
            'minutes_remaining': minutes_remaining
        }
    
    def create_private_chat(self, user1_id: str, user2_id: str) -> Dict:
        """Create or get existing private chat between two users."""
        chats = self._load_json(self.chats_file)
        
        # Generate consistent chat ID
        sorted_ids = sorted([user1_id, user2_id])
        chat_id = f"private_{sorted_ids[0]}_{sorted_ids[1]}"
        
        if chat_id not in chats:
            chats[chat_id] = {
                "id": chat_id,
                "type": "private",
                "participants": [user1_id, user2_id],
                "created_at": datetime.now().isoformat(),
                "last_message_at": None,
                "name": None  # Private chats don't have names
            }
            self._save_json(self.chats_file, chats)
        
        return {"success": True, "chat_id": chat_id}
    
    def create_group_chat(self, creator_id: str, participants: List[str], name: str, is_public: bool = False) -> Dict:
        """Create a new group chat or team."""
        chats = self._load_json(self.chats_file)
        
        chat_id = f"group_{uuid.uuid4().hex[:8]}"
        
        # Include creator in participants
        all_participants = list(set([creator_id] + participants))
        
        chats[chat_id] = {
            "id": chat_id,
            "type": "group",
            "name": name,
            "participants": all_participants,
            "creator": creator_id,
            "created_at": datetime.now().isoformat(),
            "last_message_at": None,
            "is_public": is_public,
            "description": f"{'Public' if is_public else 'Private'} group chat: {name}"
        }
        
        self._save_json(self.chats_file, chats)
        return {"success": True, "chat_id": chat_id}
    
    def create_team(self, creator_id: str, team_name: str, is_public: bool = False, description: str = "") -> Dict:
        """Create a new team with chat functionality."""
        teams_file = "data/teams.json"
        teams = self._load_json(teams_file)
        
        team_id = f"team_{uuid.uuid4().hex[:8]}"
        
        teams[team_id] = {
            "id": team_id,
            "name": team_name,
            "description": description,
            "creator": creator_id,
            "captain": creator_id,
            "members": [creator_id],
            "is_public": is_public,
            "created_at": datetime.now().isoformat(),
            "max_members": 10,
            "join_requests": [] if is_public else None  # Only track requests for private teams
        }
        
        self._save_json(teams_file, teams)
        
        # Create associated group chat for the team
        chat_result = self.create_group_chat(
            creator_id, 
            [], 
            f"Team: {team_name}", 
            is_public
        )
        
        if chat_result["success"]:
            teams[team_id]["chat_id"] = chat_result["chat_id"]
            self._save_json(teams_file, teams)
        
        return {"success": True, "team_id": team_id, "chat_id": chat_result.get("chat_id")}
    
    def get_all_public_groups(self) -> List[Dict]:
        """Get all public groups and teams that anyone can join."""
        chats = self._load_json(self.chats_file)
        teams_file = "data/teams.json"
        teams = self._load_json(teams_file)
        
        public_groups = []
        
        # Get public group chats
        for chat_id, chat in chats.items():
            if chat.get("type") == "group" and chat.get("is_public", False):
                public_groups.append({
                    "id": chat_id,
                    "name": chat["name"],
                    "type": "group_chat",
                    "description": chat.get("description", "Public group chat"),
                    "members": len(chat["participants"]),
                    "created_at": chat["created_at"]
                })
        
        # Get public teams
        for team_id, team in teams.items():
            if team.get("is_public", False):
                public_groups.append({
                    "id": team_id,
                    "name": team["name"],
                    "type": "team",
                    "description": team.get("description", "Public team"),
                    "members": len(team["members"]),
                    "created_at": team["created_at"],
                    "chat_id": team.get("chat_id")
                })
        
        # Sort by creation date (newest first)
        public_groups.sort(key=lambda x: x["created_at"], reverse=True)
        return public_groups
    
    def join_public_group(self, user_id: str, group_id: str) -> Dict:
        """Join a public group or team."""
        if group_id.startswith("team_"):
            return self._join_public_team(user_id, group_id)
        else:
            return self._join_public_chat(user_id, group_id)
    
    def _join_public_team(self, user_id: str, team_id: str) -> Dict:
        """Join a public team."""
        teams_file = "data/teams.json"
        teams = self._load_json(teams_file)
        
        if team_id not in teams:
            return {"success": False, "error": "Team not found"}
        
        team = teams[team_id]
        
        if not team.get("is_public", False):
            return {"success": False, "error": "Team is private"}
        
        if user_id in team["members"]:
            return {"success": False, "error": "Already a member"}
        
        if len(team["members"]) >= team.get("max_members", 10):
            return {"success": False, "error": "Team is full"}
        
        # Add to team
        team["members"].append(user_id)
        teams[team_id] = team
        self._save_json(teams_file, teams)
        
        # Add to team chat if exists
        if team.get("chat_id"):
            chats = self._load_json(self.chats_file)
            if team["chat_id"] in chats:
                if user_id not in chats[team["chat_id"]]["participants"]:
                    chats[team["chat_id"]]["participants"].append(user_id)
                    self._save_json(self.chats_file, chats)
        
        return {"success": True, "message": f"Joined team: {team['name']}"}
    
    def _join_public_chat(self, user_id: str, chat_id: str) -> Dict:
        """Join a public group chat."""
        chats = self._load_json(self.chats_file)
        
        if chat_id not in chats:
            return {"success": False, "error": "Chat not found"}
        
        chat = chats[chat_id]
        
        if not chat.get("is_public", False):
            return {"success": False, "error": "Chat is private"}
        
        if user_id in chat["participants"]:
            return {"success": False, "error": "Already a member"}
        
        # Add to chat
        chat["participants"].append(user_id)
        chats[chat_id] = chat
        self._save_json(self.chats_file, chats)
        
        return {"success": True, "message": f"Joined chat: {chat['name']}"}
    
    def send_message_to_channel(self, channel_id: str, sender_id: str, content: str) -> Dict:
        """Send a message to a public channel."""
        return self.send_message(f"public_{channel_id}", sender_id, content)
    
    def send_message_to_group(self, group_id: str, sender_id: str, content: str) -> Dict:
        """Send a message to a group chat."""
        return self.send_message(group_id, sender_id, content)
    
    def get_channel_messages(self, channel_id: str, limit: int = 50) -> List[Dict]:
        """Get messages from a public channel."""
        return self.get_chat_messages(f"public_{channel_id}", limit)
    
    def get_group_messages(self, group_id: str, limit: int = 50) -> List[Dict]:
        """Get messages from a group chat."""
        return self.get_chat_messages(group_id, limit)
    
    def get_private_messages(self, user_id: str, chat_id: str, limit: int = 50) -> List[Dict]:
        """Get messages from a private chat."""
        return self.get_chat_messages(chat_id, limit)
    
    def get_chat_participants_info(self, chat_id: str) -> List[Dict]:
        """Get participant information for a chat."""
        chats = self._load_json(self.chats_file)
        
        if chat_id not in chats:
            return []
        
        participants = chats[chat_id]["participants"]
        
        # Get user info for participants
        from modules.auth_manager import AuthManager
        auth_manager = AuthManager()
        users = auth_manager._load_data(auth_manager.users_file)
        
        participant_info = []
        for participant_id in participants:
            if participant_id in users:
                user_data = users[participant_id]
                participant_info.append({
                    'user_id': participant_id,
                    'username': user_data.get('username', 'Unknown'),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', '')
                })
        
        return participant_info
    
    def add_reaction(self, message_id: str, user_id: str, emoji: str) -> Dict:
        """Add a reaction to a message."""
        messages = self._load_json(self.messages_file)
        
        # Find the message across all chats
        for chat_id, chat_messages in messages.items():
            for message in chat_messages:
                if message['id'] == message_id:
                    if 'reactions' not in message:
                        message['reactions'] = {}
                    
                    if emoji not in message['reactions']:
                        message['reactions'][emoji] = []
                    
                    if user_id not in message['reactions'][emoji]:
                        message['reactions'][emoji].append(user_id)
                    
                    self._save_json(self.messages_file, messages)
                    return {"success": True}
        
        return {"success": False, "error": "Message not found"}
    
    def send_message(self, chat_id: str, sender_id: str, content: str, message_type: str = "text", 
                    portfolio_data: Optional[Dict] = None) -> Dict:
        """Send a message to a chat."""
        # Check if user is timed out
        if self._is_user_timed_out(sender_id):
            timeout_info = self.get_timeout_info(sender_id)
            return {
                "success": False, 
                "error": f"You are timed out for {timeout_info['hours_remaining']}h {timeout_info['minutes_remaining']}m for: {timeout_info['reason']}"
            }
        
        # Check rate limit (30 seconds between messages for non-admins)
        if self._check_rate_limit(sender_id):
            return {
                "success": False,
                "error": "Please wait 30 seconds between messages"
            }
        
        # Check for bad words
        if self._check_bad_words(content):
            self._timeout_user(sender_id, "Inappropriate language")
            return {
                "success": False,
                "error": "Message blocked for inappropriate content. You have been timed out for 24 hours."
            }
        
        # Clean up old messages before sending new ones
        self._cleanup_old_messages()
        
        # Update rate limit
        self._update_rate_limit(sender_id)
        
        messages = self._load_json(self.messages_file)
        chats = self._load_json(self.chats_file)
        
        # Validate chat exists and user has access
        if chat_id not in chats and not chat_id.startswith("public_"):
            return {"success": False, "error": "Chat not found"}
        
        if not chat_id.startswith("public_"):
            chat = chats[chat_id]
            if sender_id not in chat["participants"]:
                return {"success": False, "error": "Access denied"}
        
        # Create message
        message_id = uuid.uuid4().hex
        message = {
            "id": message_id,
            "chat_id": chat_id,
            "sender_id": sender_id,
            "content": content,
            "message_type": message_type,
            "portfolio_data": portfolio_data,
            "timestamp": datetime.now().isoformat(),
            "edited": False,
            "reactions": {}
        }
        
        if chat_id not in messages:
            messages[chat_id] = []
        
        messages[chat_id].append(message)
        self._save_json(self.messages_file, messages)
        
        # Update last message time
        if not chat_id.startswith("public_"):
            chats[chat_id]["last_message_at"] = datetime.now().isoformat()
            self._save_json(self.chats_file, chats)
        
        # Create notifications for other participants
        self._create_message_notifications(chat_id, sender_id, content, message_type)
        
        return {"success": True, "message_id": message_id}
    
    def send_public_message(self, channel_id: str, sender_id: str, content: str, 
                           message_type: str = "text", portfolio_data: Optional[Dict] = None) -> Dict:
        """Send a message to a public channel."""
        return self.send_message(f"public_{channel_id}", sender_id, content, message_type, portfolio_data)
    
    def get_chat_messages(self, chat_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get messages from a chat."""
        # Clean up old messages when retrieving
        self._cleanup_old_messages()
        
        messages = self._load_json(self.messages_file)
        
        if chat_id not in messages:
            return []
        
        chat_messages = messages[chat_id]
        # Sort by timestamp (newest first)
        chat_messages.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        start = offset
        end = offset + limit
        
        return chat_messages[start:end]
    
    def get_user_chats(self, user_id: str) -> List[Dict]:
        """Get all chats for a user."""
        chats = self._load_json(self.chats_file)
        user_chats = []
        
        for chat_id, chat in chats.items():
            if user_id in chat["participants"]:
                # Add last message preview
                messages = self.get_chat_messages(chat_id, limit=1)
                chat["last_message"] = messages[0] if messages else None
                user_chats.append(chat)
        
        # Sort by last message time
        user_chats.sort(key=lambda x: x.get("last_message_at", ""), reverse=True)
        return user_chats
    
    def get_public_channels(self) -> List[Dict]:
        """Get all public channels."""
        channels = self._load_json(self.public_channels_file)
        return list(channels.values())
    
    def get_user_notifications(self, user_id: str) -> List[Dict]:
        """Get unread notifications for a user."""
        notifications = self._load_json(self.notifications_file)
        
        if user_id not in notifications:
            return []
        
        user_notifications = notifications[user_id]
        # Filter unread notifications
        unread = [n for n in user_notifications if not n.get("read", False)]
        
        # Sort by timestamp (newest first)
        unread.sort(key=lambda x: x["timestamp"], reverse=True)
        return unread
    
    def mark_notifications_read(self, user_id: str, notification_ids: List[str] = None) -> Dict:
        """Mark notifications as read."""
        notifications = self._load_json(self.notifications_file)
        
        if user_id not in notifications:
            return {"success": True}
        
        user_notifications = notifications[user_id]
        
        for notification in user_notifications:
            if notification_ids is None or notification["id"] in notification_ids:
                notification["read"] = True
                notification["read_at"] = datetime.now().isoformat()
        
        self._save_json(self.notifications_file, notifications)
        return {"success": True}
    
    def _create_message_notifications(self, chat_id: str, sender_id: str, content: str, message_type: str):
        """Create notifications for new messages."""
        notifications = self._load_json(self.notifications_file)
        chats = self._load_json(self.chats_file)
        
        # Get participants to notify
        participants_to_notify = []
        
        if chat_id.startswith("public_"):
            # For public channels, we don't create notifications to avoid spam
            # Users can check channels manually
            return
        
        if chat_id in chats:
            participants_to_notify = [p for p in chats[chat_id]["participants"] if p != sender_id]
        
        # Create notification for each participant
        for participant_id in participants_to_notify:
            if participant_id not in notifications:
                notifications[participant_id] = []
            
            notification = {
                "id": uuid.uuid4().hex,
                "type": "new_message",
                "chat_id": chat_id,
                "sender_id": sender_id,
                "content_preview": content[:50] + "..." if len(content) > 50 else content,
                "message_type": message_type,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            
            notifications[participant_id].append(notification)
        
        self._save_json(self.notifications_file, notifications)
    
    def add_reaction(self, message_id: str, user_id: str, emoji: str) -> Dict:
        """Add reaction to a message."""
        messages = self._load_json(self.messages_file)
        
        # Find message
        for chat_id, chat_messages in messages.items():
            for message in chat_messages:
                if message["id"] == message_id:
                    if "reactions" not in message:
                        message["reactions"] = {}
                    
                    if emoji not in message["reactions"]:
                        message["reactions"][emoji] = []
                    
                    if user_id not in message["reactions"][emoji]:
                        message["reactions"][emoji].append(user_id)
                    
                    self._save_json(self.messages_file, messages)
                    return {"success": True}
        
        return {"success": False, "error": "Message not found"}
    
    def create_portfolio_share_message(self, user_id: str, portfolio_data: Dict) -> Dict:
        """Create a formatted portfolio share message."""
        return {
            "type": "portfolio_share",
            "user_id": user_id,
            "portfolio_value": portfolio_data.get("total_value", 0),
            "daily_change": portfolio_data.get("daily_change", 0),
            "daily_change_percent": portfolio_data.get("daily_change_percent", 0),
            "top_positions": portfolio_data.get("top_positions", []),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_chat_participants_info(self, chat_id: str) -> List[Dict]:
        """Get information about chat participants."""
        chats = self._load_json(self.chats_file)
        
        if chat_id not in chats:
            return []
        
        # This would integrate with user management to get user details
        from modules.user_management import UserManager
        user_manager = UserManager()
        
        participants = []
        for participant_id in chats[chat_id]["participants"]:
            user_info = user_manager.get_user_info(participant_id)
            if user_info:
                participants.append({
                    "user_id": participant_id,
                    "username": user_info.get("username", "Unknown"),
                    "first_name": user_info.get("first_name", ""),
                    "last_name": user_info.get("last_name", "")
                })
        
        return participants
    
    def search_messages(self, user_id: str, query: str) -> List[Dict]:
        """Search messages across all user's chats."""
        messages = self._load_json(self.messages_file)
        chats = self._load_json(self.chats_file)
        
        results = []
        query_lower = query.lower()
        
        # Search through all chats the user has access to
        for chat_id, chat_messages in messages.items():
            # Check if user has access to this chat
            if chat_id.startswith("public_"):
                # All users can access public channels
                has_access = True
            elif chat_id in chats and user_id in chats[chat_id]["participants"]:
                # User is participant in private/group chat
                has_access = True
            else:
                has_access = False
            
            if has_access:
                for message in chat_messages:
                    if query_lower in message.get("content", "").lower():
                        results.append({
                            "chat_id": chat_id,
                            "message_id": message["id"],
                            "content": message["content"],
                            "sender_id": message["sender_id"],
                            "timestamp": message["timestamp"]
                        })
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results
    
    def get_channel_messages(self, channel_id: str, limit: int = 30) -> List[Dict]:
        """Get messages from a public channel."""
        return self.get_chat_messages(f"public_{channel_id}", limit)
    
    def get_group_messages(self, group_id: str, limit: int = 30) -> List[Dict]:
        """Get messages from a group chat."""
        return self.get_chat_messages(f"group_{group_id}", limit)
    
    def get_private_messages(self, user1_id: str, user2_username: str, limit: int = 30) -> List[Dict]:
        """Get private messages between two users."""
        # For private messages, we use a consistent chat_id format
        return self.get_chat_messages(user2_username, limit)
    
    def send_message_to_channel(self, channel_id: str, sender_id: str, content: str) -> Dict:
        """Send message to a public channel."""
        return self.send_message(f"public_{channel_id}", sender_id, content)
    
    def send_message_to_group(self, group_id: str, sender_id: str, content: str) -> Dict:
        """Send message to a group chat."""
        return self.send_message(f"group_{group_id}", sender_id, content)
    
    def send_private_message(self, sender_id: str, target_username: str, content: str) -> Dict:
        """Send private message to another user."""
        return self.send_message(target_username, sender_id, content)