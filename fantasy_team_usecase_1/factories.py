from fantasy_team_usecase_1.models import Goalkeeper, Defender, Midfielder, Forward

class PlayerFactory:
    @staticmethod
    def create_player(player_data: dict):
        position = str(player_data.get("position", "")).lower()
        id = player_data.get("id", 0)
        name = player_data.get("name", "Unknown Player")
        team = player_data.get("team", "Unknown Team")
        cost = player_data.get("cost", 4.0)
        total_points = player_data.get("total_points", 0)
        minutes = player_data.get("minutes", 0)
        
        if position in ("goalkeeper", "gk", "1"):
            saves = player_data.get("saves", 0)
            clean_sheets = player_data.get("clean_sheets", 0)
            goals_conceded = player_data.get("goals_conceded", 0)
            return Goalkeeper(id, name, team, cost, total_points, minutes, saves, clean_sheets, goals_conceded)
            
        elif position in ("defender", "def", "2"):
            clean_sheets = player_data.get("clean_sheets", 0)
            goals_conceded = player_data.get("goals_conceded", 0)
            threat = player_data.get("threat", 0.0)
            return Defender(id, name, team, cost, total_points, minutes, clean_sheets, goals_conceded, threat)
            
        elif position in ("midfielder", "mid", "3"):
            goals = player_data.get("goals", 0)
            assists = player_data.get("assists", 0)
            creativity = player_data.get("creativity", 0.0)
            return Midfielder(id, name, team, cost, total_points, minutes, goals, assists, creativity)
            
        elif position in ("forward", "fwd", "4"):
            goals = player_data.get("goals", 0)
            assists = player_data.get("assists", 0)
            threat = player_data.get("threat", 0.0)
            influence = player_data.get("influence", 0.0)
            return Forward(id, name, team, cost, total_points, minutes, goals, assists, threat, influence)
            
        else:
            raise ValueError(f"Unknown position identifier: {position}")
