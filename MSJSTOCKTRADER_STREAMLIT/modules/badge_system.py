import json
import os
from datetime import datetime
from typing import Dict, List
import streamlit as st

class BadgeSystem:
    """Manages user badges and achievements."""
    
    def __init__(self):
        self.badges_file = "data/user_badges.json"
        self.badge_definitions_file = "data/badge_definitions.json"
        self._ensure_data_files()
        self._initialize_badge_definitions()
    
    def _ensure_data_files(self):
        """Ensure badge data files exist."""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists(self.badges_file):
            with open(self.badges_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.badge_definitions_file):
            with open(self.badge_definitions_file, 'w') as f:
                json.dump({}, f)
    
    def _initialize_badge_definitions(self):
        """Initialize all available badge definitions."""
        badges = {
            # Basic badges
            "newcomer": {
                "name": "Newcomer",
                "description": "Welcome to MSJSTOCKTRADER!",
                "icon": "🌟",
                "rarity": "common",
                "category": "starter"
            },
            "first_trade": {
                "name": "First Trade",
                "description": "Made your first trade",
                "icon": "📈",
                "rarity": "common",
                "category": "trading"
            },
            
            # Trading Performance Badges
            "profit_maker": {
                "name": "Profit Maker",
                "description": "Made your first profit",
                "icon": "💰",
                "rarity": "common",
                "category": "performance"
            },
            "big_winner": {
                "name": "Big Winner",
                "description": "Made over $10,000 profit",
                "icon": "🏆",
                "rarity": "rare",
                "category": "performance"
            },
            "millionaire": {
                "name": "Millionaire",
                "description": "Portfolio value reached $1,000,000",
                "icon": "💎",
                "rarity": "legendary",
                "category": "performance"
            },
            
            # Top Earner Badges
            "top_earner_bronze": {
                "name": "Bronze Earner",
                "description": "Top 10% earner this month",
                "icon": "🥉",
                "rarity": "rare",
                "category": "leaderboard"
            },
            "top_earner_silver": {
                "name": "Silver Earner",
                "description": "Top 5% earner this month",
                "icon": "🥈",
                "rarity": "epic",
                "category": "leaderboard"
            },
            "top_earner_gold": {
                "name": "Gold Earner",
                "description": "Top 1% earner this month",
                "icon": "🥇",
                "rarity": "legendary",
                "category": "leaderboard"
            },
            
            # Competition Badges
            "solo_champion": {
                "name": "Solo Champion",
                "description": "Won a solo competition",
                "icon": "👑",
                "rarity": "legendary",
                "category": "competition"
            },
            "solo_silver": {
                "name": "Solo Silver",
                "description": "2nd place in solo competition",
                "icon": "🥈",
                "rarity": "epic",
                "category": "competition"
            },
            "solo_bronze": {
                "name": "Solo Bronze",
                "description": "3rd place in solo competition",
                "icon": "🥉",
                "rarity": "rare",
                "category": "competition"
            },
            "team_champion": {
                "name": "Team Champion",
                "description": "Won a team competition",
                "icon": "🏆",
                "rarity": "legendary",
                "category": "team"
            },
            "team_silver": {
                "name": "Team Silver",
                "description": "2nd place in team competition",
                "icon": "🥈",
                "rarity": "epic",
                "category": "team"
            },
            "team_bronze": {
                "name": "Team Bronze",
                "description": "3rd place in team competition",
                "icon": "🥉",
                "rarity": "rare",
                "category": "team"
            },
            
            # Creative Achievement Badges
            "risk_taker": {
                "name": "Risk Taker",
                "description": "Made trades worth over 50% of portfolio",
                "icon": "🎲",
                "rarity": "rare",
                "category": "trading"
            },
            "diversified": {
                "name": "Diversified",
                "description": "Own stocks in 10+ different sectors",
                "icon": "🌈",
                "rarity": "rare",
                "category": "strategy"
            },
            "day_trader": {
                "name": "Day Trader",
                "description": "Made 10+ trades in a single day",
                "icon": "⚡",
                "rarity": "epic",
                "category": "trading"
            },
            "long_term_investor": {
                "name": "Long-term Investor",
                "description": "Held a position for 30+ days",
                "icon": "🐂",
                "rarity": "rare",
                "category": "strategy"
            },
            "social_butterfly": {
                "name": "Social Butterfly",
                "description": "Added 5+ friends",
                "icon": "🦋",
                "rarity": "common",
                "category": "social"
            },
            "team_player": {
                "name": "Team Player",
                "description": "Member of a team",
                "icon": "🤝",
                "rarity": "common",
                "category": "team"
            },
            "team_leader": {
                "name": "Team Leader",
                "description": "Captain of a team",
                "icon": "👨‍💼",
                "rarity": "rare",
                "category": "team"
            },
            
            # Special Achievement Badges
            "perfect_timing": {
                "name": "Perfect Timing",
                "description": "Bought at the daily low, sold at the daily high",
                "icon": "🎯",
                "rarity": "legendary",
                "category": "skill"
            },
            "comeback_king": {
                "name": "Comeback King",
                "description": "Recovered from 50%+ loss to profit",
                "icon": "👑",
                "rarity": "epic",
                "category": "resilience"
            },
            "streak_master": {
                "name": "Streak Master",
                "description": "10 profitable trades in a row",
                "icon": "🔥",
                "rarity": "epic",
                "category": "skill"
            },
            "market_predictor": {
                "name": "Market Predictor",
                "description": "Made 5 correct day trading predictions",
                "icon": "🔮",
                "rarity": "epic",
                "category": "prediction"
            },
            
            # Admin and Special Badges
            "admin": {
                "name": "Administrator",
                "description": "System administrator",
                "icon": "⚙️",
                "rarity": "legendary",
                "category": "admin"
            },
            "beta_tester": {
                "name": "Beta Tester",
                "description": "Early platform tester",
                "icon": "🧪",
                "rarity": "rare",
                "category": "special"
            },
            "vip": {
                "name": "VIP",
                "description": "Very Important Player",
                "icon": "💎",
                "rarity": "legendary",
                "category": "special"
            }
        }
        
        with open(self.badge_definitions_file, 'w') as f:
            json.dump(badges, f, indent=2)
    
    def _load_data(self, file_path: str) -> Dict:
        """Load data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, file_path: str, data: Dict):
        """Save data to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_badge_definitions(self) -> Dict:
        """Get all badge definitions."""
        return self._load_data(self.badge_definitions_file)
    
    def get_user_badges(self, username: str) -> Dict:
        """Get badges for a specific user."""
        user_badges = self._load_data(self.badges_file)
        return user_badges.get(username, {"owned_badges": ["newcomer"], "equipped_badge": "newcomer"})
    
    def award_badge(self, username: str, badge_id: str) -> bool:
        """Award a badge to a user."""
        user_badges = self._load_data(self.badges_file)
        badge_definitions = self.get_badge_definitions()
        
        if badge_id not in badge_definitions:
            return False
        
        if username not in user_badges:
            user_badges[username] = {"owned_badges": ["newcomer"], "equipped_badge": "newcomer"}
        
        if badge_id not in user_badges[username]["owned_badges"]:
            user_badges[username]["owned_badges"].append(badge_id)
            self._save_data(self.badges_file, user_badges)
            return True
        
        return False
    
    def equip_badge(self, username: str, badge_id: str) -> bool:
        """Equip a badge for display."""
        user_badges = self._load_data(self.badges_file)
        
        if username not in user_badges:
            return False
        
        if badge_id in user_badges[username]["owned_badges"]:
            user_badges[username]["equipped_badge"] = badge_id
            self._save_data(self.badges_file, user_badges)
            return True
        
        return False
    
    def get_badge_display(self, username: str) -> str:
        """Get the badge icon for display next to username."""
        user_badges = self.get_user_badges(username)
        badge_definitions = self.get_badge_definitions()
        
        equipped_badge = user_badges.get("equipped_badge", "newcomer")
        if equipped_badge in badge_definitions:
            return badge_definitions[equipped_badge]["icon"]
        
        return "🌟"  # Default badge
    
    def check_and_award_badges(self, username: str, portfolio_manager, trading_engine, friends_manager=None, team_manager=None):
        """Check and automatically award badges based on user activity."""
        user_badges = self.get_user_badges(username)
        
        # Get user data
        try:
            # Get user ID from auth manager first
            from modules.auth_manager import AuthManager
            auth_manager = AuthManager()
            users = auth_manager._load_data(auth_manager.users_file)
            user_id = None
            for uid, user_data in users.items():
                if user_data.get('username') == username:
                    user_id = uid
                    break
            
            if not user_id:
                return
                
            portfolio_value = portfolio_manager.get_portfolio_value(user_id)
            trades = []
            
            # Performance badges
            if portfolio_value >= 1000000 and "millionaire" not in user_badges["owned_badges"]:
                self.award_badge(username, "millionaire")
            
            if portfolio_value >= 110000 and "big_winner" not in user_badges["owned_badges"]:
                self.award_badge(username, "big_winner")
            
            if portfolio_value > 100000 and "profit_maker" not in user_badges["owned_badges"]:
                self.award_badge(username, "profit_maker")
            
            # Trading badges
            if len(trades) >= 1 and "first_trade" not in user_badges["owned_badges"]:
                self.award_badge(username, "first_trade")
            
            # Check positions for diversification
            positions = portfolio_manager.get_positions(user_id)
            if not positions.empty and len(positions) >= 10:
                if "diversified" not in user_badges["owned_badges"]:
                    self.award_badge(username, "diversified")
            
            # Social badges
            if friends_manager:
                friends = friends_manager.get_friends(username)
                if len(friends) >= 5 and "social_butterfly" not in user_badges["owned_badges"]:
                    self.award_badge(username, "social_butterfly")
            
            # Team badges
            if team_manager:
                user_team = team_manager.get_user_team(username)
                if user_team:
                    if "team_player" not in user_badges["owned_badges"]:
                        self.award_badge(username, "team_player")
                    
                    if user_team["captain"] == username and "team_leader" not in user_badges["owned_badges"]:
                        self.award_badge(username, "team_leader")
            
        except Exception as e:
            st.error(f"Error checking badges: {e}")
    
    def get_badges_by_category(self) -> Dict:
        """Get badges organized by category."""
        badge_definitions = self.get_badge_definitions()
        categories = {}
        
        for badge_id, badge_data in badge_definitions.items():
            category = badge_data.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append({"id": badge_id, **badge_data})
        
        return categories