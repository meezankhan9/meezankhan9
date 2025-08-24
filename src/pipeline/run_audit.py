from __future__ import annotations


"""Orchestrate data collection, merging, analysis, and report building."""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import pandas as pd

from .auto_handles import guess_handles
from ..collect.collect_x import collect_x
from ..collect.collect_instagram import collect_instagram
from ..collect.collect_youtube import collect_youtube
from ..collect.merge_posts import merge_posts
from ..analyze.report_builder import build_summary


def run(
    name: str,
    months: int = 12,
    youtube_key: str | None = None,
    rivals: Iterable[str] | None = None,
    sentiment: bool = False,
) -> dict:
    handles = guess_handles(name)
    since = datetime.utcnow() - timedelta(days=30 * months)
    dfs: list[pd.DataFrame] = []

    if h := handles.get("x"):
        dfs.append(collect_x(h, since, is_competitor=False))
    if h := handles.get("instagram"):
        dfs.append(collect_instagram(h, since, is_competitor=False))
    yt_identifier = handles.get("youtube_channel_id") or handles.get("youtube_handle")
    if youtube_key and yt_identifier:
        dfs.append(collect_youtube(yt_identifier, youtube_key, since, is_competitor=False))

    if rivals:
        for item in rivals:
            try:
                plat, handle = item.split(":", 1)
            except ValueError:
                continue
            plat = plat.strip().lower()
            handle = handle.strip()
            if plat in {"x", "twitter"}:
                dfs.append(collect_x(handle, since, is_competitor=True))
            elif plat in {"instagram", "ig"}:
                dfs.append(collect_instagram(handle, since, is_competitor=True))
            elif plat in {"youtube", "yt"} and youtube_key:
                dfs.append(collect_youtube(handle, youtube_key, since, is_competitor=True))

    master = merge_posts(dfs)
    master_path = Path("build/posts_master.csv")
    master_path.parent.mkdir(parents=True, exist_ok=True)
    master.to_csv(master_path, index=False)

    summary = build_summary(str(master_path), handles.get("x", name), months_view=months, run_sentiment=sentiment)
    report_path = Path("build/reports") / f"{name.replace(' ', '_')}_audit.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(summary["summary_md"])

    result = {
        "handles": handles,
        "summary_md": summary["summary_md"],
        "report_path": str(report_path),
        "pillar_scores": summary["pillar_scores"],
        "lowest_pillar": summary["lowest_pillar"],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--months", type=int, default=12)
    parser.add_argument("--youtube-key", dest="youtube_key")
    parser.add_argument(
        "--rivals",
        help="Comma-separated platform:handle pairs",
        default="",
    )
    parser.add_argument("--sentiment", action="store_true")
    args = parser.parse_args()
    rivals = [r.strip() for r in args.rivals.split(",") if r.strip()]
    result = run(args.name, args.months, args.youtube_key, rivals, args.sentiment)
    print(json.dumps(result))


if __name__ == "__main__":  # pragma: no cover
    main()
