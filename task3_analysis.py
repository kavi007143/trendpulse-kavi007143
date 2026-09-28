import numpy as np
import pandas as pd

df = pd.read_csv("data/trends_clean.csv")

print(f"Loaded data: {df.shape}")
print("\nFirst 5 rows:")
print(df.head())

# pandas mean() for the quick overview
print(f"\nAverage score   : {df['score'].mean():.0f}")
print(f"Average comments: {df['num_comments'].mean():.0f}")

# convert the columns to numpy arrays so numpy functions can be used
scores = df["score"].to_numpy()

print("\n--- NumPy Stats ---")
print(f"Mean score   : {np.mean(scores):.0f}")
print(f"Median score : {np.median(scores):.0f}")
print(f"Std deviation: {np.std(scores):.0f}")
print(f"Max score    : {np.max(scores)}")
print(f"Min score    : {np.min(scores)}")

# category with the most stories (value_counts is sorted, so first = highest)
category_counts = df["category"].value_counts()
top_category = category_counts.index[0]
print(f"\nMost stories in: {top_category} ({category_counts.iloc[0]} stories)")

# story with the most comments: argmax gives the position of the biggest value
comments = df["num_comments"].to_numpy()
top_index = np.argmax(comments)
print(f"\nMost commented story: \"{df['title'].iloc[top_index]}\" - {comments[top_index]} comments")

# engagement = comments per upvote (+1 avoids dividing by zero)
df["engagement"] = df["num_comments"] / (df["score"] + 1)

# is_popular = True when the story's score is above the average score
avg_score = df["score"].mean()
df["is_popular"] = df["score"] > avg_score

output_path = "data/trends_analysed.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved to {output_path}")