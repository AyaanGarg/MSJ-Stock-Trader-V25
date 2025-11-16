import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AnnouncementsManager:
    """Manage system announcements with auto-deletion after 24 hours."""
    
    def __init__(self):
        self.announcements_file = "data/announcements.json"
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure announcements data file exists."""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.announcements_file):
            with open(self.announcements_file, 'w') as f:
                json.dump([], f)
    
    def add_announcement(self, message: str, priority: str = "Medium", admin_id: str = None) -> Dict:
        """Add a new announcement."""
        try:
            announcements = self._load_announcements()
            
            # Clean up old announcements first
            self._cleanup_old_announcements(announcements)
            
            new_announcement = {
                "id": str(len(announcements) + 1),
                "message": message,
                "priority": priority,
                "admin_id": admin_id,
                "timestamp": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            announcements.append(new_announcement)
            
            # Save updated announcements
            with open(self.announcements_file, 'w') as f:
                json.dump(announcements, f, indent=2)
            
            return {"success": True, "message": "Announcement added successfully"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to add announcement: {str(e)}"}
    
    def get_active_announcements(self) -> List[Dict]:
        """Get all active (non-expired) announcements."""
        try:
            announcements = self._load_announcements()
            
            # Clean up expired announcements
            active_announcements = self._cleanup_old_announcements(announcements)
            
            # Save cleaned list
            with open(self.announcements_file, 'w') as f:
                json.dump(active_announcements, f, indent=2)
            
            # Sort by priority and timestamp
            priority_order = {"High": 3, "Medium": 2, "Low": 1}
            active_announcements.sort(
                key=lambda x: (priority_order.get(x.get('priority', 'Medium'), 2), x.get('timestamp', '')),
                reverse=True
            )
            
            return active_announcements
            
        except Exception as e:
            return []
    
    def _load_announcements(self) -> List[Dict]:
        """Load announcements from file."""
        try:
            with open(self.announcements_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _cleanup_old_announcements(self, announcements: List[Dict]) -> List[Dict]:
        """Remove announcements older than 24 hours."""
        current_time = datetime.now()
        active_announcements = []
        
        for announcement in announcements:
            try:
                expires_at = datetime.fromisoformat(announcement.get('expires_at', ''))
                if current_time < expires_at:
                    active_announcements.append(announcement)
            except Exception:
                # If no expiration date or invalid format, check timestamp
                try:
                    timestamp = datetime.fromisoformat(announcement.get('timestamp', ''))
                    if current_time - timestamp < timedelta(hours=24):
                        active_announcements.append(announcement)
                except Exception:
                    # Skip invalid announcements
                    continue
        
        return active_announcements
    
    def delete_announcement(self, announcement_id: str) -> Dict:
        """Delete a specific announcement."""
        try:
            announcements = self._load_announcements()
            updated_announcements = [a for a in announcements if a.get('id') != announcement_id]
            
            with open(self.announcements_file, 'w') as f:
                json.dump(updated_announcements, f, indent=2)
            
            return {"success": True, "message": "Announcement deleted successfully"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to delete announcement: {str(e)}"}
    
    def cleanup_expired_announcements(self) -> Dict:
        """Manual cleanup of expired announcements."""
        try:
            announcements = self._load_announcements()
            active_announcements = self._cleanup_old_announcements(announcements)
            
            deleted_count = len(announcements) - len(active_announcements)
            
            with open(self.announcements_file, 'w') as f:
                json.dump(active_announcements, f, indent=2)
            
            return {
                "success": True, 
                "message": f"Cleaned up {deleted_count} expired announcements",
                "deleted_count": deleted_count,
                "active_count": len(active_announcements)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to cleanup announcements: {str(e)}"}