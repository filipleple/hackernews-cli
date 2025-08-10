# Hacker News CLI Fetcher

This is a simple Python command-line tool for fetching the newest Hacker News story via the [Hacker News API](https://github.com/HackerNews/API).
It can optionally display the story's top-level comments.
Results are cached locally to avoid repeated API calls for the same item.

## Features

* Fetches the newest story ID from Hacker News.
* Recursively resolves comment chains back to the original story.
* Optionally prints top-level comments for that story.
* Caches all fetched items in a JSON file (`cache.json`) so they are only fetched once.
* Debug output using Python’s built-in `logging` module, toggleable with `--debug`.

## Requirements

* Python 3.7+
* The following Python packages:

  * `requests`
  * `beautifulsoup4`

Install dependencies with:

```bash
pip install requests beautifulsoup4
```

## Usage

### Fetch newest story

```bash
python hn.py get_newest_story
```

Example output:

```
-----------
Zig's Lovely Syntax
https://matklad.github.io/2025/08/09/zigs-lovely-syntax.html
-----------
```

### Fetch newest story with top-level comments

```bash
python hn.py get_newest_story --with_comments
```

Example output:

```
-----------
Zig's Lovely Syntax
https://matklad.github.io/2025/08/09/zigs-lovely-syntax.html
-----------
@username
This is a comment...
-----
@anotheruser
Another comment...
-----
```

### Enable debug output

By default, only essential output is shown. Use `--debug` to see all debug logs:

```bash
python hn.py --debug get_newest_story --with_comments
```

Debug logs include:

* When an item is fetched vs. read from cache
* Cache size after updates
* Parent/child item resolution

### Cache

The tool stores all fetched items in `cache.json` in the current directory.
Keys are string item IDs to avoid int/str collisions.

You can safely delete `cache.json` at any time to start with a fresh cache.

## Command Reference

```
usage: hn.py [-h] [--debug] {get_newest_story} ...

HackerNews CLI fetcher

positional arguments:
  {get_newest_story}   Commands
    get_newest_story   Get the newest story from HackerNews

options:
  -h, --help           Show help message and exit
  --debug              Enable debug output
```

## API Reference

* **Newest item**: `https://hacker-news.firebaseio.com/v0/maxitem.json`
* **Item details**: `https://hacker-news.firebaseio.com/v0/item/<id>.json`
