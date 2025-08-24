from __future__ import annotations

"""Merge multiple post DataFrames into a single master dataset."""

from typing import Iterable

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


def merge_posts(dfs: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate and cast columns to the standard schema."""
    dfs = [df for df in dfs if df is not None and not df.empty]
    if not dfs:
        return pd.DataFrame(columns=SCHEMA)
    df = pd.concat(dfs, ignore_index=True)
    df = df.reindex(columns=SCHEMA)
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True)
    return df
