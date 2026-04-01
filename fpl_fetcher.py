import requests
import json
import csv
import time
import os

class FPLFetcher:
    def __init__(self):
        self.base_url = "https://fantasy.premierleague.com/api"
        self.session = requests.Session()
        # Set User-Agent headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def get_bootstrap_static(self):
        """Fetch general data: teams, gameweeks (events), players (elements)."""
        print("Fetching bootstrap-static...")
        r = self.session.get(f"{self.base_url}/bootstrap-static/")
        r.raise_for_status()
        return r.json()

    def get_player_summary(self, player_id):
        """Fetch detailed stats for a specific player."""
        # Rate limiting: polite pause
        time.sleep(0.05) 
        r = self.session.get(f"{self.base_url}/element-summary/{player_id}/")
        if r.status_code != 200:
            print(f"Error fetching player {player_id}: {r.status_code}")
            return None
        return r.json()

    def fetch_weekly_data(self, target_gameweek=None):
        static_data = self.get_bootstrap_static()
        
        # 1. Determine current/target gameweek
        events = static_data['events']
        current_event = next((e for e in events if e['is_current']), None)
        
        if target_gameweek:
            gw_id = target_gameweek
            print(f"Targeting Gameweek: {gw_id} (User Specified)")
        elif current_event:
            gw_id = current_event['id']
            print(f"Targeting Current Gameweek: {gw_id}")
        else:
            # Fallback if season finished or between seasons
            gw_id = events[-1]['id'] if events else 1
            print(f"No current gameweek found. Defaulting to: {gw_id}")

        # 2. Map Team IDs to Names
        teams = {t['id']: t['name'] for t in static_data['teams']}
        
        # 3. Process Players
        players = static_data['elements']
        print(f"Found {len(players)} players. Starting detailed fetch...")
        
        processed_data = []
        
        count = 0
        total = len(players)
        
        for p in players:
            p_id = p['id']
            p_name = f"{p['first_name']} {p['second_name']}"
            team_name = teams.get(p['team'], "Unknown")
            
            # Fetch details
            summary = self.get_player_summary(p_id)
            if not summary or 'history' not in summary:
                continue

            # Find stats for the specific gameweek
            gw_stats = next((h for h in summary['history'] if h['round'] == gw_id), None)
            
            if gw_stats:
                # Resolve Match Context
                opponent_id = gw_stats['opponent_team']
                opponent_name = teams.get(opponent_id, f"ID_{opponent_id}")
                is_home = gw_stats['was_home']
                venue = "Home" if is_home else "Away"
                score = f"{gw_stats['team_h_score']}-{gw_stats['team_a_score']}"

                # Calculate ICT Index (Influence, Creativity, Threat)
                # API provides these as strings, sometimes blank?
                ict = gw_stats['ict_index']
                
                # Cost (Price) - API gives it as int (e.g. 125 = 12.5)
                cost = p['now_cost'] / 10.0

                # Map API fields to User Requirements
                row = {
                    "ID": p_id,
                    "Name": p_name,
                    "Team": team_name,
                    "Position": p['element_type'], # 1=GKP, 2=DEF, 3=MID, 4=FWD
                    "Cost": cost,
                    "Gameweek": gw_id,
                    
                    # Match Context
                    "Opponent": opponent_name,
                    "Venue": venue,
                    "Score (H-A)": score,
                    "Result": "N/A", # Logic to determine W/D/L is complex without knowing own team ID vs H/A

                    # Fantasy Metrics
                    "Total Points": gw_stats['total_points'],
                    "Bonus Points": gw_stats['bonus'],
                    "ICT Index": ict,
                    "FDR (Difficulty)": "N/A", # Often on 'fixture' endpoint, simplified here

                    # Attack
                    "Goals": gw_stats['goals_scored'],
                    "Assists": gw_stats['assists'],
                    "Shots": "N/A", # Not available in API
                    "Shot Accuracy": "N/A", # Not available in API
                    "Threat": gw_stats['threat'],
                    "Creativity": gw_stats['creativity'],
                    "Influence": gw_stats['influence'],
                    
                    # Discipline
                    "Yellow Cards": gw_stats['yellow_cards'],
                    "Red Cards": gw_stats['red_cards'],
                    
                    # Defense
                    "Clean Sheets": gw_stats['clean_sheets'],
                    "Goals Conceded": gw_stats['goals_conceded'],
                    "Saves": gw_stats['saves'],
                    "Own Goals": gw_stats['own_goals'],
                    
                    # Time
                    "Minutes": gw_stats['minutes'],
                    "Starts": gw_stats['starts'],
                }
                
                processed_data.append(row)
            
            count += 1
            if count % 50 == 0:
                print(f"Processed {count}/{total} players...")

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
        
        # 1. Upsert Players (Clean way: Replace or Ignore)
        # We need to ensure player exists before adding stats
        for row in data:
            # Insert Player (Replace to update cost)
            c.execute('''
                INSERT OR REPLACE INTO players (id, first_name, second_name, team, position_id, cost)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['ID'], row['Name'].split()[0], " ".join(row['Name'].split()[1:]), row['Team'], row['Position'], row['Cost']))
            
            # Insert Stats
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
