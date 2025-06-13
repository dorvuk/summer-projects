from googleapiclient.discovery import build
import json
from collections import defaultdict
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Canonical structure
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

results = defaultdict(int)

# Filter by recent 30 days
published_after = (datetime.now() - timedelta(days=30)).isoformat("T") + "Z"

print(f"Filtering for videos published after: {published_after}\n")

for canonical, aliases in character_aliases.items():
    total_views = 0
    for alias in aliases:
        query = f"{alias} deltarune"
        print(f"🔍 Searching: {query} → {canonical}")

        try:
            search_response = youtube.search().list(
                q=query,
                part='id',
                type='video',
                maxResults=25,
                publishedAfter=published_after
            ).execute()

            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

            if not video_ids:
                print(f"No recent videos for: {alias}")
                continue

            video_response = youtube.videos().list(
                part='statistics,snippet',
                id=','.join(video_ids)
            ).execute()

            for video in video_response.get("items", []):
                title = video['snippet']['title']
                views = int(video['statistics'].get('viewCount', 0))
                print(f"   🎬 {title} — {views} views")
                total_views += views

            time.sleep(1)

        except Exception as e:
            print(f"Error on alias '{alias}': {e}")

    print(f"Total recent views for {canonical}: {total_views}\n")
    results[canonical] += total_views

# Sort + save
sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

with open("youtube_recent_popularity.json", "w") as f:
    json.dump(sorted_results, f, indent=2)

print("Saved recent YouTube popularity to youtube_recent_popularity.json")
