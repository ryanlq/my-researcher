"""Authentication API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse
from app.core.security.auth import get_current_user, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # TODO: Implement user registration
    # - Check if email already exists
    # - Hash password
    # - Create user
    # - Return user data
    pass


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    User login
    """
    # TODO: Implement login
    # - Verify email and password
    # - Generate JWT token
    # - Return token with user data
    pass


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout user (JWT is stateless, client should discard token)
    """
    return {"message": "Successfully logged out"}
