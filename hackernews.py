#!/usr/bin/python
import logging
import argparse
import requests
import html
from bs4 import BeautifulSoup
import json
import os

CACHE_FILE = "cache.json"

# Configure logging: default to INFO, user can override to DEBUG
logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                raw = json.load(f)
                if not isinstance(raw, dict):
                    logger.warning("Cache file is invalid. Initializing empty cache.")
                    return {}
                # Normalize keys to strings (dedupe int/str collisions)
                cache = {}
                for k, v in raw.items():
                    cache[str(k)] = v
                logger.debug("Loaded cache with %d items", len(cache))
                return cache
        except (json.JSONDecodeError, ValueError):
            logger.warning("Cache file is invalid. Initializing empty cache.")
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)
    logger.debug("Saved cache with %d items", len(cache))

def get_newest_item():
    url = "https://hacker-news.firebaseio.com/v0/maxitem.json?print=pretty"
    try:
        response = requests.get(url)
        response.raise_for_status()
        max_item_id = response.json()
        return max_item_id
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching max item ID: %s", e)
        return None

def fetch_item(item_id, cache):
    key = str(item_id)
    if key in cache:
        logger.debug("Using cached data for item %s", item_id)
        return cache[key]

    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json?print=pretty"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        cache[key] = data
        logger.debug("Item %s fetched and added to cache.", item_id)
        return data
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching item %s: %s", item_id, e)
        return None

def find_parent_story(item_id, cache):
    item = fetch_item(item_id, cache)
    if not item:
        return None
    logger.debug("Cache size: %d", len(cache))
    if "parent" in item:
        logger.debug("Item %s is a comment, looking for parent %s", item_id, item['parent'])
        return find_parent_story(item["parent"], cache)
    logger.debug("Item %s is a story.", item_id)
    return item

def sanitize_comment_text(comment_text):
    decoded_text = html.unescape(comment_text)
    soup = BeautifulSoup(decoded_text, 'html.parser')
    for p_tag in soup.find_all('p'):
        p_tag.insert_before('\n\n')
        p_tag.unwrap()
    return soup.get_text()

def print_comments(comments_stack):
    for comment in comments_stack:
        if ("by" in comment) and ("text" in comment):
            print("@"+comment['by'])
            print(sanitize_comment_text(comment['text']))
            print("-----")

def fetch_story_comments(story, cache):
    ids = story.get("kids") or []
    comments = []
    for cid in ids:
        c = fetch_item(cid, cache)
        if c:
            comments.append(c)
    return comments        

def get_newest_story(cache, with_comments=False):
    max_item_id = get_newest_item()
    if not max_item_id:
        logger.error("Could not retrieve newest item ID.")
        return
    story = find_parent_story(max_item_id, cache)
    if not story:
        logger.error("Could not retrieve story for item ID %s", max_item_id)
        return

    print("-----------")
    print(story['title'])
    if "url" in story:
        print(story['url'])
    print("-----------")

    if with_comments:
        comments = fetch_story_comments(story, cache)
        print_comments(comments)

    save_cache(cache)

def main():
    parser = argparse.ArgumentParser(description="HackerNews CLI fetcher")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    subparsers = parser.add_subparsers(dest="command", required=True)

    newest_story_parser = subparsers.add_parser("get_newest_story", help="Get the newest story from HackerNews")
    newest_story_parser.add_argument("--with_comments", action="store_true", help="Print the comments as well")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    cache = load_cache()

    if args.command == "get_newest_story":
        get_newest_story(cache, with_comments=args.with_comments)

    save_cache(cache)

if __name__ == "__main__":
    main()
