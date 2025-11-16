import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class EnhancedTeamManager:
    """Enhanced team management with invitations, public/private teams, and team creator powers."""
    
    def __init__(self):
        self.data_dir = "data"
        self.teams_file = os.path.join(self.data_dir, "enhanced_teams.json")
        self.invitations_file = os.path.join(self.data_dir, "team_invitations.json")
        self.notifications_file = os.path.join(self.data_dir, "team_notifications.json")
        self._ensure_data_directory()
        self._initialize_files()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _initialize_files(self):
        """Initialize all team-related files."""
        files_and_defaults = {
            self.teams_file: {},
            self.invitations_file: [],
            self.notifications_file: []
        }
        
        for file_path, default_data in files_and_defaults.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
    
    def _load_data(self, file_path: str):
        """Load data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if file_path == self.teams_file else []
    
    def _save_data(self, file_path: str, data):
        """Save data to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_team(self, team_name: str, creator_username: str, description: str = "", 
                   is_public: bool = True) -> Dict:
        """Create a new team with public/private visibility."""
        teams = self._load_data(self.teams_file)
        
        # Check if team name already exists
        for team_id, team_data in teams.items():
            if team_data["name"].lower() == team_name.lower():
                return {"success": False, "message": "Team name already exists"}
        
        # Check if user is already in a team
        for team_id, team_data in teams.items():
            if creator_username in team_data.get("members", []):
                return {"success": False, "message": "You're already in a team. Leave your current team first."}
        
        team_id = str(uuid.uuid4())
        team_data = {
            "id": team_id,
            "name": team_name,
            "description": description,
            "creator": creator_username,
            "captain": creator_username,
            "members": [creator_username],
            "is_public": is_public,
            "created_at": datetime.now().isoformat(),
            "total_value": 0.0,
            "competitions_won": 0,
            "badges": [],
            "is_active": True,
            "max_members": 25
        }
        
        teams[team_id] = team_data
        self._save_data(self.teams_file, teams)
        
        visibility = "public" if is_public else "private"
        return {
            "success": True, 
            "message": f"Team '{team_name}' created successfully as {visibility} team!",
            "team_id": team_id
        }
    
    def send_team_invitation(self, team_id: str, inviter_username: str, invitee_username: str) -> Dict:
        """Send a team invitation to a user."""
        teams = self._load_data(self.teams_file)
        invitations = self._load_data(self.invitations_file)
        
        if team_id not in teams:
            return {"success": False, "message": "Team not found"}
        
        team = teams[team_id]
        
        # Check if inviter has permission (creator or captain)
        if inviter_username not in [team["creator"], team["captain"]]:
            return {"success": False, "message": "Only team creator or captain can send invitations"}
        
        # Check if team is full
        if len(team["members"]) >= team["max_members"]:
            return {"success": False, "message": "Team is full (maximum 25 members)"}
        
        # Check if user is already in any team
        for tid, tdata in teams.items():
            if invitee_username in tdata.get("members", []):
                return {"success": False, "message": f"{invitee_username} is already in a team"}
        
        # Check if invitation already exists
        for invitation in invitations:
            if (invitation["team_id"] == team_id and 
                invitation["invitee_username"] == invitee_username and 
                invitation["status"] == "pending"):
                return {"success": False, "message": "Invitation already sent to this user"}
        
        # Create invitation
        invitation = {
            "id": str(uuid.uuid4()),
            "team_id": team_id,
            "team_name": team["name"],
            "inviter_username": inviter_username,
            "invitee_username": invitee_username,
            "message": f"You've been invited to join team '{team['name']}'",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        invitations.append(invitation)
        self._save_data(self.invitations_file, invitations)
        
        # Create notification
        self._create_notification(
            invitee_username,
            f"Team Invitation: You've been invited to join '{team['name']}'",
            f"Team captain {inviter_username} has invited you to join their team.",
            "team_invitation",
            {"invitation_id": invitation["id"], "team_id": team_id}
        )
        
        # Send email notification for invitation
        self._send_invitation_email(invitee_username, team['name'], inviter_username, invitation["id"])
        
        # Send email for all new notifications
        self._send_team_notification_email(
            invitee_username,
            f"Team Invitation: You've been invited to join '{team['name']}'",
            f"Team captain {inviter_username} has invited you to join their team."
        )
        
        return {"success": True, "message": f"Invitation sent to {invitee_username}"}
    
    def respond_to_invitation(self, invitation_id: str, username: str, accept: bool) -> Dict:
        """Accept or decline a team invitation."""
        invitations = self._load_data(self.invitations_file)
        teams = self._load_data(self.teams_file)
        
        # Find the invitation
        invitation = None
        invitation_index = None
        for i, inv in enumerate(invitations):
            if inv["id"] == invitation_id and inv["invitee_username"] == username:
                invitation = inv
                invitation_index = i
                break
        
        if not invitation:
            return {"success": False, "message": "Invitation not found"}
        
        if invitation["status"] != "pending":
            return {"success": False, "message": "Invitation has already been responded to"}
        
        # Check if invitation has expired
        expires_at = datetime.fromisoformat(invitation["expires_at"])
        if datetime.now() > expires_at:
            invitation["status"] = "expired"
            invitations[invitation_index] = invitation
            self._save_data(self.invitations_file, invitations)
            return {"success": False, "message": "Invitation has expired"}
        
        if accept:
            # Check if user is already in a team
            for team_id, team_data in teams.items():
                if username in team_data.get("members", []):
                    return {"success": False, "message": "You're already in a team"}
            
            # Add user to team
            team_id = invitation["team_id"]
            if team_id in teams:
                team = teams[team_id]
                
                if len(team["members"]) >= team["max_members"]:
                    return {"success": False, "message": "Team is now full"}
                
                team["members"].append(username)
                teams[team_id] = team
                self._save_data(self.teams_file, teams)
                
                invitation["status"] = "accepted"
                response_message = f"Successfully joined team '{team['name']}'"
            else:
                invitation["status"] = "expired"
                response_message = "Team no longer exists"
        else:
            invitation["status"] = "declined"
            response_message = f"Declined invitation to join '{invitation['team_name']}'"
        
        # Update invitation status
        invitations[invitation_index] = invitation
        self._save_data(self.invitations_file, invitations)
        
        return {"success": True, "message": response_message}
    
    def get_user_invitations(self, username: str) -> List[Dict]:
        """Get pending invitations for a user."""
        invitations = self._load_data(self.invitations_file)
        user_invitations = []
        
        current_time = datetime.now()
        
        for invitation in invitations:
            if (invitation["invitee_username"] == username and 
                invitation["status"] == "pending"):
                
                # Check if expired
                expires_at = datetime.fromisoformat(invitation["expires_at"])
                if current_time <= expires_at:
                    user_invitations.append(invitation)
        
        return user_invitations
    
    def delete_team(self, team_id: str, username: str) -> Dict:
        """Delete a team (only creator can delete)."""
        teams = self._load_data(self.teams_file)
        
        if team_id not in teams:
            return {"success": False, "message": "Team not found"}
        
        team = teams[team_id]
        
        # Only creator can delete the team
        if team["creator"] != username:
            return {"success": False, "message": "Only the team creator can delete the team"}
        
        team_name = team["name"]
        del teams[team_id]
        self._save_data(self.teams_file, teams)
        
        # Cancel all pending invitations for this team
        invitations = self._load_data(self.invitations_file)
        for invitation in invitations:
            if invitation["team_id"] == team_id and invitation["status"] == "pending":
                invitation["status"] = "cancelled"
        self._save_data(self.invitations_file, invitations)
        
        return {"success": True, "message": f"Team '{team_name}' has been deleted"}
    
    def leave_team(self, team_id: str, username: str) -> Dict:
        """Leave a team."""
        teams = self._load_data(self.teams_file)
        
        if team_id not in teams:
            return {"success": False, "message": "Team not found"}
        
        team = teams[team_id]
        
        if username not in team["members"]:
            return {"success": False, "message": "You're not a member of this team"}
        
        # Any member can leave including creator
        team["members"].remove(username)
        
        # If no members left, delete the team
        if not team["members"]:
            del teams[team_id]
            self._save_data(self.teams_file, teams)
            return {"success": True, "message": f"Left team '{team['name']}'. Team was deleted as it was empty."}
        
        # If captain leaves, assign new captain (creator takes priority if still in team)
        if team["captain"] == username:
            if team["creator"] in team["members"]:
                team["captain"] = team["creator"]
            elif team["members"]:
                team["captain"] = team["members"][0]
        
        teams[team_id] = team
        self._save_data(self.teams_file, teams)
        
        return {"success": True, "message": f"Successfully left team '{team['name']}'"}
    
    def get_public_teams(self) -> List[Dict]:
        """Get all public teams that users can discover."""
        teams = self._load_data(self.teams_file)
        public_teams = []
        
        for team_id, team_data in teams.items():
            if team_data.get("is_public", True) and team_data.get("is_active", True):
                public_teams.append({
                    "team_id": team_id,
                    "name": team_data["name"],
                    "description": team_data.get("description", ""),
                    "creator": team_data["creator"],
                    "member_count": len(team_data["members"]),
                    "max_members": team_data.get("max_members", 10),
                    "total_value": team_data.get("total_value", 0),
                    "created_at": team_data["created_at"]
                })
        
        return sorted(public_teams, key=lambda x: x["total_value"], reverse=True)
    
    def get_user_team(self, username: str) -> Optional[Dict]:
        """Get the team a user belongs to."""
        teams = self._load_data(self.teams_file)
        
        for team_id, team_data in teams.items():
            if username in team_data.get("members", []):
                return {"team_id": team_id, **team_data}
        
        return None
    
    def _create_notification(self, username: str, title: str, message: str, 
                           notification_type: str, data: Dict = None):
        """Create a notification for a user and send email."""
        notifications = self._load_data(self.notifications_file)
        
        notification = {
            "id": str(uuid.uuid4()),
            "username": username,
            "title": title,
            "message": message,
            "type": notification_type,
            "data": data or {},
            "read": False,
            "created_at": datetime.now().isoformat()
        }
        
        notifications.append(notification)
        self._save_data(self.notifications_file, notifications)
        
        # Send email notification for every new notification
        self._send_team_notification_email(username, title, message)
    
    def get_user_notifications(self, username: str) -> List[Dict]:
        """Get notifications for a user."""
        notifications = self._load_data(self.notifications_file)
        user_notifications = [n for n in notifications if n["username"] == username]
        return sorted(user_notifications, key=lambda x: x["created_at"], reverse=True)
    
    def mark_notification_read(self, notification_id: str, username: str) -> Dict:
        """Mark a notification as read."""
        notifications = self._load_data(self.notifications_file)
        
        for notification in notifications:
            if (notification["id"] == notification_id and 
                notification["username"] == username):
                notification["read"] = True
                self._save_data(self.notifications_file, notifications)
                return {"success": True, "message": "Notification marked as read"}
        
        return {"success": False, "message": "Notification not found"}
    
    def search_users_for_invitation(self, search_query: str, current_username: str) -> List[Dict]:
        """Search for users to invite to team."""
        # Import here to avoid circular imports
        from modules.auth_manager import AuthManager
        
        auth_manager = AuthManager()
        users = auth_manager._load_users()
        teams = self._load_data(self.teams_file)
        
        # Find users not in any team
        users_in_teams = set()
        for team_data in teams.values():
            users_in_teams.update(team_data.get("members", []))
        
        search_results = []
        search_lower = search_query.lower()
        
        for user_id, user_data in users.items():
            username = user_data.get("username", "")
            if (username != current_username and 
                username not in users_in_teams and
                (search_lower in username.lower() or 
                 search_lower in user_data.get("first_name", "").lower() or
                 search_lower in user_data.get("last_name", "").lower())):
                
                search_results.append({
                    "username": username,
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                    "role": user_data.get("role", "basic")
                })
        
        return search_results[:10]  # Limit to 10 results
    
    def update_team_values(self, portfolio_manager):
        """Update team total values based on member portfolios."""
        teams = self._load_data(self.teams_file)
        
        for team_id, team_data in teams.items():
            total_value = 0.0
            
            for member in team_data.get("members", []):
                try:
                    portfolio_value = portfolio_manager.calculate_portfolio_value(member)
                    if portfolio_value:
                        total_value += portfolio_value
                except:
                    continue
            
            teams[team_id]["total_value"] = total_value
        
        self._save_data(self.teams_file, teams)
    
    def get_team_leaderboard(self, portfolio_manager) -> List[Dict]:
        """Get team leaderboard sorted by total portfolio value."""
        self.update_team_values(portfolio_manager)
        teams = self._load_data(self.teams_file)
        
        team_list = []
        for team_id, team_data in teams.items():
            team_list.append({
                "team_id": team_id,
                "name": team_data["name"],
                "creator": team_data["creator"],
                "captain": team_data["captain"],
                "members": team_data.get("members", []),
                "member_count": len(team_data.get("members", [])),
                "total_value": team_data.get("total_value", 0),
                "competitions_won": team_data.get("competitions_won", 0),
                "badges": team_data.get("badges", []),
                "is_public": team_data.get("is_public", True)
            })
        
        return sorted(team_list, key=lambda x: x["total_value"], reverse=True)
    
    def _send_invitation_email(self, invitee_username: str, team_name: str, inviter_username: str, invitation_id: str):
        """Send email notification for team invitation."""
        try:
            from modules.email_service import EmailService
            from modules.auth_manager import AuthManager
            
            email_service = EmailService()
            auth_manager = AuthManager()
            
            # Get invitee's email
            invitee_data = auth_manager.get_user_by_username(invitee_username)
            if invitee_data and invitee_data.get('email'):
                invitee_name = f"{invitee_data.get('first_name', '')} {invitee_data.get('last_name', '')}".strip()
                if not invitee_name:
                    invitee_name = invitee_username
                
                result = email_service.send_team_invitation_email(
                    invitee_data['email'],
                    invitee_name,
                    team_name,
                    inviter_username,
                    invitation_id
                )
                
                # Log result but don't fail the invitation if email fails
                if not result['success']:
                    print(f"Failed to send invitation email: {result['message']}")
        except Exception as e:
            # Don't fail the invitation if email service has issues
            print(f"Email service error: {str(e)}")
    
    def _send_team_notification_email(self, username: str, title: str, message: str):
        """Send email notification for team events."""
        try:
            from modules.email_service import EmailService
            from modules.auth_manager import AuthManager
            
            email_service = EmailService()
            auth_manager = AuthManager()
            
            # Get user's email
            user_data = auth_manager.get_user_by_username(username)
            if user_data and user_data.get('email'):
                user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                if not user_name:
                    user_name = username
                
                result = email_service.send_team_notification_email(
                    user_data['email'],
                    user_name,
                    title,
                    message
                )
                
                if not result['success']:
                    print(f"Failed to send notification email: {result['message']}")
        except Exception as e:
            print(f"Email service error: {str(e)}")