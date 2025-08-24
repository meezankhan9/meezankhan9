from __future__ import annotations

"""Build neutral analytics report and pillar scores."""

from collections import Counter
from typing import Dict, Iterable

import numpy as np
import pandas as pd

# Generic narrative keywords for gap detection
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

PILLARS: Dict[str, Dict[str, object]] = {
    "janata": {
        "title": "Janata ke Beech",
        "desc": "Belonging & trust with people, grassroots contact",
        "kw": ["janata", "people", "public", "sampark", "gaon", "trust"],
    },
    "fixer": {
        "title": "The Fixer",
        "desc": "Before/after work, problem → action → result",
        "kw": ["before", "after", "fix", "kaam", "samasya", "samadhan"],
    },
    "aspiration": {
        "title": "Aspiration Ladder",
        "desc": "Future roadmap visuals and plans",
        "kw": ["future", "vision", "roadmap", "sapna", "plan"],
    },
    "dashboard": {
        "title": "Development Dashboard",
        "desc": "Data charts showing progress",
        "kw": ["dashboard", "data", "chart", "progress", "report"],
    },
    "seva": {
        "title": "Seva & Samvedna",
        "desc": "Human stories and service",
        "kw": ["seva", "samvedna", "service", "help", "story"],
    },
    "youth": {
        "title": "Youth Connect",
        "desc": "Jobs, sports, shorts",
        "kw": ["youth", "jobs", "sports", "shorts", "campus"],
    },
    "women": {
        "title": "Women & Safety",
        "desc": "Testimonials and safety meets",
        "kw": ["women", "mahila", "safety", "nari", "testimonials"],
    },
    "misinfo": {
        "title": "Counter-Misinformation",
        "desc": "Claim → Fact reels with citations",
        "kw": ["fact", "myth", "claim", "truth", "misinformation"],
    },
    "branding": {
        "title": "Heroic Personal Branding",
        "desc": "Leader as symbol, third-party mentions",
        "kw": ["leader", "brand", "hero", "symbol", "mention"],
    },
}

RECOMMENDATIONS = {
    "janata": [
        "Host more community interactions with candid photos",
        "Share testimonials from beneficiaries to build trust",
    ],
    "fixer": [
        "Post before/after visuals for completed work",
        "Use 'problem → action → result' format in reels",
    ],
    "aspiration": [
        "Publish roadmap infographics for upcoming plans",
        "Outline future milestones via carousel posts",
    ],
    "dashboard": [
        "Use simple charts to show progress numbers",
        "Release periodic dashboard-style updates",
    ],
    "seva": [
        "Highlight human stories of service with consent",
        "Share 'day in life' posts of on-ground work",
    ],
    "youth": [
        "Weekly Shorts about jobs or skill programs",
        "Feature sports or campus event reels",
    ],
    "women": [
        "Share testimonials from women beneficiaries",
        "Publicize safety initiative meet-ups",
    ],
    "misinfo": [
        "Create 'Claim → Fact' reels with citations",
        "Maintain myth-busting threads with sources",
    ],
    "branding": [
        "Post third-party endorsements or awards",
        "Share symbolic leadership moments factually",
    ],
}

try:  # optional semantic model
    from numpy.linalg import norm
    from sentence_transformers import SentenceTransformer

    _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:  # pragma: no cover - optional dependency
    _MODEL = None


def _semantic_score(text: str, desc: str) -> float:
    if not _MODEL:
        return 0.0
    v1 = _MODEL.encode([text], show_progress_bar=False)[0]
    v2 = _MODEL.encode([desc], show_progress_bar=False)[0]
    sim = float(np.dot(v1, v2) / (norm(v1) * norm(v2) + 1e-9))
    return (sim + 1) / 2  # normalize to [0,1]


def _post_weights(df: pd.DataFrame) -> np.ndarray:
    now = pd.Timestamp.now(tz="UTC")
    eng = df["likes"].fillna(0) + 2 * df["comments"].fillna(0) + 2 * df["shares"].fillna(0)
    max_eng = max(eng.max(), 1)
    w_eng = eng / max_eng
    age_months = (now - df["datetime"]).dt.days / 30
    w_time = np.exp(-0.2 * age_months)
    w_media = np.where(df["media_type"].isin(["video", "reel"]), 1.15, 1.0)
    return 0.5 * w_eng + 0.3 * w_time + 0.2 * w_media


def _pillar_presence(df: pd.DataFrame, pillar: Dict[str, object]) -> float:
    if df.empty:
        return 0.0
    weights = _post_weights(df)
    raw = 0.0
    for (text, hashtags, media), w in zip(
        df[["text", "hashtags", "media_type"]].fillna(""), weights
    ):
        text_full = f"{text} {hashtags}".lower()
        kw_hits = sum(1 for kw in pillar["kw"] if kw in text_full)
        kw_score = min(kw_hits / 3.0, 1.0)
        sem_score = _semantic_score(text_full, pillar["desc"])
        match = 0.6 * kw_score + 0.4 * sem_score if _MODEL else kw_score
        raw += match * w
    denom = weights.sum() + 1e-9
    return raw / denom


def score_pillars(candidate_df: pd.DataFrame, rivals_df: pd.DataFrame) -> Dict[str, int]:
    scores = {k: _pillar_presence(candidate_df, v) for k, v in PILLARS.items()}
    if rivals_df is not None and not rivals_df.empty:
        rival_scores = {k: _pillar_presence(rivals_df, v) for k, v in PILLARS.items()}
        for k in scores:
            rv = rival_scores.get(k, 0.0)
            if rv > 0:
                scores[k] *= 1 + 0.2 * (scores[k] / rv)
    return {k: int(round(100 * min(v, 1.0))) for k, v in scores.items()}


def build_summary(
    master_csv: str,
    candidate_handle: str,
    months_view: int = 12,
    run_sentiment: bool = False,
) -> Dict[str, object]:
    """Generate summary markdown and pillar scores from merged posts."""
    df = pd.read_csv(master_csv)
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True)
    cutoff = pd.Timestamp.now(tz="UTC") - pd.DateOffset(months=months_view)
    df = df[df["datetime"] >= cutoff]

    candidate_df = df[df["is_competitor"] == False]
    rivals_df = df[df["is_competitor"] == True]

    lines = [f"# Digital Audit for {candidate_handle}\n"]
    lines.append("## Section 1 – Overview")
    posts_per_week = len(candidate_df) / max((months_view * 4), 1)
    presence = int(min(100, posts_per_week * 10 + candidate_df["platform"].nunique() * 10))
    lines.append(f"Presence score: {presence}/100")
    platforms = sorted(candidate_df["platform"].dropna().unique().tolist())
    lines.append(f"Platforms used: {', '.join(platforms) if platforms else 'None'}")
    if not candidate_df.empty:
        lines.append(
            f"Activity window: {candidate_df['datetime'].min().date()} – {candidate_df['datetime'].max().date()}"
        )

    lines.append("\n## Section 2 – Strengths")
    if not candidate_df.empty:
        for _, row in candidate_df.sort_values("likes", ascending=False).head(3).iterrows():
            lines.append(f"- {row['platform']} {row['url']} with {int(row['likes'] or 0)} likes")
    else:
        lines.append("No data")

    lines.append("\n## Section 3 – Weaknesses")
    if not candidate_df.empty:
        for _, row in candidate_df.sort_values("likes").head(3).iterrows():
            lines.append(f"- {row['platform']} {row['url']} with {int(row['likes'] or 0)} likes")
    else:
        lines.append("No data")

    lines.append("\n## Section 4 – Opportunities (neutral ops)")
    lines.append("- Balance formats and ensure consistent cadence")
    lines.append("- Maintain hashtag and caption hygiene across platforms")

    lines.append("\n## Section 5 – Threats / Risks")
    lines.append("- Rivals may outperform in engagement or platform breadth")

    lines.append("\n## Section 6 – Narrative Themes")
    if not candidate_df.empty:
        words = Counter(
            " ".join(candidate_df["text"].fillna("")).lower().split()
        )
        lines.append(", ".join(w for w, _ in words.most_common(10)))
    else:
        lines.append("No data")

    lines.append("\n## Section 7 – Narrative Gaps")
    text = " ".join(candidate_df["text"].fillna("")).lower()
    gaps = [k for k in KEYWORDS if k not in text]
    lines.append(", ".join(gaps) if gaps else "None")

    lines.append("\n## Section 8 – Recommendations (neutral, operational)")
    lines.extend(
        [
            "- Increase cadence to 3–5 posts/week",
            "- Add more short-form videos",
            "- Write longer captions with consistent hashtags",
            "- Showcase offline work online",
            "- Add content on missing themes (education, jobs, etc.)",
            "- Maintain weekly content calendar",
        ]
    )

    pillar_scores = score_pillars(candidate_df, rivals_df)
    lines.append("\n## Section 9 – Narrative Pillar Scores")
    lines.append("| Pillar | Score |")
    lines.append("| --- | --- |")
    for key, score in sorted(pillar_scores.items(), key=lambda x: x[1]):
        lines.append(f"| {PILLARS[key]['title']} | {score}/100 |")
    lowest_key = min(pillar_scores, key=pillar_scores.get)
    lines.append(
        f"\nLowest pillar: {PILLARS[lowest_key]['title']} ({pillar_scores[lowest_key]}/100)"
    )

    lines.append("\n## Section 10 – Pillar-Specific Recommendations")
    for rec in RECOMMENDATIONS.get(lowest_key, []):
        lines.append(f"- {rec}")

    summary_md = "\n".join(lines)
    pillar_scores_named = {PILLARS[k]["title"]: v for k, v in pillar_scores.items()}
    return {
        "summary_md": summary_md,
        "pillar_scores": pillar_scores_named,
        "lowest_pillar": PILLARS[lowest_key]["title"],
    }
