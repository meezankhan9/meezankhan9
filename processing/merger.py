"""Functions for merging collected data."""
from __future__ import annotations

from typing import Sequence

import pandas as pd

from collectors.twitter import SCHEMA


def merge_posts(dfs: Sequence[pd.DataFrame]) -> pd.DataFrame:
    """Merge collected posts into a single DataFrame.

    Parameters
    ----------
    dfs:
        Sequence of dataframes gathered from various collectors.

    Returns
    -------
    pd.DataFrame
        A dataframe containing the merged posts constrained to ``SCHEMA``.
        If all inputs are empty, an empty dataframe with ``SCHEMA`` columns is
        returned.
    """

    valid = [d for d in dfs if not d.empty]
    if not valid:
        return pd.DataFrame(columns=SCHEMA)
    df = pd.concat(valid, ignore_index=True)
    return df[SCHEMA]

