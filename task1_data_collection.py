import requests
import time
import json
import os
from datetime import datetime

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
BEST_STORIES_URL = "https://hacker-news.firebaseio.com/v0/beststories.json"
NEW_STORIES_URL = "https://hacker-news.firebaseio.com/v0/newstories.json"
ITEM_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{}.json"

HEADERS = {"User-Agent": "TrendPulse/1.0"}

MAX_STORY_IDS_TO_FETCH = 500
MAX_STORIES_PER_CATEGORY = 25
MAX_RETRIES = 3          # how many times to try one request before giving up
TIMEOUT_SECONDS = 10     # don't wait forever for one request

CATEGORY_KEYWORDS = {
    "technology": ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews": ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports": ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "game", "book", "show", "award", "streaming"],
}

# one session reuses the same connection, so fewer connection resets
session = requests.Session()
session.headers.update(HEADERS)

story_cache = {}


def fetch_json(url):
    """GET a url and return parsed JSON. Retries a few times, returns None if all fail."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt}/{MAX_RETRIES}) for {url}: {e}")
            time.sleep(1)   # short pause only after a failure, then retry
    return None


def get_story_ids():
    """Top stories first, then best and new stories added (duplicates removed)."""
    story_ids = []
    seen = set()

    for url in [TOP_STORIES_URL, BEST_STORIES_URL, NEW_STORIES_URL]:
        ids = fetch_json(url)
        if ids is None:
            continue
        for story_id in ids[:MAX_STORY_IDS_TO_FETCH]:
            if story_id not in seen:
                seen.add(story_id)
                story_ids.append(story_id)

    return story_ids


def get_story_details(story_id):
    """Fetch one story, using the cache so each story is requested only once."""
    if story_id in story_cache:
        return story_cache[story_id]

    story_data = fetch_json(ITEM_URL_TEMPLATE.format(story_id))
    story_cache[story_id] = story_data   # cache even failures so we don't retry forever
    return story_data


def title_matches_category(title, category):
    if not title:
        return False
    title_lower = title.lower()
    for keyword in CATEGORY_KEYWORDS[category]:
        if keyword in title_lower:
            return True
    return False


def collect_stories():
    story_ids = get_story_ids()

    if not story_ids:
        print("No story IDs were fetched. Exiting.")
        return []

    print(f"Scanning {len(story_ids)} story IDs...")
    collected_stories = []

    for category in CATEGORY_KEYWORDS:
        print(f"Collecting stories for category: {category}")
        count_for_this_category = 0

        for story_id in story_ids:
            if count_for_this_category >= MAX_STORIES_PER_CATEGORY:
                break

            story = get_story_details(story_id)

            if story is None or "title" not in story:
                continue

            if title_matches_category(story["title"], category):
                collected_stories.append({
                    "post_id": story.get("id"),
                    "title": story.get("title"),
                    "category": category,
                    "score": story.get("score", 0),
                    "num_comments": story.get("descendants", 0),
                    "author": story.get("by", "unknown"),
                    "collected_at": datetime.now().isoformat(),
                })
                count_for_this_category += 1

        print(f"  -> Found {count_for_this_category} stories for {category}")
        time.sleep(2)   # one sleep per category, not per story

    return collected_stories


def save_to_json(stories):
    os.makedirs("data", exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d")
    file_path = f"data/trends_{today_str}.json"

    with open(file_path, "w") as f:
        json.dump(stories, f, indent=2)

    print(f"Collected {len(stories)} stories. Saved to {file_path}")


if __name__ == "__main__":
    stories = collect_stories()
    save_to_json(stories)