import requests

# Create a valid 15-man squad test payload
TEAM_DATA = {
    "name": "API Validated All Stars",
    "player_ids": [
        1, 19, # GKs
        5, 6, 8, 26, 28, # DEFs
        16, 17, 18, 20, 21, # MIDs
        10, 11, 48  # FWDs
    ]
}

response = requests.post("http://127.0.0.1:8080/team", json=TEAM_DATA)
print(f"Status Code: {response.status_code}")
try:
    print(response.json())
except Exception as e:
    print(response.text)
