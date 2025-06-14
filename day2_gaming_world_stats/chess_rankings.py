import requests
from collections import defaultdict
import pycountry
import json

headers = { "User-Agent": "summer-gaming-analysis-bot" }
url = "https://api.chess.com/pub/leaderboards"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    raise Exception("Failed to retrieve leaderboard data.")

data = response.json()

modes = ["blitz", "rapid", "bullet", "daily"]
country_scores = defaultdict(list)

for mode in modes:
    print(f"Checking mode: {mode}")
    players = data.get(mode, [])
    if not players:
        print(f"No data for {mode}")
        continue

    for player in players:
        rating = player.get("score", 0)
        country_url = player.get("country", "")
        code = country_url.split("/")[-1]

        try:
            country = pycountry.countries.get(alpha_2=code).name
            country_scores[country].append(rating)
        except:
            continue

# Average across all modes
avg_scores = {
    country: round(sum(ratings) / len(ratings), 2)
    for country, ratings in country_scores.items()
}

# Normalize 0–100
max_score = max(avg_scores.values())
normalized = {
    country: round((score / max_score) * 100, 2)
    for country, score in avg_scores.items()
}

# Save both raw + normalized
with open("chess_country_scores.json", "w") as f:
    json.dump(normalized, f, indent=2)

print("Combined country skill saved.")
