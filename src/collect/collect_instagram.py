from __future__ import annotations

"""Collect public Instagram posts using instaloader."""

from datetime import datetime

import pandas as pd
import instaloader

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


def collect_instagram(handle: str, since: datetime, *, is_competitor: bool = False) -> pd.DataFrame:
    """Collect posts for ``handle`` since ``since``; skip private profiles."""
    loader = instaloader.Instaloader(download=False, quiet=True)
    posts = []
    try:
        profile = instaloader.Profile.from_username(loader.context, handle)
    except Exception:
        return pd.DataFrame(columns=SCHEMA)
    if profile.is_private:
        return pd.DataFrame(columns=SCHEMA)

    for post in profile.get_posts():
        if post.date_utc < since:
            break
        posts.append(
            {
                "post_id": post.mediaid,
                "platform": "instagram",
                "handle": handle,
                "url": f"https://www.instagram.com/p/{post.shortcode}",
                "datetime": post.date_utc,
                "text": post.caption,
                "media_type": "video" if post.is_video else "image",
                "hashtags": ",".join(post.caption_hashtags),
                "likes": post.likes,
                "comments": post.comments,
                "shares": None,
                "views": post.video_view_count if post.is_video else None,
                "followers_at_post": profile.followers,
                "author_name": profile.full_name,
                "author_id": profile.userid,
                "is_competitor": is_competitor,
            }
        )
    df = pd.DataFrame(posts, columns=SCHEMA)
    return df
