"""reddit_search.py

Runs a single read-only Reddit search and saves the results (post titles,
permalinks, scores, and a few top comments per post) to a local JSON file.

Used as part of a personal content-research workflow: given a topic I'm
considering, this tells me what's already being discussed about it on
Reddit, so I can spot gaps and pull real, quotable phrasing instead of
guessing.

Usage:
    python reddit_search.py --query "sleep before a big day" --posts-per-search 25

Credentials are read from config.ini (see config.ini.example). No Reddit
username or password is ever used, PRAW authenticates as an app only and
runs entirely read-only: this script never posts, comments, votes, follows,
or otherwise writes anything back to Reddit.
"""

import argparse
import configparser
import json
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.ini")

TOP_COMMENTS_PER_POST = 3
COMMENT_SNIPPET_MAX_CHARS = 500


def load_config():
    parser = configparser.ConfigParser()
    if not CONFIG_PATH.exists():
        print(
            f"ERROR: {CONFIG_PATH.name} not found. Copy config.ini.example to "
            "config.ini and fill in your Reddit API credentials first.",
            file=sys.stderr,
        )
        sys.exit(1)
    parser.read(CONFIG_PATH)
    section = parser["reddit"]
    return {
        "client_id": section.get("client_id", ""),
        "client_secret": section.get("client_secret", ""),
        "user_agent": section.get("user_agent", ""),
    }


def collect_top_comments(submission) -> list:
    submission.comment_sort = "top"
    submission.comments.replace_more(limit=0)
    snippets = []
    for comment in submission.comments[:TOP_COMMENTS_PER_POST]:
        body = (getattr(comment, "body", "") or "").strip()
        if not body or comment.author is None:
            continue
        snippets.append(body[:COMMENT_SNIPPET_MAX_CHARS])
    return snippets


def run_search(reddit, query: str, posts_per_search: int) -> list:
    posts = []
    for submission in reddit.subreddit("all").search(query, limit=posts_per_search, sort="relevance"):
        posts.append({
            "title": submission.title,
            "subreddit": str(submission.subreddit),
            "permalink": f"https://www.reddit.com{submission.permalink}",
            "score": submission.score,
            "num_comments": submission.num_comments,
            "top_comments": collect_top_comments(submission),
        })
    return posts


def main():
    arg_parser = argparse.ArgumentParser(description="Read-only Reddit search, saved to a local JSON file.")
    arg_parser.add_argument("--query", required=True, help="Search terms, e.g. \"can't fall asleep\"")
    arg_parser.add_argument("--posts-per-search", type=int, default=25, help="Max number of posts to pull (default 25)")
    arg_parser.add_argument("--output", default=None, help="Output file path (default: <query>.json in the current folder)")
    args = arg_parser.parse_args()

    config = load_config()
    if not config["client_id"] or not config["client_secret"] or not config["user_agent"]:
        print("ERROR: client_id, client_secret, and user_agent must all be set in config.ini", file=sys.stderr)
        sys.exit(1)

    try:
        import praw
    except ImportError:
        print("ERROR: praw is not installed. Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    reddit = praw.Reddit(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        user_agent=config["user_agent"],
    )

    print(f"Searching Reddit for: {args.query!r} (up to {args.posts_per_search} posts)...")
    posts = run_search(reddit, args.query, args.posts_per_search)

    output_path = Path(args.output) if args.output else Path(f"{args.query.replace(' ', '_')}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"query": args.query, "posts": posts}, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(posts)} results to {output_path}")


if __name__ == "__main__":
    main()
