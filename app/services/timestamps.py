"""Timestamp management service for tracking user data viewing progress"""

from typing import Optional
import pandas as pd
from app.services.auth import _load_users, _save_users


def update_last_viewed(username: str, last_viewed_timestamp: str) -> bool:
    """Update the last viewed timestamp for a user if the new timestamp is more recent
    Args:
        username (str): The username of the user
        last_viewed_timestamp (str): The new timestamp to potentially update to
    Returns:
        bool: True if the timestamp was updated, False otherwise
    """
    users = _load_users()

    current_timestamp = users[username].get("last_viewed_timestamp")

    if current_timestamp is None or pd.to_datetime(last_viewed_timestamp) > pd.to_datetime(current_timestamp):
        users[username]["last_viewed_timestamp"] = last_viewed_timestamp
        _save_users(users)
        return True
    return False


def get_last_viewed(username: str) -> Optional[str]:
    """This function retrieves the last viewed timestamp for a user
    Args:
        username (str): The username of the user
    Returns:
        Optional[str]: The last viewed timestamp if valid, None otherwise
    """
    users = _load_users()

    if username in users:
        return users[username].get("last_viewed_timestamp")
    return None
