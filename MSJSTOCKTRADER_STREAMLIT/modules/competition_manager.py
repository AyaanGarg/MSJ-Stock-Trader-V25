import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class CompetitionManager:
    """Manages 6-month trading competitions with automatic data cleanup and winner tracking."""
    
    def __init__(self):
        self.competitions_file = "data/competitions.json"
        self.notifications_file = "data/deletion_notifications.json"
        self._ensure_data_directory()
        self._initialize_data()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs("data", exist_ok=True)
    
    def _initialize_data(self):
        """Initialize competition data files."""
        if not os.path.exists(self.competitions_file):
            default_data = {
                "current_season": None,
                "seasons": [],
                "settings": {
                    "competition_duration_months": 6,
                    "starting_cash": 100000.0,
                    "notification_days": [30, 7, 1]
                }
            }
            self._save_json(self.competitions_file, default_data)
        
        if not os.path.exists(self.notifications_file):
            self._save_json(self.notifications_file, {})
    
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
    
    def get_current_season(self) -> Optional[Dict]:
        """Get current active competition season."""
        data = self._load_json(self.competitions_file)
        current_id = data.get("current_season")
        
        if not current_id:
            return None
        
        # Find the season
        for season in data.get("seasons", []):
            if season["season_id"] == current_id:
                return season
        
        return None
    
    def start_new_season(self, start_date_str: Optional[str] = None, end_date_str: Optional[str] = None) -> Dict:
        """Start a new 6-month competition season.
        
        Args:
            start_date_str: Optional start date in 'YYYY-MM-DD' format
            end_date_str: Optional end date in 'YYYY-MM-DD' format
        """
        data = self._load_json(self.competitions_file)
        
        # Check if there's already an active season
        if data.get("current_season"):
            return {
                "success": False,
                "message": "A competition season is already active. End it first before starting a new one."
            }
        
        # Create new season
        season_id = str(uuid.uuid4())
        
        # Use provided dates or default to now + 6 months
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.now()
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = start_date + timedelta(days=182)  # Approximately 6 months
        
        new_season = {
            "season_id": season_id,
            "season_number": len(data.get("seasons", [])) + 1,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": "active",
            "participants": [],
            "winners": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Add to seasons list
        if "seasons" not in data:
            data["seasons"] = []
        data["seasons"].append(new_season)
        data["current_season"] = season_id
        
        self._save_json(self.competitions_file, data)
        
        return {
            "success": True,
            "message": f"Season {new_season['season_number']} started successfully!",
            "season": new_season
        }
    
    def end_current_season(self, winners: List[Dict]) -> Dict:
        """End the current season and declare winners."""
        data = self._load_json(self.competitions_file)
        current_id = data.get("current_season")
        
        if not current_id:
            return {
                "success": False,
                "message": "No active season to end."
            }
        
        # Find and update the season
        for i, season in enumerate(data["seasons"]):
            if season["season_id"] == current_id:
                data["seasons"][i]["status"] = "completed"
                data["seasons"][i]["winners"] = winners
                data["seasons"][i]["ended_at"] = datetime.now().isoformat()
                break
        
        # Clear current season
        data["current_season"] = None
        
        self._save_json(self.competitions_file, data)
        
        return {
            "success": True,
            "message": "Season ended successfully!",
            "winners": winners
        }
    
    def add_participant(self, user_id: str, username: str) -> Dict:
        """Add a user to the current competition season."""
        data = self._load_json(self.competitions_file)
        current_id = data.get("current_season")
        
        if not current_id:
            return {
                "success": False,
                "message": "No active season."
            }
        
        # Find the season and add participant
        for i, season in enumerate(data["seasons"]):
            if season["season_id"] == current_id:
                # Check if already a participant
                if any(p["user_id"] == user_id for p in season.get("participants", [])):
                    return {
                        "success": False,
                        "message": "User already registered for this season."
                    }
                
                participant = {
                    "user_id": user_id,
                    "username": username,
                    "joined_at": datetime.now().isoformat()
                }
                
                if "participants" not in data["seasons"][i]:
                    data["seasons"][i]["participants"] = []
                
                data["seasons"][i]["participants"].append(participant)
                break
        
        self._save_json(self.competitions_file, data)
        
        return {
            "success": True,
            "message": "Registered for competition successfully!"
        }
    
    def get_all_seasons(self) -> List[Dict]:
        """Get all competition seasons."""
        data = self._load_json(self.competitions_file)
        return data.get("seasons", [])
    
    def get_season_by_id(self, season_id: str) -> Optional[Dict]:
        """Get a specific season by ID."""
        data = self._load_json(self.competitions_file)
        for season in data.get("seasons", []):
            if season["season_id"] == season_id:
                return season
        return None
    
    def check_season_expiry(self) -> Dict:
        """Check if current season has expired and needs to be ended."""
        current_season = self.get_current_season()
        
        if not current_season:
            return {
                "expired": False,
                "message": "No active season."
            }
        
        end_date = datetime.fromisoformat(current_season["end_date"])
        now = datetime.now()
        
        if now >= end_date:
            return {
                "expired": True,
                "season": current_season,
                "days_overdue": (now - end_date).days
            }
        
        days_remaining = (end_date - now).days
        return {
            "expired": False,
            "days_remaining": days_remaining,
            "season": current_season
        }
    
    def schedule_deletion_notification(self, user_id: str, days_until_deletion: int) -> Dict:
        """Schedule a notification for upcoming data deletion."""
        notifications = self._load_json(self.notifications_file)
        
        if user_id not in notifications:
            notifications[user_id] = []
        
        notification = {
            "notification_id": str(uuid.uuid4()),
            "days_until_deletion": days_until_deletion,
            "scheduled_date": datetime.now().isoformat(),
            "deletion_date": (datetime.now() + timedelta(days=days_until_deletion)).isoformat(),
            "sent": False
        }
        
        notifications[user_id].append(notification)
        self._save_json(self.notifications_file, notifications)
        
        return {
            "success": True,
            "notification": notification
        }
    
    def get_pending_notifications(self, user_id: str) -> List[Dict]:
        """Get all pending deletion notifications for a user."""
        notifications = self._load_json(self.notifications_file)
        user_notifications = notifications.get(user_id, [])
        
        return [n for n in user_notifications if not n.get("sent", False)]
    
    def mark_notification_sent(self, user_id: str, notification_id: str) -> Dict:
        """Mark a notification as sent."""
        notifications = self._load_json(self.notifications_file)
        
        if user_id in notifications:
            for i, notif in enumerate(notifications[user_id]):
                if notif["notification_id"] == notification_id:
                    notifications[user_id][i]["sent"] = True
                    notifications[user_id][i]["sent_at"] = datetime.now().isoformat()
                    break
        
        self._save_json(self.notifications_file, notifications)
        
        return {"success": True}
    
    def get_competition_stats(self) -> Dict:
        """Get overall competition statistics."""
        data = self._load_json(self.competitions_file)
        seasons = data.get("seasons", [])
        
        total_seasons = len(seasons)
        active_seasons = sum(1 for s in seasons if s.get("status") == "active")
        completed_seasons = sum(1 for s in seasons if s.get("status") == "completed")
        total_participants = sum(len(s.get("participants", [])) for s in seasons)
        
        return {
            "total_seasons": total_seasons,
            "active_seasons": active_seasons,
            "completed_seasons": completed_seasons,
            "total_participants": total_participants,
            "current_season": self.get_current_season()
        }
