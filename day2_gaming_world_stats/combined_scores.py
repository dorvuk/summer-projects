import json
import os
from collections import defaultdict
import pycountry

# Load game score files
with open("chess_country_scores.json") as f:
    chess = json.load(f)
with open("csgo_country_skill.json") as f:
    csgo = json.load(f)
with open("lol_country_skill.json") as f:
    lol = json.load(f)
with open("osu_country_skill.json") as f:
    osu = json.load(f)

# Expand LoL regions to countries
region_map = {
    "na1": ["US", "CA"],
    "euw1": ["GB", "FR", "DE", "IT", "ES", "NL", "PT", "BE", "AT", "CH", "SE", "FI", "DK", "NO", "IE"],
    "eun1": ["PL", "CZ", "SK", "HU", "RO", "BG", "RS", "HR", "SI", "LT", "LV", "EE", "UA"],
    "kr": ["KR"],
    "br1": ["BR"],
    "la1": ["MX"],
    "la2": ["AR", "CL", "CO", "PE"],
    "tr1": ["TR"],
    "ru": ["RU"],
    "oc1": ["AU", "NZ"],
    "jp1": ["JP"]
}

lol_country_expanded = {}
for region, score in lol.items():
    countries = region_map.get(region.lower(), [])
    for c in countries:
        lol_country_expanded[c] = score

# Merge all data by ISO2 country code
game_datasets = [chess, csgo, osu, lol_country_expanded]
country_scores = defaultdict(list)

# Convert full country names to ISO2
def get_iso2(name):
    try:
        return pycountry.countries.lookup(name).alpha_2
    except:
        return None

for dataset in game_datasets:
    for name, score in dataset.items():
        code = get_iso2(name) if len(name) > 2 else name.upper()
        if code:
            country_scores[code].append(score)

# Collect all country codes globally
all_country_codes = {country.alpha_2 for country in pycountry.countries}

# Average scores
averaged_scores = {
    code: sum(scores) / len(scores)
    for code, scores in country_scores.items()
}

# Normalize
if averaged_scores:
    max_val = max(averaged_scores.values())
    normalized = {
        code: round(score / max_val * 100, 2)
        for code, score in averaged_scores.items()
    }
else:
    normalized = {}

# Fill missing with "N/A"
final_scores = {code: normalized.get(code, "N/A") for code in all_country_codes}

# Convert back to full names
final_named = {}
for code, score in final_scores.items():
    country = pycountry.countries.get(alpha_2=code)
    if country:
        final_named[country.name] = score

# Save result
with open("combined_normalized_scores.json", "w") as f:
    json.dump(final_named, f, indent=2)

print("✅ combined_normalized_scores.json saved.")
