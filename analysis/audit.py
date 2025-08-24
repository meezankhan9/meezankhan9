"""Generate neutral digital audit from social media posts."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import List

import pandas as pd

KEYWORDS = [
    "development",
    "youth",
    "jobs",
    "women",
    "safety",
    "farmers",
    "health",
    "education",
    "corruption",
]


def presence_score(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    platforms = df["platform"].nunique()
    posts = len(df)
    score = min(100, platforms * 10 + posts // 10)
    return score


def top_keywords(df: pd.DataFrame, n: int = 10) -> List[str]:
    words = Counter()
    for text in df["text"].fillna(""):
        for w in text.lower().split():
            words[w] += 1
    return [w for w, _ in words.most_common(n)]


def narrative_gaps(df: pd.DataFrame) -> List[str]:
    text = " ".join(df["text"].fillna("")).lower()
    gaps = [k for k in KEYWORDS if k not in text]
    return gaps


def generate_audit(df: pd.DataFrame, name: str) -> str:
    lines = []
    lines.append(f"# Digital Audit for {name}\n")
    score = presence_score(df)
    lines.append("## Section 1 – Overview")
    lines.append(f"Presence score: {score}/100")
    lines.append(f"Platforms used: {', '.join(sorted(df['platform'].unique())) if not df.empty else 'None'}")
    if not df.empty:
        lines.append(f"Activity window: {df['datetime'].min()} – {df['datetime'].max()}")

    lines.append("\n## Section 2 – Strengths")
    if not df.empty:
        top = df.sort_values("likes", ascending=False).head(3)
        for _, row in top.iterrows():
            lines.append(f"- {row['platform']} {row['url']} with {row['likes']} likes")
    else:
        lines.append("No data")

    lines.append("\n## Section 3 – Weaknesses")
    if not df.empty:
        low = df.sort_values("likes").head(3)
        for _, row in low.iterrows():
            lines.append(f"- {row['platform']} {row['url']} with {row['likes']} likes")
    else:
        lines.append("No data")

    lines.append("\n## Section 4 – Opportunities")
    lines.append("- Balance formats and ensure consistent posting cadence.")
    lines.append("- Maintain hashtag hygiene and cross-platform usage.")

    lines.append("\n## Section 5 – Threats / Risks")
    lines.append("- Competitors may have higher engagement or broader platform presence.")

    lines.append("\n## Section 6 – Narrative Themes")
    if not df.empty:
        keywords = top_keywords(df)
        lines.append(", ".join(keywords))
    else:
        lines.append("No data")

    lines.append("\n## Section 7 – Narrative Gaps")
    gaps = narrative_gaps(df)
    lines.append(", ".join(gaps) if gaps else "None")

    lines.append("\n## Section 8 – Recommendations")
    lines.append("- Increase cadence to 3–5 posts/week.")
    lines.append("- Add more short-form videos and longer captions.")
    lines.append("- Showcase offline work online and cover missing themes.")
    lines.append("- Maintain a weekly content calendar.")

    return "\n".join(lines)

