from __future__ import annotations

import os
from datetime import datetime, timezone

import praw
from dotenv import load_dotenv

from config import load_config

load_dotenv()


def reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ["REDDIT_USER_AGENT"],
        username=os.getenv("REDDIT_USERNAME"),
    )


def discover(limit: int = 100) -> list[dict]:
    cfg = load_config()
    reddit = reddit_client()
    found: list[dict] = []
    keywords = [k.lower() for k in cfg["keywords"]]

    for subreddit_name in cfg["subreddits"]:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.new(limit=limit):
            text = f"{post.title}\n{post.selftext}".lower()
            matches = [k for k in keywords if k in text]
            if not matches:
                continue
            found.append({
                "reddit_id": post.id,
                "subreddit": subreddit_name,
                "title": post.title,
                "body": post.selftext,
                "author": str(post.author) if post.author else None,
                "permalink": f"https://www.reddit.com{post.permalink}",
                "created_at": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                "matched_keywords": matches,
                "score": post.score,
                "comments": post.num_comments,
            })
    return found


if __name__ == "__main__":
    for item in discover():
        print(item)
