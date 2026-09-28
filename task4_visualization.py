import os
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/trends_analysed.csv")
os.makedirs("outputs", exist_ok=True)   # folder for all chart images


def shorten(title, limit=50):
    """Cut titles longer than 50 characters so they fit on the y-axis."""
    if len(title) > limit:
        return title[:limit - 3] + "..."
    return title


# Each chart is a function that draws on a given axis (ax).
# This way I can reuse the same code for the single chart AND the dashboard.

def draw_top_stories(ax):
    # sort by score, take the 10 highest
    top10 = df.sort_values("score", ascending=False).head(10)
    labels = [shorten(t) for t in top10["title"]]
    ax.barh(labels, top10["score"], color="steelblue")
    ax.invert_yaxis()   # barh draws first item at the bottom, so flip it: highest on top
    ax.set_title("Top 10 Stories by Score")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Story title")


def draw_categories(ax):
    counts = df["category"].value_counts()
    colors = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3"]   # one colour per bar
    ax.bar(counts.index, counts.values, color=colors[:len(counts)])
    ax.set_title("Stories per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of stories")
    ax.tick_params(axis="x", rotation=30)


def draw_scatter(ax):
    # split the data using the is_popular column, plot each group with its own colour
    popular = df[df["is_popular"] == True]
    not_popular = df[df["is_popular"] == False]
    ax.scatter(popular["score"], popular["num_comments"], color="green", label="Popular", alpha=0.7)
    ax.scatter(not_popular["score"], not_popular["num_comments"], color="red", label="Not popular", alpha=0.7)
    ax.set_title("Score vs Comments")
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of comments")
    ax.legend()


fig, ax = plt.subplots(figsize=(10, 6))
draw_top_stories(ax)
fig.tight_layout()
plt.savefig("outputs/chart1_top_stories.png")   # savefig first, always
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 6))
draw_categories(ax)
fig.tight_layout()
plt.savefig("outputs/chart2_categories.png")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 6))
draw_scatter(ax)
fig.tight_layout()
plt.savefig("outputs/chart3_scatter.png")
plt.close(fig)

# Bonus: Dashboard (all 3 charts in one figure)
fig, axes = plt.subplots(1, 3, figsize=(24, 7))
draw_top_stories(axes[0])
draw_categories(axes[1])
draw_scatter(axes[2])
fig.suptitle("TrendPulse Dashboard", fontsize=20)
fig.tight_layout()
plt.savefig("outputs/dashboard.png")
plt.close(fig)

print("Charts saved in outputs/ folder:")
for name in sorted(os.listdir("outputs")):
    print(" -", name)