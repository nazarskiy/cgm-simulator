"""User-related Pydantic models for request/response validation"""

from typing import Optional
from pydantic import BaseModel

class UserRegister(BaseModel):
    """Model for user registration requests
    Attributes:
        username (str): Unique username for the user
        password (str): User's password
        use_real_data (bool): Whether to use real or synthetic data
        real_user_id (Optional[int]): ID for real data if using real data
        synthetic_user_id (Optional[int]): ID for synthetic data if using synthetic data
    """
    username: str
    password: str
    use_real_data: bool
    real_user_id: Optional[int] = None
    synthetic_user_id: Optional[int] = None

class UserLogin(BaseModel):
    """Model for user login requests
    Attributes:
        username (str): User's username
        password (str): User's password
    """
    username: str
    password: str

class UserOut(BaseModel):
    """Model for user response data
    Attributes:
        user_id (int): Primary user ID
        username (str): User's username
        real_user_id (Optional[int]): ID for real data if using real data
        synthetic_user_id (Optional[int]): ID for synthetic data if using synthetic data
        is_synthetic (bool): Flag indicating if user is using synthetic data
    """
    user_id: int
    username: str
    real_user_id: Optional[int] = None
    synthetic_user_id: Optional[int] = None
    is_synthetic: bool = False
