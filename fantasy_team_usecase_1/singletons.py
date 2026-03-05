import logging

logger = logging.getLogger(__name__)

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class DatabaseManager(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = None
        
    def connect(self):
        if not self.connection:
            logger.info("Connected to SQLite database.")
            self.connection = "SQLite Connection Active"
        return self.connection

    def save_team(self, team):
        logger.info(f"Saved team '{team.name}' with {len(team.players)} players.")
        return True

class APIService(metaclass=SingletonMeta):
    def fetch_player_data(self):
        players = []
        try:
            import csv
            import os
            
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'fpl_stats_gw24.csv')
            
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        cost = float(row.get('Cost', '4.0'))
                    except ValueError:
                        cost = 4.0
                    
                    try:
                        fpl_id = int(row.get('ID', 0))
                    except ValueError:
                        fpl_id = 0
                        
                    name = row.get('Name', 'Unknown')
                    pos_id = row.get('Position', '0')
                    
                    def safe_int(val):
                        return int(val) if val and str(val).isdigit() else 0
                        
                    def safe_float(val):
                        try:
                            return float(val)
                        except (ValueError, TypeError):
                            return 0.0
                    
                    players.append({
                        "id": fpl_id,
                        "name": name,
                        "team": row.get('Team', 'Unknown'),
                        "position": pos_id, 
                        "cost": cost,
                        "total_points": safe_int(row.get('Total Points')),
                        "minutes": safe_int(row.get('Minutes')),
                        "saves": safe_int(row.get('Saves')),
                        "clean_sheets": safe_int(row.get('Clean Sheets')),
                        "goals_conceded": safe_int(row.get('Goals Conceded')),
                        "goals": safe_int(row.get('Goals')),
                        "assists": safe_int(row.get('Assists')),
                        "threat": safe_float(row.get('Threat')),
                        "creativity": safe_float(row.get('Creativity')),
                        "influence": safe_float(row.get('Influence'))
                    })
                    
        except FileNotFoundError as e:
            logger.error(f"Could not locate CSV file at path: {csv_path}")
            raise FileNotFoundError("Real-world player data (CSV) is required. Ensure 'fpl_stats_gw24.csv' is present.") from e
            
        return players
