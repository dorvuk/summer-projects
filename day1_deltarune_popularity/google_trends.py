from pytrends.request import TrendReq
import pandas as pd
import json
import time

# Google Trends connection
pytrends = TrendReq(hl='en-US', tz=360)

# Canonical character names
character_aliases = {
    "Kris": ["kris"],
    "Susie": ["susie"],
    "Ralsei": ["ralsei"],
    "Noelle": ["noelle"],
    "Asgore": ["asgore"],
    "Sans": ["sans"],
    "Toriel": ["toriel"],
    "Dess": ["dess", "december"],
    "Carol": ["carol"],
    "Asriel": ["asriel"],
    "Queen": ["queen"],
    "King": ["king"],
    "Roaring Knight": ["roaring knight", "the knight", "knight"],
    "Jevil": ["jevil"],
    "Spamton": ["spamton", "spamton g", "spamton g spamton", "spamton neo"],
    "Garson": ["garson", "gerson"],
    "Tenna": ["tenna"],
    "Papyrus": ["papyrus"],
    "Undyne": ["undyne"],
    "Alphys": ["alphys"],
    "Gaster": ["gaster", "w.d. gaster", "wd gaster", "w. d. gaster"]
}

# Use only the canonical names as search terms
characters = list(character_aliases.keys())

# Output data
results = {}

# Google only lets 5 terms per call
def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

print("Fetching Google Trends data...")

for group in chunk(characters, 5):
    pytrends.build_payload(group, timeframe='now 7-d')
    data = pytrends.interest_over_time()
    if not data.empty:
        for char in group:
            avg = int(data[char].mean())
            results[char] = avg
    time.sleep(1)  # avoid throttling

# Sort and save
sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
with open("google_trends_popularity.json", "w") as f:
    json.dump(sorted_results, f, indent=2)

print("Google Trends popularity saved to google_trends_popularity.json")
