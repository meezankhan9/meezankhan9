from __future__ import annotations

"""Collect YouTube uploads using the Data API v3."""

from datetime import datetime
from typing import Optional

import pandas as pd
from googleapiclient.discovery import build

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


def _ensure_channel_id(youtube, identifier: str) -> Optional[str]:
    """Resolve a channel handle to a channel ID if needed."""
    if identifier.startswith("UC"):
        return identifier
    if identifier.startswith("@"):
        query = identifier
    else:
        query = f"@{identifier}"
    resp = (
        youtube.search()
        .list(part="snippet", q=query, type="channel", maxResults=1)
        .execute()
    )
    items = resp.get("items")
    if items:
        return items[0]["snippet"]["channelId"]
    return None


def collect_youtube(
    identifier: str,
    api_key: str,
    since: datetime,
    *,
    is_competitor: bool = False,
) -> pd.DataFrame:
    """Collect recent uploads for channel ``identifier`` (ID or @handle)."""
    youtube = build("youtube", "v3", developerKey=api_key)
    channel_id = _ensure_channel_id(youtube, identifier)
    if not channel_id:
        return pd.DataFrame(columns=SCHEMA)

    channel_res = youtube.channels().list(
        id=channel_id, part="contentDetails,snippet,statistics"
    ).execute()
    items = channel_res.get("items")
    if not items:
        return pd.DataFrame(columns=SCHEMA)
    ch = items[0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    author_name = ch["snippet"]["title"]
    followers = int(ch.get("statistics", {}).get("subscriberCount", 0))

    posts = []
    next_page: Optional[str] = None
    while True:
        res = youtube.playlistItems().list(
            playlistId=uploads,
            part="contentDetails,snippet",
            maxResults=50,
            pageToken=next_page,
        ).execute()
        for item in res["items"]:
            vid_id = item["contentDetails"]["videoId"]
            published = datetime.fromisoformat(
                item["contentDetails"]["videoPublishedAt"].replace("Z", "+00:00")
            )
            if published < since:
                return pd.DataFrame(posts, columns=SCHEMA)
            stats = (
                youtube.videos()
                .list(id=vid_id, part="statistics,snippet")
                .execute()
                .get("items", [{}])[0]
            )
            snippet = stats.get("snippet", {})
            statistics = stats.get("statistics", {})
            posts.append(
                {
                    "post_id": vid_id,
                    "platform": "youtube",
                    "handle": channel_id,
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                    "datetime": published,
                    "text": snippet.get("description"),
                    "media_type": "video",
                    "hashtags": ",".join(snippet.get("tags", [])),
                    "likes": int(statistics.get("likeCount", 0)),
                    "comments": int(statistics.get("commentCount", 0)),
                    "shares": None,
                    "views": int(statistics.get("viewCount", 0)),
                    "followers_at_post": followers,
                    "author_name": author_name,
                    "author_id": channel_id,
                    "is_competitor": is_competitor,
                }
            )
        next_page = res.get("nextPageToken")
        if not next_page:
            break
    df = pd.DataFrame(posts, columns=SCHEMA)
    return df
