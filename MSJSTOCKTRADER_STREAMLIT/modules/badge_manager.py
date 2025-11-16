"""
Badge Manager for MSJSTOCKTRADER

Manages user badges, achievements, competitions, and badge inventory system.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class BadgeManager:
    """Manages user badges, achievements, and competitions."""
    
    def __init__(self):
        self.data_dir = "data"
        self.badges_file = os.path.join(self.data_dir, "user_badges.json")
        self.badge_definitions_file = os.path.join(self.data_dir, "badge_definitions.json")
        self.competitions_file = os.path.join(self.data_dir, "competitions.json")
        self._ensure_data_directory()
        self._initialize_badge_definitions()
        self._initialize_user_badges()
        self._initialize_competitions()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _initialize_badge_definitions(self):
        """Initialize badge definitions with various achievement badges."""
        if not os.path.exists(self.badge_definitions_file):
            badge_definitions = {
                # Leaderboard Badges
                "leaderboard_champion": {
                    "name": "🏆 Leaderboard Champion",
                    "description": "Reached #1 on the leaderboard",
                    "category": "Competition",
                    "rarity": "Legendary",
                    "color": "#FFD700",
                    "icon": "🏆",
                    "requirements": "Be #1 on the leaderboard"
                },
                "top_3_trader": {
                    "name": "🥉 Top 3 Trader",
                    "description": "Finished in top 3 on leaderboard",
                    "category": "Competition", 
                    "rarity": "Epic",
                    "color": "#CD7F32",
                    "icon": "🥉",
                    "requirements": "Finish in top 3 on leaderboard"
                },
                "top_10_performer": {
                    "name": "⭐ Top 10 Performer",
                    "description": "Reached top 10 on leaderboard",
                    "category": "Competition",
                    "rarity": "Rare",
                    "color": "#C0C0C0",
                    "icon": "⭐",
                    "requirements": "Reach top 10 on leaderboard"
                },
                
                # Trading Achievement Badges
                "millionaire": {
                    "name": "💰 Millionaire",
                    "description": "Portfolio value exceeded $1,000,000",
                    "category": "Trading",
                    "rarity": "Legendary",
                    "color": "#00FF00",
                    "icon": "💰",
                    "requirements": "Portfolio value > $1,000,000"
                },
                "big_gains": {
                    "name": "📈 Big Gains",
                    "description": "Achieved 100%+ portfolio gain",
                    "category": "Trading",
                    "rarity": "Epic",
                    "color": "#4CAF50",
                    "icon": "📈",
                    "requirements": "100%+ portfolio gain"
                },
                "diamond_hands": {
                    "name": "💎 Diamond Hands",
                    "description": "Held a position for 30+ days",
                    "category": "Trading",
                    "rarity": "Rare",
                    "color": "#E3F2FD",
                    "icon": "💎",
                    "requirements": "Hold position for 30+ days"
                },
                "day_trader": {
                    "name": "⚡ Day Trader",
                    "description": "Completed 50+ day trades",
                    "category": "Trading",
                    "rarity": "Rare",
                    "color": "#FF9800",
                    "icon": "⚡",
                    "requirements": "Complete 50+ day trades"
                },
                "profit_streak": {
                    "name": "🔥 Profit Streak",
                    "description": "7 consecutive profitable trading days",
                    "category": "Trading",
                    "rarity": "Epic",
                    "color": "#F44336",
                    "icon": "🔥",
                    "requirements": "7 consecutive profitable days"
                },
                
                # Social Badges
                "social_butterfly": {
                    "name": "🦋 Social Butterfly",
                    "description": "Made 10+ friends on the platform",
                    "category": "Social",
                    "rarity": "Common",
                    "color": "#E91E63",
                    "icon": "🦋",
                    "requirements": "Make 10+ friends"
                },
                "chat_master": {
                    "name": "💬 Chat Master",
                    "description": "Sent 1000+ chat messages",
                    "category": "Social",
                    "rarity": "Rare",
                    "color": "#9C27B0",
                    "icon": "💬",
                    "requirements": "Send 1000+ messages"
                },
                "mentor": {
                    "name": "🧑‍🏫 Mentor",
                    "description": "Helped 5+ new traders get started",
                    "category": "Social",
                    "rarity": "Epic",
                    "color": "#3F51B5",
                    "icon": "🧑‍🏫",
                    "requirements": "Help 5+ new traders"
                },
                
                # Special Event Badges
                "early_adopter": {
                    "name": "🚀 Early Adopter",
                    "description": "Joined during beta testing",
                    "category": "Special",
                    "rarity": "Legendary",
                    "color": "#9C27B0",
                    "icon": "🚀",
                    "requirements": "Joined during beta"
                },
                "weekend_warrior": {
                    "name": "⚔️ Weekend Warrior",
                    "description": "Active trader on weekends",
                    "category": "Special",
                    "rarity": "Rare",
                    "color": "#607D8B",
                    "icon": "⚔️",
                    "requirements": "Trade on 10+ weekends"
                },
                "night_owl": {
                    "name": "🦉 Night Owl",
                    "description": "Active trader after midnight",
                    "category": "Special",
                    "rarity": "Rare",
                    "color": "#263238",
                    "icon": "🦉",
                    "requirements": "Trade after midnight 20+ times"
                },
                
                # Competition Badges
                "tournament_winner": {
                    "name": "🏅 Tournament Winner",
                    "description": "Won a trading tournament",
                    "category": "Competition",
                    "rarity": "Legendary",
                    "color": "#FFD700",
                    "icon": "🏅",
                    "requirements": "Win a trading tournament"
                },
                "speed_trader": {
                    "name": "🏃 Speed Trader",
                    "description": "Fastest trader in speed competition",
                    "category": "Competition",
                    "rarity": "Epic",
                    "color": "#00BCD4",
                    "icon": "🏃",
                    "requirements": "Win speed trading competition"
                },
                "risk_master": {
                    "name": "🎯 Risk Master",
                    "description": "Best risk-adjusted returns",
                    "category": "Competition",
                    "rarity": "Epic",
                    "color": "#FF5722",
                    "icon": "🎯",
                    "requirements": "Best risk-adjusted returns"
                }
            }
            
            with open(self.badge_definitions_file, 'w') as f:
                json.dump(badge_definitions, f, indent=2)
    
    def _initialize_user_badges(self):
        """Initialize user badges file if it doesn't exist."""
        if not os.path.exists(self.badges_file):
            with open(self.badges_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def _initialize_competitions(self):
        """Initialize competitions tracking file."""
        if not os.path.exists(self.competitions_file):
            competitions = {
                "monthly_leaderboard": {
                    "name": "Monthly Leaderboard Competition",
                    "type": "leaderboard",
                    "start_date": datetime.now().replace(day=1).isoformat(),
                    "end_date": (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).isoformat(),
                    "prizes": {
                        "1st": "leaderboard_champion",
                        "2nd": "top_3_trader", 
                        "3rd": "top_3_trader",
                        "top_10": "top_10_performer"
                    },
                    "status": "active"
                },
                "weekly_profit_challenge": {
                    "name": "Weekly Profit Challenge",
                    "type": "profit",
                    "start_date": datetime.now().isoformat(),
                    "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
                    "prizes": {
                        "winner": "profit_streak"
                    },
                    "status": "active"
                }
            }
            
            with open(self.competitions_file, 'w') as f:
                json.dump(competitions, f, indent=2)
    
    def _load_user_badges(self) -> Dict:
        """Load user badges data."""
        try:
            with open(self.badges_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_user_badges(self, badges_data: Dict):
        """Save user badges data."""
        with open(self.badges_file, 'w') as f:
            json.dump(badges_data, f, indent=2)
    
    def _load_badge_definitions(self) -> Dict:
        """Load badge definitions."""
        try:
            with open(self.badge_definitions_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def award_badge(self, user_id: str, badge_id: str, reason: str = None) -> Dict:
        """Award a badge to a user."""
        badges_data = self._load_user_badges()
        badge_definitions = self._load_badge_definitions()
        
        if badge_id not in badge_definitions:
            return {
                "success": False,
                "message": "Badge definition not found"
            }
        
        if user_id not in badges_data:
            badges_data[user_id] = {
                "earned_badges": [],
                "equipped_badge": None,
                "badge_history": []
            }
        
        # Check if user already has this badge
        earned_badges = badges_data[user_id]["earned_badges"]
        if any(badge["badge_id"] == badge_id for badge in earned_badges):
            return {
                "success": False,
                "message": "User already has this badge"
            }
        
        # Award the badge
        new_badge = {
            "badge_id": badge_id,
            "earned_date": datetime.now().isoformat(),
            "reason": reason or "Achievement unlocked"
        }
        
        badges_data[user_id]["earned_badges"].append(new_badge)
        badges_data[user_id]["badge_history"].append({
            "action": "earned",
            "badge_id": badge_id,
            "date": datetime.now().isoformat(),
            "reason": reason or "Achievement unlocked"
        })
        
        # Auto-equip first badge or legendary badges
        if (not badges_data[user_id]["equipped_badge"] or 
            badge_definitions[badge_id]["rarity"] == "Legendary"):
            badges_data[user_id]["equipped_badge"] = badge_id
        
        self._save_user_badges(badges_data)
        
        return {
            "success": True,
            "message": f"Badge '{badge_definitions[badge_id]['name']}' awarded!",
            "badge": badge_definitions[badge_id]
        }
    
    def equip_badge(self, user_id: str, badge_id: str) -> Dict:
        """Equip a badge for display on user profile."""
        badges_data = self._load_user_badges()
        badge_definitions = self._load_badge_definitions()
        
        if user_id not in badges_data:
            return {
                "success": False,
                "message": "User has no badges"
            }
        
        # Check if user owns the badge
        earned_badges = badges_data[user_id]["earned_badges"]
        if not any(badge["badge_id"] == badge_id for badge in earned_badges):
            return {
                "success": False,
                "message": "You don't own this badge"
            }
        
        # Equip the badge
        badges_data[user_id]["equipped_badge"] = badge_id
        badges_data[user_id]["badge_history"].append({
            "action": "equipped",
            "badge_id": badge_id,
            "date": datetime.now().isoformat()
        })
        
        self._save_user_badges(badges_data)
        
        return {
            "success": True,
            "message": f"Badge '{badge_definitions[badge_id]['name']}' equipped!",
            "badge": badge_definitions[badge_id]
        }
    
    def unequip_badge(self, user_id: str) -> Dict:
        """Unequip currently equipped badge."""
        badges_data = self._load_user_badges()
        
        if user_id not in badges_data or not badges_data[user_id].get("equipped_badge"):
            return {
                "success": False,
                "message": "No badge currently equipped"
            }
        
        badges_data[user_id]["equipped_badge"] = None
        badges_data[user_id]["badge_history"].append({
            "action": "unequipped",
            "date": datetime.now().isoformat()
        })
        
        self._save_user_badges(badges_data)
        
        return {
            "success": True,
            "message": "Badge unequipped"
        }
    
    def get_user_badges(self, user_id: str) -> Dict:
        """Get all badges for a user."""
        badges_data = self._load_user_badges()
        badge_definitions = self._load_badge_definitions()
        
        if user_id not in badges_data:
            return {
                "earned_badges": [],
                "equipped_badge": None,
                "badge_count": 0
            }
        
        user_badge_data = badges_data[user_id]
        
        # Enrich badge data with definitions
        enriched_badges = []
        for badge in user_badge_data["earned_badges"]:
            badge_id = badge["badge_id"]
            if badge_id in badge_definitions:
                enriched_badge = {**badge, **badge_definitions[badge_id]}
                enriched_badges.append(enriched_badge)
        
        equipped_badge_data = None
        if user_badge_data.get("equipped_badge"):
            equipped_id = user_badge_data["equipped_badge"]
            if equipped_id in badge_definitions:
                equipped_badge_data = badge_definitions[equipped_id]
        
        return {
            "earned_badges": enriched_badges,
            "equipped_badge": equipped_badge_data,
            "equipped_badge_id": user_badge_data.get("equipped_badge"),
            "badge_count": len(enriched_badges),
            "badge_history": user_badge_data.get("badge_history", [])
        }
    
    def get_all_badge_definitions(self) -> Dict:
        """Get all available badge definitions."""
        return self._load_badge_definitions()
    
    def check_and_award_achievements(self, user_id: str, user_stats: Dict) -> List[Dict]:
        """Check user stats and award applicable achievements."""
        awarded_badges = []
        badges_data = self._load_user_badges()
        
        # Get user's existing badges
        existing_badge_ids = []
        if user_id in badges_data:
            existing_badge_ids = [badge["badge_id"] for badge in badges_data[user_id]["earned_badges"]]
        
        # Check portfolio value achievements
        portfolio_value = user_stats.get("portfolio_value", 0)
        if portfolio_value >= 1000000 and "millionaire" not in existing_badge_ids:
            result = self.award_badge(user_id, "millionaire", "Portfolio exceeded $1,000,000")
            if result["success"]:
                awarded_badges.append(result)
        
        # Check trading achievements
        total_trades = user_stats.get("total_trades", 0)
        if total_trades >= 50 and "day_trader" not in existing_badge_ids:
            result = self.award_badge(user_id, "day_trader", "Completed 50+ trades")
            if result["success"]:
                awarded_badges.append(result)
        
        # Check social achievements
        friend_count = user_stats.get("friend_count", 0)
        if friend_count >= 10 and "social_butterfly" not in existing_badge_ids:
            result = self.award_badge(user_id, "social_butterfly", "Made 10+ friends")
            if result["success"]:
                awarded_badges.append(result)
        
        # Check leaderboard position
        leaderboard_position = user_stats.get("leaderboard_position", 999)
        if leaderboard_position == 1 and "leaderboard_champion" not in existing_badge_ids:
            result = self.award_badge(user_id, "leaderboard_champion", "Reached #1 on leaderboard")
            if result["success"]:
                awarded_badges.append(result)
        elif leaderboard_position <= 3 and "top_3_trader" not in existing_badge_ids:
            result = self.award_badge(user_id, "top_3_trader", f"Reached #{leaderboard_position} on leaderboard")
            if result["success"]:
                awarded_badges.append(result)
        elif leaderboard_position <= 10 and "top_10_performer" not in existing_badge_ids:
            result = self.award_badge(user_id, "top_10_performer", f"Reached #{leaderboard_position} on leaderboard")
            if result["success"]:
                awarded_badges.append(result)
        
        return awarded_badges
    
    def get_equipped_badge_html(self, user_id: str) -> str:
        """Get HTML for user's equipped badge."""
        user_badges = self.get_user_badges(user_id)
        
        if not user_badges["equipped_badge"]:
            return ""
        
        badge = user_badges["equipped_badge"]
        
        return f"""
        <span style="background: {badge['color']}; color: white; padding: 4px 8px; 
                     border-radius: 15px; font-size: 12px; font-weight: bold;
                     box-shadow: 0 2px 4px rgba(0,0,0,0.2); margin-left: 8px;">
            {badge['icon']} {badge['name']}
        </span>
        """
    
    def get_badge_rarity_color(self, rarity: str) -> str:
        """Get color for badge rarity."""
        colors = {
            "Common": "#9E9E9E",
            "Rare": "#2196F3", 
            "Epic": "#9C27B0",
            "Legendary": "#FF9800"
        }
        return colors.get(rarity, "#9E9E9E")
    
    def get_badge_display(self, username: str) -> str:
        """Get the badge display for a user."""
        try:
            user_badges = self.get_user_badges(username)
            if not user_badges:
                return ""
            
            # Get the most recent badge
            latest_badge = user_badges[-1]
            badge_definitions = self._load_badge_definitions()
            badge_def = badge_definitions.get(latest_badge['badge_id'], {})
            
            return badge_def.get('icon', '🏆')
        except:
            return ""