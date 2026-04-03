import requests
import json

def inspect_api():
    # 1. Get static data to find a player ID
    print("Fetching bootstrap-static...")
    static_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(static_url)
    data = response.json()
    
    # Get a random player (e.g., the one with the highest selected_by_percent to ensure they played)
    elements = data['elements']
    top_player = sorted(elements, key=lambda x: float(x['selected_by_percent']), reverse=True)[0]
    player_id = top_player['id']
    player_name = f"{top_player['first_name']} {top_player['second_name']}"
    
    output = {}
    output['top_player'] = {'name': player_name, 'id': player_id}
    
    # 2. Get detailed summary for that player
    print(f"\nFetching element-summary for {player_name}...")
    summary_url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
    summary_resp = requests.get(summary_url)
    summary_data = summary_resp.json()
    
    if 'history' in summary_data and len(summary_data['history']) > 0:
        latest_history = summary_data['history'][-1]
        output['latest_gameweek_keys'] = list(latest_history.keys())
        output['latest_gameweek_data'] = latest_history
    else:
        output['error'] = "No history found"
        
    with open('research_output.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("Research data saved to research_output.json")

if __name__ == "__main__":
    inspect_api()
