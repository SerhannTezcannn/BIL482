import sqlite3
from collections import defaultdict
from core.event_bus import bus, Events
from fantasy_points_usecase_2.calculator import TeamPointCalculator

class TeamScoreUpdaterObserver:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def update(self, gameweek_id: int):
        print(f"[Observer - Use Case 4] New Gameweek {gameweek_id} data detected! Recalculating all team points...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT id, name, budget_used FROM user_teams")
        teams_data = {row['id']: dict(row) for row in c.fetchall()}
        
        calc = TeamPointCalculator()
        
        query = '''
            SELECT tp.team_id, p.id, p.position_id as position, 
                   s.total_points, s.minutes, s.saves, s.clean_sheets, s.goals_conceded,
                   s.goals, s.assists, s.yellow_cards, s.red_cards, s.bonus, s.ict_index,
                   s.result, s.venue, tp.is_captain, tp.is_bench
            FROM team_players tp
            JOIN players p ON tp.player_id = p.id
            LEFT JOIN stats s ON p.id = s.player_id AND s.gameweek = ?
        '''
        c.execute(query, (gameweek_id,))
        
        team_players_map = defaultdict(list)
        for row in c.fetchall():
            row_dict = dict(row)
            t_id = row_dict.pop('team_id')
            team_players_map[t_id].append(row_dict)
        
        for team_id, team_info in teams_data.items():
            players = team_players_map.get(team_id, [])
            gw_score = calc.calculate_team_score(players)
            
            bus.publish(Events.TEAM_SCORES_UPDATED, {
                "team_id": team_id,
                "team_name": team_info['name'],
                "score": gw_score,
                "budget": team_info['budget_used']
            })
            
        conn.close()
        print(f"[Observer - Use Case 4] Successfully recalculated points for {len(teams_data)} teams!")
