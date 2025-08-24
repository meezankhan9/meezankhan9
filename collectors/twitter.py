"""Twitter collector using snscrape."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

import pandas as pd
import snscrape.modules.twitter as sntwitter


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


def collect_twitter(handle: str, months: int = 6) -> pd.DataFrame:
    """Collect tweets for handle within last ``months`` months."""
    since = (datetime.utcnow() - timedelta(days=30 * months)).date()
    query = f"from:{handle} since:{since}"
    tweets: List[dict] = []
    try:
        for tweet in sntwitter.TwitterSearchScraper(query).get_items():
            tweets.append(
                {
                    "post_id": tweet.id,
                    "platform": "twitter",
                    "handle": handle,
                    "url": tweet.url,
                    "datetime": tweet.date,
                    "text": tweet.rawContent,
                    "media_type": getattr(tweet, "media", None).__class__.__name__ if getattr(tweet, "media", None) else None,
                    "hashtags": ",".join(hashtag.lower() for hashtag in tweet.hashtags or []),
                    "likes": tweet.likeCount,
                    "comments": tweet.replyCount,
                    "shares": tweet.retweetCount,
                    "views": tweet.viewCount if hasattr(tweet, "viewCount") else None,
                    "followers_at_post": None,
                    "author_name": tweet.user.displayname,
                    "author_id": tweet.user.id,
                    "is_competitor": False,
                }
            )
    except Exception:
        pass
    df = pd.DataFrame(tweets, columns=SCHEMA)
    return df

