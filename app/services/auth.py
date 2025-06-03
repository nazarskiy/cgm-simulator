"""Authentication service module for user registration and login functionality"""

import json
import random
from typing import Optional, Dict, Any
from app.models.user import UserRegister, UserLogin, UserOut

USERS_FILE = "users.json"

def _load_users() -> Dict[str, Any]:
    """Load user data from the JSON file
    Returns:
        Dict[str, Any]: Dictionary containing user data
    """
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_users(users: Dict[str, Any]) -> None:
    """Save user data to the JSON file
    Args:
        users (Dict[str, Any]): Dictionary containing user data to save
    """
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def register_user(data: UserRegister) -> UserOut:
    """Register a new user in the system
    Args:
        data (UserRegister): User registration data containing username, password,
            and data source preferences
    Returns:
        UserOut: User data object containing registration details
    Raises:
        ValueError: If the username is already taken
    """
    users = _load_users()
    if data.username in users:
        raise ValueError("Username already taken")

    real_id = None
    if data.use_real_data:
        real_id = data.real_user_id if data.real_user_id != 0 else random.randint(0, 25)
    synthetic_id = None
    if not data.use_real_data:
        synthetic_id = data.synthetic_user_id if data.synthetic_user_id is not None else random.randint(0, 200)

    user_id = len(users) + 1
    users[data.username] = {
        "id": user_id,
        "password": data.password,
        "use_real_data": data.use_real_data,
        "real_user_id": real_id,
        "synthetic_user_id": synthetic_id,
        "last_viewed_timestamp": None
    }

    _save_users(users)
    return UserOut(
        user_id=user_id,
        username=data.username,
        real_user_id=real_id,
        synthetic_user_id=synthetic_id,
        is_synthetic=not data.use_real_data
    )

def login_user(data: UserLogin) -> Optional[UserOut]:
    """Authenticate a user and return their data if successful
    Args:
        data (UserLogin): User login credentials containing username and password
    Returns:
        Optional[UserOut]: User data object if authentication is successful,
            None otherwise.
    """
    users = _load_users()
    user = users.get(data.username)
    if not user:
        raise ValueError("Invalid username")
    if not user["password"] == data.password:
        raise ValueError("Invalid password")
    return UserOut(
            user_id=user["id"],
            username=data.username,
            real_user_id=user.get("real_user_id"),
            synthetic_user_id=user.get("synthetic_user_id"),
            is_synthetic=not user.get("use_real_data", False)
        )
