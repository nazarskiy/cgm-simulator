"""Data loading service for accessing user health metrics data
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REAL_DATA_PATH = os.path.join(BASE_DIR, "data", "db.csv")
SYNTHETIC_DATA_PATH = os.path.join(BASE_DIR, "synthetic", "prepr_synt_enhanced.csv")

def get_real_user_data(user_id: int, real_data: bool) -> pd.DataFrame:
    """Load all data for a specific user from either real or synthetic dataset
    Args:
        user_id (int): The ID of the user to load data for
        real_data (bool): Whether to load from real or synthetic dataset
    Returns:
        pd.DataFrame: DataFrame containing all user data
    """
    db_path = REAL_DATA_PATH if real_data else SYNTHETIC_DATA_PATH
    db = pd.read_csv(db_path)

    if user_id not in db["user_id"].unique():
        raise ValueError(f"User {user_id} not found")

    user_data = db[db["user_id"] == user_id]
    return user_data


def load_certain_data(user_id: int, *columns: str, real_data: bool) -> pd.DataFrame:
    """Load specific columns of data for a user
    Args:
        user_id (int): The ID of the user to load data for
        *columns (str): Variable number of column names to load (e.g., 'glucose', 'heart_rate')
        real_data (bool): Whether to load from real or synthetic dataset
    Returns:
        pd.DataFrame: DataFrame containing requested columns
    """
    if real_data and (user_id < 0 or user_id >= 26):
        raise ValueError("Real User ID out of range (must be between 0 and 25)")
    if not real_data and (user_id < 0 or user_id >= 201):
        raise ValueError("Synthetic User ID out of range (must be between 0 and 200)")

    data = get_real_user_data(user_id, real_data)

    if not pd.api.types.is_datetime64_any_dtype(data["time"]):
        data["time"] = pd.to_datetime(data["time"], errors="coerce")

    data = data.sort_values("time", ascending=True)

    columns = ("time",) + columns
    ret_data = data[list(columns)].copy()
    ret_data = ret_data.rename(columns={'time': 'timestamps'})

    return ret_data
