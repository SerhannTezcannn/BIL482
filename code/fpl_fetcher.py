import requests
import json
import csv
import time
import os

class FPLFetcher:
    def __init__(self):
        self.base_url = "https://fantasy.premierleague.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def get_bootstrap_static(self):
        print("Fetching bootstrap-static...")
        r = self.session.get(f"{self.base_url}/bootstrap-static/")
        r.raise_for_status()
        return r.json()

    def get_player_summary(self, player_id):
        time.sleep(0.05) 
        r = self.session.get(f"{self.base_url}/element-summary/{player_id}/")
        if r.status_code != 200:
            print(f"Error fetching player {player_id}: {r.status_code}")
            return None
        return r.json()

    def fetch_weekly_data(self, target_gameweek=None):
        static_data = self.get_bootstrap_static()
        
        events = static_data['events']
        current_event = next((e for e in events if e['is_current']), None)
        
        if target_gameweek:
            gw_id = target_gameweek
            print(f"Targeting Gameweek: {gw_id}")
        elif current_event:
            gw_id = current_event['id']
            print(f"Targeting Current Gameweek: {gw_id}")
        else:
            gw_id = events[-1]['id'] if events else 1
            print(f"Defaulting to: {gw_id}")

        teams = {t['id']: t['name'] for t in static_data['teams']}
        
        players = static_data['elements']
        print(f"Found {len(players)} players. Fetching details...")
        
        processed_data = []
        count = 0
        total = len(players)
        
        for p in players:
            p_id = p['id']
            p_name = f"{p['first_name']} {p['second_name']}"
            team_name = teams.get(p['team'], "Unknown")
            
            summary = self.get_player_summary(p_id)
            if not summary or 'history' not in summary:
                continue

            gw_stats = next((h for h in summary['history'] if h['round'] == gw_id), None)
            
            if gw_stats:
                opponent_id = gw_stats['opponent_team']
                opponent_name = teams.get(opponent_id, f"ID_{opponent_id}")
                is_home = gw_stats['was_home']
                venue = "Home" if is_home else "Away"
                score = f"{gw_stats['team_h_score']}-{gw_stats['team_a_score']}"
                ict = gw_stats['ict_index']
                
                cost = p['now_cost'] / 10.0

                row = {
                    "ID": p_id,
                    "Name": p_name,
                    "Team": team_name,
                    "Position": p['element_type'],
                    "Cost": cost,
                    "Gameweek": gw_id,
                    
                    "Opponent": opponent_name,
                    "Venue": venue,
                    "Score (H-A)": score,
                    "Result": "N/A",

                    "Total Points": gw_stats['total_points'],
                    "Bonus Points": gw_stats['bonus'],
                    "ICT Index": ict,
                    "FDR (Difficulty)": "N/A",

                    "Goals": gw_stats['goals_scored'],
                    "Assists": gw_stats['assists'],
                    "Shots": "N/A",
                    "Shot Accuracy": "N/A",
                    "Threat": gw_stats['threat'],
                    "Creativity": gw_stats['creativity'],
                    "Influence": gw_stats['influence'],
                    
                    "Yellow Cards": gw_stats['yellow_cards'],
                    "Red Cards": gw_stats['red_cards'],
                    
                    "Clean Sheets": gw_stats['clean_sheets'],
                    "Goals Conceded": gw_stats['goals_conceded'],
                    "Saves": gw_stats['saves'],
                    "Own Goals": gw_stats['own_goals'],
                    
                    "Minutes": gw_stats['minutes'],
                    "Starts": gw_stats['starts'],
                }
                
                processed_data.append(row)
            
            count += 1
            if count % 50 == 0:
                print(f"Processed {count}/{total} players...", flush=True)

        return processed_data, gw_id

    def save_to_csv(self, data, gameweek):
        if not data:
            print("No data collected.")
            return

        filename = f"fpl_stats_gw{gameweek}.csv"
        keys = data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
            
        print(f"\nSuccess! Data saved to {filename}")
        print(f"Total records: {len(data)}")

    def save_to_db(self, data, gameweek):
        import sqlite3
        if not data:
            return

        print(f"\nSaving {len(data)} records to database 'fantasy.db'...")
        conn = sqlite3.connect("fantasy.db")
        c = conn.cursor()
        
        for row in data:
            c.execute('''
                INSERT OR REPLACE INTO players (id, first_name, second_name, team, position_id, cost)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['ID'], row['Name'].split()[0], " ".join(row['Name'].split()[1:]), row['Team'], row['Position'], row['Cost']))
            
            c.execute('''
                INSERT INTO stats (
                    player_id, gameweek, opponent, venue, result,
                    total_points, bonus, ict_index,
                    goals, assists, minutes, clean_sheets, goals_conceded,
                    yellow_cards, red_cards, saves
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['ID'], gameweek, row['Opponent'], row['Venue'], row['Score (H-A)'],
                row['Total Points'], row['Bonus Points'], row['ICT Index'],
                row['Goals'], row['Assists'], row['Minutes'], row['Clean Sheets'],
                row['Goals Conceded'], row['Yellow Cards'], row['Red Cards'], row['Saves']
            ))
            
        conn.commit()
        conn.close()
        print("Database update complete.")

if __name__ == "__main__":
    fetcher = FPLFetcher()
    data, gw = fetcher.fetch_weekly_data()
    fetcher.save_to_csv(data, gw)
    fetcher.save_to_db(data, gw)
