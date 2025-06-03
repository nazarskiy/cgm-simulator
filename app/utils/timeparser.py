"""Time-based data filtering utilities for health metrics

This module provides functions for filtering and processing time-series health
metrics data based on various time intervals and reference dates.
"""

from typing import Dict
import pandas as pd

# Time intervals in hours
TIME_INTERVALS: Dict[str, float] = {
    "30min": 0.5,
    "1h": 1,
    "3h": 3,
    "6h": 6,
    "1d": 24,
    "3d": 24 * 3,
    "7d": 24 * 7,
    "14d": 24 * 14,
    "30d": 24 * 30,
    "90d": 24 * 90,
}


def last_x(df: pd.DataFrame, time_mod: str, last_date: str = None) -> pd.DataFrame:
    """Returns a DataFrame slice for the last X time interval
    Args:
        df (pd.DataFrame): DataFrame with the full data
        time_mod (str): Time interval string (e.g., '1h', '3h')
        last_date (str, optional): ISO format date string to start from
    Returns:
        pd.DataFrame: Sliced DataFrame for the last X interval
    """
    if time_mod not in TIME_INTERVALS:
        raise ValueError(f"Unknown time_mod: {time_mod}")

    if df.empty:
        return pd.DataFrame()
    df = df.sort_values(by='timestamps').reset_index(drop=True)

    if isinstance(df['timestamps'].iloc[0], str):
        df['timestamps'] = pd.to_datetime(df['timestamps'])

    window_size = int(TIME_INTERVALS[time_mod] * 12)

    if last_date:
        last_date = pd.to_datetime(last_date).tz_localize(None)

        mask = df['timestamps'] > last_date
        end = mask.idxmax() + 1 if mask.any() else len(df)
    else:
        end = 1

    end = min(end, len(df))
    start = max(0, end - window_size)

    result = df.iloc[start:end].copy()
    return result

def precise_day_last_x(full_data: pd.DataFrame, time_mod: str, last_date: str = None) -> pd.DataFrame:
    """Returns a DataFrame slice for the last X days with precise day boundaries
    Args:
        full_data (pd.DataFrame): DataFrame with the full data
        time_mod (str): Time interval string (e.g., '1d', '3d')
        last_date (str, optional): ISO format date string to start from
    Returns:
        pd.DataFrame: Sliced DataFrame for the last X days
    """
    df = last_x(full_data, time_mod, last_date)

    if not pd.api.types.is_datetime64_any_dtype(df["timestamps"]):
        df["timestamps"] = pd.to_datetime(df["timestamps"])

    digits = int(''.join(char for char in time_mod if char.isdigit()))
    unique_days = df["timestamps"].dt.date.nunique()

    if (digits != unique_days) and (unique_days > digits):
        df = df.sort_values("timestamps")
        to_remove = df["timestamps"].iloc[0].date()
        df = df[df["timestamps"].dt.date != to_remove]

    return df
