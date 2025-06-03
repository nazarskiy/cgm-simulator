"""API routes for the application

This module contains all the API endpoints for user authentication, data retrieval,
and statistics calculation
"""

from fastapi import APIRouter, Body
from app.services.data_loader import load_certain_data
from app.models.user import UserRegister, UserLogin, UserOut
from app.services.auth import register_user, login_user
from app.services.timestamps import get_last_viewed, update_last_viewed
from app.utils.stats import update_stats
from app.utils.timeparser import last_x

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserRegister) -> UserOut:
    """Register a new user
    Args:
        user (UserRegister): User registration data
    Returns:
        UserOut: Registered user information
    """
    return register_user(user)

@router.post("/login", response_model=UserOut)
def login(user: UserLogin) -> UserOut:
    """Authenticate and login a user
    Args:
        user (UserLogin): User login credentials
    Returns:
        UserOut: Authenticated user information
    """
    return login_user(user)

@router.get("/api/stats/{user_id}")
def get_stats(
    user_id: int,
    real_data: bool,
    time_mod: str = "1h",
    last_date: str | None = None
) -> dict:
    """Get statistics for a specific user
    Args:
        user_id (int): ID of the user
        real_data (bool): Whether to use real or simulated data
        time_mod (str, optional): Time window for statistics. Defaults to "1h"
        last_date (str | None, optional): Last date to consider. Defaults to None
    Returns:
        dict: Dictionary containing calculated statistics
    """
    data = load_certain_data(user_id, "glucose", "heart_rate", "steps", real_data=real_data)
    window_data = last_x(data, time_mod, last_date)
    stats = update_stats(window_data, time_mod, last_date)
    return {"stats": stats}

@router.post("/update_last_viewed")
def update_last_viewed_endpoint(
    username: str = Body(...),
    last_viewed_timestamp: str = Body(...)
) -> dict:
    """Update the last viewed timestamp for a user
    Args:
        username (str): Username of the user
        last_viewed_timestamp (str): Timestamp of last view
    Returns:
        dict: Status of the update operation
    """
    success = update_last_viewed(username, last_viewed_timestamp)
    return {"status": "success" if success else "user not found"}

@router.get("/api/glucose/{user_id}")
def get_glucose(
    user_id: int,
    real_data: bool,
    time_mod: str = "1h",
    last_date: str | None = None
) -> list:
    """Get glucose data for a specific user for plotting later
    Args:
        user_id (int): ID of the user
        real_data (bool): Whether to use real or simulated data
        time_mod (str, optional): Time window for data. Defaults to "1h"
        last_date (str | None, optional): Last date to consider. Defaults to None
    Returns:
        list: List of glucose records
    """
    data = load_certain_data(user_id, "glucose", real_data=real_data)
    window_data = last_x(data, time_mod, last_date)
    return window_data.to_dict("records")

@router.get("/api/last_viewed/{username}")
def get_last_viewed_endpoint(username: str) -> dict:
    """Get the last viewed timestamp for a user
    Args:
        username (str): Username of the user
    Returns:
        dict: Dictionary containing the last viewed timestamp
    """
    last_viewed = get_last_viewed(username)
    return {"last_viewed_timestamp": last_viewed}
