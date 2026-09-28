import glob
import os
import pandas as pd


json_files = sorted(glob.glob("data/trends_*.json"))
if not json_files:
    print("No JSON file found in data/ folder. Run task1 first.")
    raise SystemExit

json_path = json_files[-1]   # sorted by name, so last = newest date

# ---------- 1. Load the JSON file ----------
df = pd.read_json(json_path)
print(f"Loaded {len(df)} stories from {json_path}")

# ---------- 2. Clean the data ----------

# Duplicates: same post_id can appear twice (e.g. a title matching two categories)
df = df.drop_duplicates(subset="post_id")
print(f"After removing duplicates: {len(df)}")

# Missing values: drop rows where post_id, title or score is missing
df = df.dropna(subset=["post_id", "title", "score"])
print(f"After removing nulls: {len(df)}")

# Data types: num_comments can be missing for stories with no comments,
# so I fill it with 0 first, then convert both columns to integers
df["num_comments"] = df["num_comments"].fillna(0)
df["score"] = df["score"].astype(int)
df["num_comments"] = df["num_comments"].astype(int)

# Low quality: keep only stories with score of 5 or more
df = df[df["score"] >= 5]
print(f"After removing low scores: {len(df)}")

# Whitespace: remove extra spaces at the start and end of titles
df["title"] = df["title"].str.strip()

print(f"Rows remaining after cleaning: {len(df)}")

# ---------- 3. Save as CSV ----------
os.makedirs("data", exist_ok=True)
csv_path = "data/trends_clean.csv"
df.to_csv(csv_path, index=False)   # index=False so no extra number column is saved
print(f"Saved {len(df)} rows to {csv_path}")

# Quick summary: how many stories per category
print("\nStories per category:")
print(df["category"].value_counts())
