# Reddit Search Tool

A small, personal command-line script that runs a read-only search against
Reddit and saves the results to a local JSON file.

## What it's for

Before I sit down to write about a topic, I like to know what people are
already saying about it on Reddit, what questions come up, what's already
been covered elsewhere, and what real phrasing people use when they talk
about it. This script does that: give it a search term, it pulls back the
top matching posts across Reddit along with a few top comments on each, and
saves everything to a JSON file I can read through afterward.

It's a manual, run-it-yourself tool. There's no automation, no scheduling,
and nothing that runs in the background.

## What it does and doesn't do

- **Read-only.** It only searches and reads public posts and comments.
- **No account actions.** It never logs in as a Reddit user, and never
  votes, comments, posts, messages, follows, or joins anything. It
  authenticates to Reddit's API as an app, not as a person.
- **Nothing is shared.** Results are saved to a plain JSON file on your own
  machine and go nowhere else.
- **Small and occasional.** Meant to be run by hand, a handful of times a
  week at most, one search at a time.

## Setup

1. Install Python 3.10 or newer.
2. Install the one dependency:
   ```
   pip install -r requirements.txt
   ```
3. Get Reddit API credentials (client ID, client secret, and a user agent
   string) and copy `config.ini.example` to `config.ini`:
   ```
   cp config.ini.example config.ini
   ```
   Then fill in the three values under `[reddit]`.

## Usage

```
python reddit_search.py --query "can't fall asleep"
```

Optional flags:

- `--posts-per-search N` — how many posts to pull (default 25)
- `--output path.json` — where to save the results (default: a filename
  based on the query, in the current folder)

Example:

```
python reddit_search.py --query "budgeting doesn't work" --posts-per-search 15 --output budgeting.json
```

## Output format

Each run writes a JSON file shaped like this:

```json
{
  "query": "can't fall asleep",
  "posts": [
    {
      "title": "...",
      "subreddit": "sleep",
      "permalink": "https://www.reddit.com/r/sleep/comments/...",
      "score": 142,
      "num_comments": 38,
      "top_comments": ["...", "...", "..."]
    }
  ]
}
```
