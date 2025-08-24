"""Instagram collector using instaloader."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
import os

import pandas as pd
import instaloader

from .twitter import SCHEMA  # reuse schema


logger = logging.getLogger(__name__)

loader = instaloader.Instaloader(
    quiet=True,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
)

# Optional login to improve reliability on protected endpoints
_IG_USER = os.getenv("INSTAGRAM_USER")
_IG_PASS = os.getenv("INSTAGRAM_PASS")
if _IG_USER and _IG_PASS:  # pragma: no cover - requires credentials
    try:
        loader.login(_IG_USER, _IG_PASS)
    except instaloader.exceptions.InstaloaderException as exc:
        logger.warning("Instagram login failed: %s", exc)


def collect_instagram(handle: str, months: int = 6) -> pd.DataFrame:
    """Collect public Instagram posts for handle within last ``months`` months."""
    posts = []
    cutoff = datetime.utcnow() - timedelta(days=30 * months)
    try:
        profile = instaloader.Profile.from_username(loader.context, handle)
        for post in profile.get_posts():
            if post.date_utc < cutoff:
                break
            posts.append(
                {
                    "post_id": post.shortcode,
                    "platform": "instagram",
                    "handle": handle,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "datetime": post.date_utc,
                    "text": post.caption or "",
                    "media_type": "video" if post.is_video else "image",
                    "hashtags": ",".join(post.caption_hashtags),
                    "likes": post.likes,
                    "comments": post.comments,
                    "shares": None,
                    "views": post.video_view_count if post.is_video else None,
                    "followers_at_post": profile.followers,
                    "author_name": profile.full_name,
                    "author_id": profile.userid,
                    "is_competitor": False,
                }
            )
    except instaloader.exceptions.InstaloaderException as exc:
        logger.warning("Instagram scrape failed: %s", exc)
    df = pd.DataFrame(posts, columns=SCHEMA)
    return df

