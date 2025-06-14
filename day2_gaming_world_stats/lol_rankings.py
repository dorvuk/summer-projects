import os
import requests
import json
from time import sleep
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

headers = {
    "X-Riot-Token": API_KEY
}

regions = [
    "na1", "euw1", "eun1", "kr", "br1", "jp1", "ru", "tr1", "oc1",
    "la1", "la2", "ph2", "sg2", "th2", "tw2", "vn2"
]

tiers = [
    "IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND",
    "MASTER", "GRANDMASTER", "CHALLENGER"
]

divisions = ["IV", "III", "II", "I"]

country_counts = defaultdict(int)

def fetch_entries(region, tier, division=None, page=1):
    if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
        url = f"https://{region}.api.riotgames.com/lol/league/v4/{tier.lower()}leagues/by-queue/RANKED_SOLO_5x5"
    else:
        url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}?page={page}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 403:
            print(f"403 Forbidden at {region} {tier} {division} page {page}")
            return None
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {region} {tier} {division} page {page}: {e}")
        return None

print("Starting Riot scraper...")

for region in regions:
    print(f"Region: {region}")
    for tier in tiers:
        applicable_divs = divisions if tier in ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND"] else [None]
        for div in applicable_divs:
            if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
                data = fetch_entries(region, tier)
                if not data or "entries" not in data:
                    continue
                for entry in data["entries"]:
                    country_counts[region] += 1
                sleep(1.2)
            else:
                for page in range(1, 6):
                    data = fetch_entries(region, tier, div, page)
                    if not data:
                        break
                    for entry in data:
                        country_counts[region] += 1
                    sleep(1.2)

# Normalize
max_val = max(country_counts.values()) if country_counts else 1
normalized = {region: round(count / max_val * 100, 2) for region, count in country_counts.items()}

with open("lol_country_skill.json", "w") as f:
    json.dump(normalized, f, indent=2)

print("Done. Saved to lol_country_skill.json")
