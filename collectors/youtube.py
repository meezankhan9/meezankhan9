"""YouTube collector using official API."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from googleapiclient.discovery import build

from .twitter import SCHEMA


def collect_youtube(handle: str, api_key: str, months: int = 6) -> pd.DataFrame:
    """Collect videos for channel ``handle`` using the YouTube API."""
    cutoff = datetime.utcnow() - timedelta(days=30 * months)
    yt = build("youtube", "v3", developerKey=api_key)

    channel_req = yt.channels().list(part="id", forUsername=handle)
    channel_res = channel_req.execute()
    items = channel_res.get("items", [])
    if not items:
        return pd.DataFrame(columns=SCHEMA)
    channel_id = items[0]["id"]

    search_req = yt.search().list(part="snippet", channelId=channel_id, maxResults=50, order="date")
    search_res = search_req.execute()

    videos = []
    for item in search_res.get("items", []):
        snippet = item["snippet"]
        published = datetime.strptime(snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
        if published < cutoff:
            continue
        videos.append(
            {
                "post_id": item["id"].get("videoId"),
                "platform": "youtube",
                "handle": handle,
                "url": f"https://www.youtube.com/watch?v={item['id'].get('videoId')}",
                "datetime": published,
                "text": snippet.get("title"),
                "media_type": "video",
                "hashtags": None,
                "likes": None,
                "comments": None,
                "shares": None,
                "views": None,
                "followers_at_post": None,
                "author_name": snippet.get("channelTitle"),
                "author_id": channel_id,
                "is_competitor": False,
            }
        )
    df = pd.DataFrame(videos, columns=SCHEMA)
    return df

