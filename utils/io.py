"""I/O helper functions for Neuro Ninja."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
BUILD_DIR = BASE_DIR / "build"
REPORT_DIR = BUILD_DIR / "reports"

for d in [RAW_DIR, BUILD_DIR, REPORT_DIR]:
    os.makedirs(d, exist_ok=True)


def save_raw(df: pd.DataFrame, platform: str, handle: str) -> Path:
    filename = f"{platform}_{handle}.csv"
    path = RAW_DIR / filename
    df.to_csv(path, index=False)
    return path


def save_master(df: pd.DataFrame) -> Path:
    path = BUILD_DIR / "posts_master.csv"
    df.to_csv(path, index=False)
    return path


def save_report(text: str, name: str) -> Path:
    filename = f"{name}_audit.md"
    path = REPORT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

