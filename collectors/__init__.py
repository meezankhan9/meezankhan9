"""Unified social-media collectors."""
from __future__ import annotations

from typing import Dict, Optional, List

import logging
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
    logger = logging.getLogger(__name__)

    if handle := handles.get("twitter"):
        try:
            df = collect_twitter(handle, months)
            if not df.empty:
                dfs.append(df)
        except Exception as exc:  # pragma: no cover - network errors
            logger.warning("Twitter collection failed: %s", exc)

    if handle := handles.get("instagram"):
        try:
            df = collect_instagram(handle, months)
            if not df.empty:
                dfs.append(df)
        except Exception as exc:  # pragma: no cover - network errors
            logger.warning("Instagram collection failed: %s", exc)

    if yt_key and (handle := handles.get("youtube")):
        try:
            df = collect_youtube(handle, yt_key, months)
            if not df.empty:
                dfs.append(df)
        except Exception as exc:  # pragma: no cover - network errors
            logger.warning("YouTube collection failed: %s", exc)

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame(columns=SCHEMA)
