"""Functions for merging collected data."""
from __future__ import annotations

from typing import Sequence

import pandas as pd

from collectors.twitter import SCHEMA


def merge_posts(dfs: Sequence[pd.DataFrame]) -> pd.DataFrame:
    df = pd.concat([d for d in dfs if not d.empty], ignore_index=True)
    if not df.empty:
        df = df[SCHEMA]
    return df

