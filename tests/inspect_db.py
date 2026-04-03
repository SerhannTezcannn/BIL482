import sqlite3
import pandas as pd

def inspect():
    conn = sqlite3.connect("fantasy.db")
    
    print("--- Players ---")
    df_players = pd.read_sql_query("SELECT * FROM players LIMIT 5", conn)
    print(df_players)
    
    print("\n--- Stats (Joined) ---")
    query = '''
    SELECT p.first_name, p.second_name, p.team, s.gameweek, s.total_points, s.opponent, s.venue
    FROM stats s
    JOIN players p ON s.player_id = p.id
    LIMIT 10
    '''
    df_stats = pd.read_sql_query(query, conn)
    print(df_stats)
    
    conn.close()

if __name__ == "__main__":
    inspect()
