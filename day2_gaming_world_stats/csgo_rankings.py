import requests
import os
import json
from dotenv import load_dotenv
from collections import defaultdict
import pycountry

load_dotenv()
API_KEY = os.getenv("FACEIT_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
BASE_URL = "https://open.faceit.com/data/v4"
REGIONS = ["EU", "NA", "SA", "AS", "AF", "OC", "SEA"]

elo_data = defaultdict(list)

for region in REGIONS:
    try:
        url = f"{BASE_URL}/rankings/games/csgo/regions/{region}?limit=100"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json().get("items", [])
        for player in data:
            country = player.get("country")
            elo = player.get("faceit_elo")
            if country and elo:
                elo_data[country.upper()].append(elo)
    except Exception as e:
        print(f"Error fetching region {region}: {e}")

# Compute average ELO per country
averages = {country: sum(elos)/len(elos) for country, elos in elo_data.items() if elos}
max_elo = max(averages.values(), default=1)
normalized = {country: round((elo / max_elo) * 100, 2) for country, elo in averages.items()}

# Optional: Convert country codes to full country names
named = {}
for code, score in normalized.items():
    country = pycountry.countries.get(alpha_2=code)
    named[country.name if country else code] = score

# Save output
with open("csgo_country_skill.json", "w") as f:
    json.dump(named, f, indent=2)

print("Saved csgo_country_skill.json with", len(named), "countries.")
