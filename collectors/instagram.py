"""Instagram collector using instaloader."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import instaloader

from .twitter import SCHEMA  # reuse schema


L = instaloader.Instaloader(download_pictures=False,
                            download_videos=False,
                            download_comments=False,
                            save_metadata=False)


def collect_instagram(handle: str, months: int = 6) -> pd.DataFrame:
    """Collect public Instagram posts for handle within last ``months`` months."""
    posts = []
    cutoff = datetime.utcnow() - timedelta(days=30 * months)
    try:
        profile = instaloader.Profile.from_username(L.context, handle)
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
    except Exception:
        pass
    df = pd.DataFrame(posts, columns=SCHEMA)
    return df

