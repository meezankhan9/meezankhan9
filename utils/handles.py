"""Utility functions for detecting social media handles via DuckDuckGo search."""
from __future__ import annotations

from typing import Dict, Optional

from duckduckgo_search import DDGS


PLATFORM_PATTERNS = {
    "twitter": "twitter.com/",
    "instagram": "instagram.com/",
    "youtube": "youtube.com/",
}


def detect_handles(name: str, platforms: Optional[list[str]] = None) -> Dict[str, str]:
    """Return mapping of platform -> handle for the given name.

    Parameters
    ----------
    name: str
        Name of the candidate to search for.
    platforms: list[str], optional
        Subset of platforms to search. Defaults to twitter, instagram, youtube.

    Notes
    -----
    The function performs a simple web search and parses the first result
    containing the platform domain. It is not guaranteed to be accurate.
    """

    platforms = platforms or list(PLATFORM_PATTERNS.keys())
    handles: Dict[str, str] = {}

    with DDGS() as ddgs:
        for platform in platforms:
            pattern = PLATFORM_PATTERNS[platform]
            query = f"{name} {platform}"
            try:
                results = ddgs.text(query, max_results=5)
            except Exception:
                results = []
            for res in results:
                url = res.get("href", "")
                if pattern in url:
                    handle = url.split(pattern)[-1].strip("/")
                    if "?" in handle:
                        handle = handle.split("?")[0]
                    handles[platform] = handle
                    break
    return handles

