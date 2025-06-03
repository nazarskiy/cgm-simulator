"""Statistics calculation utilities for health metrics data
"""

from typing import List
import pandas as pd
from app.utils.timeparser import precise_day_last_x

def update_stats(full_data: pd.DataFrame, time_mod: str, last_date: str) -> List[str]:
    """Calculate and format health metrics statistics for a given time period
    Args:
        full_data (pd.DataFrame): DataFrame containing health metrics data
        time_mod (str): Time period modifier (e.g., 'day', 'week')
        last_date (str): Reference date for the time period
    Returns:
        List[str]: List of formatted statistics strings for glucose, heart rate, and steps
    """
    df = precise_day_last_x(full_data, time_mod, last_date)
    if df.empty:
        return ["N/A"] * 5
    current_gl = df["glucose"].iloc[-1]
    average_gl = df["glucose"].mean()
    std_gl = df["glucose"].std()
    current_hr = df["heart_rate"].iloc[-1]
    steps_total = df["steps"].sum()

    return [
        f"Current: {current_gl:.1f} mg/dL",
        f"Average: {average_gl:.1f} mg/dL",
        f"Std Dev: {std_gl:.1f} mg/dL",
        f"Current: {current_hr:.1f} bpm",
        f"Total steps: {steps_total}"
    ]
