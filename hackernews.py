#!/usr/bin/python
import argparse
import requests
import html
from bs4 import BeautifulSoup

def get_newest_item():
    url = "https://hacker-news.firebaseio.com/v0/maxitem.json?print=pretty"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx/5xx)
    
        max_item_id = response.json()  # Parse the JSON response
        return max_item_id

    except requests.exceptions.RequestException as e:
        print(f"Error fetching max item ID: {e}")
        return None

    
def fetch_item(item_id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json?print=pretty"

    try:
        response = requests.get(url)
        response.raise_for_status()  
        item_data = response.json()  

    except requests.exceptions.RequestException as e:
        print(f"Error fetching item {item_id}: {e}")
        return None

    return item_data
    
def find_parent_story(item_id, fetched_items=None):
    if fetched_items is None:
        fetched_items = []

    item_data = fetch_item(item_id)
    fetched_items.append(item_data)  # Save the fetched item to the stack

    # Check if the "parent" field exists in the data
    if "parent" in item_data:
        # print(f"Item {item_id} is a comment, parent ID: {item_data['parent']}")
        return find_parent_story(item_data['parent'], fetched_items)  # Traverse the parent
        
    else:
        # print(f"Item {item_id} is a story or does not have a parent.")
        return item_data, fetched_items  # Return the story and all fetched items    

def sanitize_comment_text(comment_text):
    decoded_text = html.unescape(comment_text)
    soup = BeautifulSoup(decoded_text, 'html.parser')
    return soup.get_text()

def print_comments(comments_stack):
    for comment in comments_stack:
        if ("by" in comment) and ("text" in comment):
            print("@"+comment['by'])
            print(sanitize_comment_text(comment['text']))
            print("-----")

def fetch_story_comments(story):
    comment_ids = story['kids']

    comments = []
    for id in comment_ids:
        comment = fetch_item(id)
        comments.append(comment)

    return comments
        

def get_newest_story(with_comments=False):
    max_item_id = get_newest_item()
    story, UNUSED = find_parent_story(max_item_id)

    print("-----------")
    print(story['title'])
    if "url" in story:
        print(story['url'])
    print("-----------")

    if with_comments:
        comments = fetch_story_comments(story)
        print_comments(comments)

def main():
    parser = argparse.ArgumentParser(description="HackerNews CLI fetcher")
    subparsers = parser.add_subparsers(dest="command", required=True)

    newest_story_parser = subparsers.add_parser("get_newest_story", help="Get the newest story from HackerNews")
    newest_story_parser.add_argument("--with_comments", action="store_true", help="print the comments as well")

    args = parser.parse_args()

    if args.command == "get_newest_story":
        get_newest_story(with_comments=args.with_comments)
    
if __name__ == "__main__":
    main()
