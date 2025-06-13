import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Load all 3 JSON files
with open("reddit_popularity.json") as f:
    reddit_data = json.load(f)
    reddit_data.pop("_meta", None)

with open("youtube_recent_popularity.json") as f:
    youtube_data = json.load(f)

with open("google_trends_popularity.json") as f:
    trends_data = json.load(f)

# Combine into a single DataFrame
characters = list(set(reddit_data) | set(youtube_data) | set(trends_data))
df = pd.DataFrame(index=characters)
df["reddit"] = pd.Series(reddit_data)
df["youtube"] = pd.Series(youtube_data)
df["trends"] = pd.Series(trends_data)

# Fill missing values with 0 (some characters don't exist in all sources)
df = df.fillna(0)

# Normalize each column to 0–1 range
scaler = MinMaxScaler()
df[["reddit_scaled", "youtube_scaled", "trends_scaled"]] = scaler.fit_transform(df[["reddit", "youtube", "trends"]])

# Weighted sum
df["popularity_score"] = (
    df["reddit_scaled"] * 0.4 +
    df["youtube_scaled"] * 0.3 +
    df["trends_scaled"] * 0.3
)

# Sort
df = df.sort_values("popularity_score", ascending=False)

# Save to JSON
df[["popularity_score"]].to_json("combined_popularity.json", indent=2)

# --- Visualization ---
top_n = 15
top_df = df.head(top_n)

plt.figure(figsize=(12, 7))
bars = plt.bar(top_df.index, top_df["popularity_score"], color="skyblue")
plt.title("Deltarune Character Popularity Score After Ch3+Ch4 Release", fontsize=16)
plt.ylabel("Popularity Score (0–1)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

# Add values above bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f"{yval:.2f}", ha='center', fontsize=9)

plt.savefig("popularity_chart.png", dpi=300)
plt.show()
