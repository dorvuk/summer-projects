import requests
import os
from dotenv import load_dotenv
import pycountry
import json
from collections import defaultdict

# Load API keys
load_dotenv()

client_id = os.getenv("OSU_CLIENT_ID")
client_secret = os.getenv("OSU_CLIENT_SECRET")

# Step 1: Get access token
print("Getting token...")
token_data = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials",
    "scope": "public"
}
token_resp = requests.post("https://osu.ppy.sh/oauth/token", json=token_data)
if token_resp.status_code != 200:
    print("Token error:", token_resp.text)
    exit()

access_token = token_resp.json().get("access_token")
print("Token received.\n")

# Step 2: Get rankings
print("📡 Fetching global rankings...")
headers = {"Authorization": f"Bearer {access_token}"}
resp = requests.get("https://osu.ppy.sh/api/v2/rankings/osu/performance", headers=headers)

if resp.status_code != 200:
    print("Ranking fetch error:", resp.text)
    exit()

data = resp.json()
players = data.get("ranking", [])
print(f"Players received: {len(players)}")

if len(players) == 0:
    print("No players in response. Exiting.")
    exit()

# Show full sample of one player
print("\nFirst player object for inspection:")
print(json.dumps(players[0], indent=2))
print("\n")

# Step 3: Process data
country_perf = defaultdict(list)

for player in players:
    user = player.get("user", {})
    username = user.get("username", "Unknown")
    code = user.get("country_code")
    pp = player.get("pp")

    if not code:
        print(f"{username} skipped — no country code")
        continue
    if pp is None:
        print(f"{username} skipped — no PP")
        continue

    try:
        country = pycountry.countries.get(alpha_2=code).name
        country_perf[country].append(pp)
    except:
        print(f"{username} — invalid ISO country code: {code}")
        continue

# Step 4: Check results
if not country_perf:
    print("No valid countries extracted. Exiting.")
    exit()

print("\nCountries included:")
for c in country_perf:
    print(f" - {c} ({len(country_perf[c])} players)")

# Step 5: Average and normalize
averaged = {c: sum(v)/len(v) for c, v in country_perf.items()}
max_score = max(averaged.values())
normalized = {c: round(v / max_score * 100, 2) for c, v in averaged.items()}

# Step 6: Save
with open("osu_country_skill.json", "w") as f:
    json.dump(normalized, f, indent=2)

print("\nosu_country_skill.json saved successfully.")
