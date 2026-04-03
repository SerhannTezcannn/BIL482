import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_db_path = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "fantasy.db"))

if os.path.exists(data_db_path):
    DB_NAME = data_db_path
else:
    DB_NAME = os.path.join(BASE_DIR, "fantasy.db")

def create_schema():
    if os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} already exists. Operating on existing schema.")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        c.execute("ALTER TABLE players ADD COLUMN cost REAL")
        print("Migrated 'players' table: Added 'cost' column.")
    except sqlite3.OperationalError:
        pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            second_name TEXT,
            team TEXT,
            position_id INTEGER,
            cost REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            gameweek INTEGER,
            
            opponent TEXT,
            venue TEXT,
            result TEXT,
            
            total_points INTEGER,
            bonus INTEGER,
            ict_index REAL,
            
            goals INTEGER,
            assists INTEGER,
            minutes INTEGER,
            clean_sheets INTEGER,
            goals_conceded INTEGER,
            yellow_cards INTEGER,
            red_cards INTEGER,
            saves INTEGER,
            
            FOREIGN KEY(player_id) REFERENCES players(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            budget_used REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS team_players (
            team_id INTEGER,
            player_id INTEGER,
            is_captain BOOLEAN DEFAULT 0,
            is_bench BOOLEAN DEFAULT 0,
            FOREIGN KEY(team_id) REFERENCES user_teams(id),
            FOREIGN KEY(player_id) REFERENCES players(id)
        )
    ''')
    
    try:
        c.execute("ALTER TABLE team_players ADD COLUMN is_bench BOOLEAN DEFAULT 0")
        print("Migrated 'team_players' table: Added 'is_bench' column.")
    except sqlite3.OperationalError:
        pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS gameweeks (
            id INTEGER PRIMARY KEY,
            name TEXT,
            deadline_time TEXT,
            is_current BOOLEAN
        )
    ''')

    conn.commit()
    conn.close()
    print("Database schema created successfully.")

if __name__ == "__main__":
    create_schema()
