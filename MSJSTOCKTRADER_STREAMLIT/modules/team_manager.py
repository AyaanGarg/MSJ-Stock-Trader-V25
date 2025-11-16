import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import streamlit as st

class TeamManager:
    """Manages team creation, competitions, and leaderboards."""
    
    def __init__(self):
        self.teams_file = "data/teams.json"
        self.team_competitions_file = "data/team_competitions.json"
        self.solo_competitions_file = "data/solo_competitions.json"
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure all data files exist."""
        os.makedirs("data", exist_ok=True)
        
        for file_path in [self.teams_file, self.team_competitions_file, self.solo_competitions_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
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
    
    def create_team(self, team_name: str, creator_username: str, description: str = "") -> Dict:
        """Create a new team."""
        teams = self._load_data(self.teams_file)
        
        # Check if team name already exists
        for team_id, team_data in teams.items():
            if team_data["name"].lower() == team_name.lower():
                return {"success": False, "message": "Team name already exists"}
        
        team_id = str(uuid.uuid4())
        team_data = {
            "id": team_id,
            "name": team_name,
            "description": description,
            "creator": creator_username,
            "members": [creator_username],
            "captain": creator_username,
            "created_at": datetime.now().isoformat(),
            "total_value": 0.0,
            "competitions_won": 0,
            "badges": [],
            "is_active": True
        }
        
        teams[team_id] = team_data
        self._save_data(self.teams_file, teams)
        
        return {"success": True, "message": "Team created successfully", "team_id": team_id}
    
    def join_team(self, team_id: str, username: str) -> Dict:
        """Join an existing team."""
        teams = self._load_data(self.teams_file)
        
        if team_id not in teams:
            return {"success": False, "message": "Team not found"}
        
        team = teams[team_id]
        
        if username in team["members"]:
            return {"success": False, "message": "Already a member of this team"}
        
        if len(team["members"]) >= 10:  # Max team size
            return {"success": False, "message": "Team is full (maximum 10 members)"}
        
        team["members"].append(username)
        teams[team_id] = team
        self._save_data(self.teams_file, teams)
        
        return {"success": True, "message": "Successfully joined team"}
    
    def leave_team(self, team_id: str, username: str) -> Dict:
        """Leave a team."""
        teams = self._load_data(self.teams_file)
        
        if team_id not in teams:
            return {"success": False, "message": "Team not found"}
        
        team = teams[team_id]
        
        if username not in team["members"]:
            return {"success": False, "message": "Not a member of this team"}
        
        team["members"].remove(username)
        
        # If captain leaves, assign new captain
        if team["captain"] == username and team["members"]:
            team["captain"] = team["members"][0]
        elif not team["members"]:
            # Delete empty team
            del teams[team_id]
            self._save_data(self.teams_file, teams)
            return {"success": True, "message": "Left team (team deleted as it was empty)"}
        
        teams[team_id] = team
        self._save_data(self.teams_file, teams)
        
        return {"success": True, "message": "Successfully left team"}
    
    def get_user_team(self, username: str) -> Optional[Dict]:
        """Get the team a user belongs to."""
        teams = self._load_data(self.teams_file)
        
        for team_id, team_data in teams.items():
            if username in team_data["members"]:
                return {"team_id": team_id, **team_data}
        
        return None
    
    def get_all_teams(self) -> List[Dict]:
        """Get all teams."""
        teams = self._load_data(self.teams_file)
        return [{"team_id": team_id, **team_data} for team_id, team_data in teams.items()]
    
    def update_team_values(self, portfolio_manager):
        """Update team total values based on member portfolios."""
        teams = self._load_data(self.teams_file)
        
        for team_id, team_data in teams.items():
            total_value = 0.0
            
            for member in team_data["members"]:
                try:
                    portfolio = portfolio_manager.get_portfolio(member)
                    if portfolio:
                        portfolio_value = portfolio_manager.calculate_portfolio_value(member)
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
                "members": team_data["members"],
                "member_count": len(team_data["members"]),
                "total_value": team_data["total_value"],
                "competitions_won": team_data.get("competitions_won", 0),
                "badges": team_data.get("badges", []),
                "captain": team_data["captain"]
            })
        
        return sorted(team_list, key=lambda x: x["total_value"], reverse=True)
    
    def start_competition(self, competition_type: str, name: str, duration_days: int = 7) -> Dict:
        """Start a new competition."""
        competition_id = str(uuid.uuid4())
        
        competition_data = {
            "id": competition_id,
            "name": name,
            "type": competition_type,  # "solo" or "team"
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=duration_days)).isoformat(),
            "duration_days": duration_days,
            "is_active": True,
            "participants": [],
            "winners": [],
            "prizes": self._get_competition_prizes(competition_type)
        }
        
        file_path = self.team_competitions_file if competition_type == "team" else self.solo_competitions_file
        competitions = self._load_data(file_path)
        competitions[competition_id] = competition_data
        self._save_data(file_path, competitions)
        
        return {"success": True, "competition_id": competition_id}
    
    def _get_competition_prizes(self, competition_type: str) -> List[Dict]:
        """Get prizes for competition winners."""
        if competition_type == "team":
            return [
                {"position": 1, "badge": "team_champion", "name": "Team Champions"},
                {"position": 2, "badge": "team_silver", "name": "Team Silver Medal"},
                {"position": 3, "badge": "team_bronze", "name": "Team Bronze Medal"}
            ]
        else:
            return [
                {"position": 1, "badge": "solo_champion", "name": "Solo Champion"},
                {"position": 2, "badge": "solo_silver", "name": "Solo Silver Medal"},
                {"position": 3, "badge": "solo_bronze", "name": "Solo Bronze Medal"}
            ]
    
    def get_active_competitions(self) -> Dict:
        """Get all active competitions."""
        team_competitions = self._load_data(self.team_competitions_file)
        solo_competitions = self._load_data(self.solo_competitions_file)
        
        active_team = []
        active_solo = []
        
        current_time = datetime.now()
        
        for comp_id, comp_data in team_competitions.items():
            end_date = datetime.fromisoformat(comp_data["end_date"])
            if comp_data["is_active"] and current_time < end_date:
                active_team.append({"competition_id": comp_id, **comp_data})
        
        for comp_id, comp_data in solo_competitions.items():
            end_date = datetime.fromisoformat(comp_data["end_date"])
            if comp_data["is_active"] and current_time < end_date:
                active_solo.append({"competition_id": comp_id, **comp_data})
        
        return {"team": active_team, "solo": active_solo}