from __future__ import annotations

"""DuckDuckGo-based handle guesser for social platforms."""

from urllib.parse import urlparse
from typing import Optional

from duckduckgo_search import DDGS


def _search_first(query: str) -> Optional[str]:
    """Return the first result URL for ``query`` using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=1):
                return r.get("href")
    except Exception:
        pass
    return None


def _handle_from_url(url: str) -> Optional[str]:
    if not url:
        return None
    path = urlparse(url).path.strip("/")
    if not path:
        return None
    return path.split("/")[0]


def guess_handles(name: str) -> dict[str, str]:
    """Guess public social handles for ``name``.

    Returns a dictionary with possible keys:
    ``x``, ``instagram``, ``youtube_channel_id``, ``youtube_handle``, ``facebook_url``.
    """
    handles: dict[str, str] = {}

    twitter_url = _search_first(f'site:twitter.com "{name}"') or _search_first(
        f'site:x.com "{name}"'
    )
    if twitter_url:
        handle = _handle_from_url(twitter_url)
        if handle:
            handles["x"] = handle

    insta_url = _search_first(f'site:instagram.com "{name}"')
    if insta_url:
        handle = _handle_from_url(insta_url)
        if handle:
            handles["instagram"] = handle

    yt_url = _search_first(f'site:youtube.com/channel "{name}"') or _search_first(
        f'site:youtube.com/@ "{name}"'
    )
    if yt_url:
        parsed = urlparse(yt_url)
        parts = parsed.path.strip("/").split("/")
        if "channel" in parts:
            idx = parts.index("channel") + 1
            if idx < len(parts):
                handles["youtube_channel_id"] = parts[idx]
        elif parsed.path.startswith("/@"):
            handles["youtube_handle"] = parsed.path[2:]

    fb_url = _search_first(f'site:facebook.com "{name}"')
    if fb_url:
        handles["facebook_url"] = fb_url

    return handles
