from __future__ import annotations

"""Collect posts from X/Twitter using snscrape."""

import json
import subprocess
import sys
from datetime import datetime

import pandas as pd

SCHEMA = [
    "post_id",
    "platform",
    "handle",
    "url",
    "datetime",
    "text",
    "media_type",
    "hashtags",
    "likes",
    "comments",
    "shares",
    "views",
    "followers_at_post",
    "author_name",
    "author_id",
    "is_competitor",
]


def collect_x(handle: str, since: datetime, *, is_competitor: bool = False) -> pd.DataFrame:
    """Collect tweets for ``handle`` since ``since`` date."""
    cmd = [
        sys.executable,
        "-m",
        "snscrape",
        "--jsonl",
        "twitter-search",
        f"from:{handle} since:{since:%Y-%m-%d}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    rows = []
    for line in proc.stdout.splitlines():
        try:
            data = json.loads(line)
        except Exception:
            continue
        rows.append(
            {
                "post_id": data.get("id"),
                "platform": "x",
                "handle": handle,
                "url": data.get("url"),
                "datetime": data.get("date"),
                "text": data.get("content"),
                "media_type": (data.get("media") or [{}])[0].get("type") if data.get("media") else None,
                "hashtags": ",".join(data.get("hashtags") or []),
                "likes": data.get("likeCount"),
                "comments": data.get("replyCount"),
                "shares": data.get("retweetCount"),
                "views": data.get("viewCount"),
                "followers_at_post": None,
                "author_name": (data.get("user") or {}).get("displayname"),
                "author_id": (data.get("user") or {}).get("id"),
                "is_competitor": is_competitor,
            }
        )
    df = pd.DataFrame(rows, columns=SCHEMA)
    return df
