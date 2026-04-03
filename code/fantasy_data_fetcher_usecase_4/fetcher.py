import sqlite3
import random
from core.event_bus import bus, Events
from fantasy_points_usecase_2.scoring_strategies import (
    GoalkeeperScoringStrategy, DefenderScoringStrategy, MidfielderScoringStrategy, ForwardScoringStrategy
)

class GameweekDataFetcher:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def fetch_and_save_data(self, target_gameweek: int):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("SELECT MAX(gameweek) FROM stats")
            latest_gw_row = c.fetchone()
            latest_gw = latest_gw_row[0] if latest_gw_row and latest_gw_row[0] is not None else 24

            c.execute("""
                SELECT s.*, p.position_id 
                FROM stats s
                JOIN players p ON s.player_id = p.id
                WHERE s.gameweek = ?
            """, (latest_gw,))
            
            columns = [desc[0] for desc in c.description][:-1] # Exclude position_id
            gw_data = c.fetchall()
            
            insert_query = f'''
                INSERT INTO stats ({", ".join(columns[1:])}) 
                VALUES ({", ".join(["?" for _ in columns[1:]])})
            '''
            
            strategies_map = {
                1: GoalkeeperScoringStrategy(),
                2: DefenderScoringStrategy(),
                3: MidfielderScoringStrategy(),
                4: ForwardScoringStrategy()
            }
            
            batch_data = []
            for row in gw_data:
                row_dict = dict(zip(columns, row[:-1]))
                position_id = row[-1]
                row_dict['gameweek'] = target_gameweek
                
                if random.random() > 0.85:
                    row_dict['goals'] = random.randint(0, 3)
                    row_dict['assists'] = random.randint(0, 2)
                if random.random() > 0.7:
                    row_dict['clean_sheets'] = random.choice([0, 1])
                    row_dict['saves'] = random.randint(0, 7)
                    row_dict['goals_conceded'] = random.randint(0, 4)
                if random.random() > 0.9:
                    row_dict['yellow_cards'] = 1
                    row_dict['red_cards'] = random.choice([0, 1])
                    
                row_dict['ict_index'] += random.uniform(-2.0, 5.0)
                
                strategy = strategies_map.get(position_id, MidfielderScoringStrategy())
                row_dict['total_points'] = strategy.calculate_score(row_dict)
                
                batch_data.append(tuple(row_dict[col] for col in columns[1:]))
                
            c.executemany(insert_query, batch_data)
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to fetch and save: {e}")
        finally:
            conn.close()
        
        bus.publish(Events.GAMEWEEK_DATA_FETCHED, target_gameweek)
        return True
