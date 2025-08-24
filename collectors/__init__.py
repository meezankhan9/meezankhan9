"""Unified social-media collectors."""
from __future__ import annotations

from typing import Dict, Optional, List

import pandas as pd

from .twitter import collect_twitter, SCHEMA
from .instagram import collect_instagram
from .youtube import collect_youtube

__all__ = [
    "collect_twitter",
    "collect_instagram",
    "collect_youtube",
    "collect_all",
    "SCHEMA",
]


def collect_all(
    handles: Dict[str, str], months: int = 6, yt_key: Optional[str] = None
) -> pd.DataFrame:
    """Collect posts for available handles across supported platforms."""
    dfs: List[pd.DataFrame] = []

    if handle := handles.get("twitter"):
        df = collect_twitter(handle, months)
        if not df.empty:
            dfs.append(df)

    if handle := handles.get("instagram"):
        df = collect_instagram(handle, months)
        if not df.empty:
            dfs.append(df)

    if yt_key and (handle := handles.get("youtube")):
        df = collect_youtube(handle, yt_key, months)
        if not df.empty:
            dfs.append(df)

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame(columns=SCHEMA)
