from __future__ import annotations

from urllib.parse import urlencode


def tracked_url(base_url: str, *, subreddit: str, campaign: str, content: str) -> str:
    separator = '&' if '?' in base_url else '?'
    query = urlencode({
        'utm_source': 'reddit',
        'utm_medium': 'organic',
        'utm_campaign': campaign,
        'utm_content': content,
        'reddit_subreddit': subreddit,
    })
    return f"{base_url}{separator}{query}"
