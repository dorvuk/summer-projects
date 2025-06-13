import praw
import re
from collections import defaultdict
import json
import os
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Canonical character names and their aliases/misspellings
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

# Subreddits to search in
subreddits = ["Deltarune", "Undertale", "deltarunememes", "DeltaruneV2", "UndertaleMemesReddit"]

# Initialize result storage
results = defaultdict(int)
total_posts = 0

# Scrape Reddit
for sub in subreddits:
    print(f"Scraping r/{sub}...")
    for post in reddit.subreddit(sub).top(limit=1000, time_filter='week'):
        total_posts += 1
        content = f"{post.title} {post.selftext or ''}".lower()

        for canonical, aliases in character_aliases.items():
            for alias in aliases:
                # Word-boundary regex to match exact words/phrases
                pattern = r"\b" + re.escape(alias) + r"\b"
                if re.search(pattern, content):
                    results[canonical] += 1
                    break  # Avoid double-counting if multiple aliases match

# Sort results by count
sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

# Add metadata
sorted_results["_meta"] = {"total_posts_scanned": total_posts}

# Save to JSON
with open("reddit_popularity.json", "w") as f:
    json.dump(sorted_results, f, indent=2)

print("Done. Results saved to reddit_popularity.json")
