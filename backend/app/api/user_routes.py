"""
User Management API routes
Handles user CRUD operations (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models import User
from app.schemas import (
    UserCreate, UserResponse, UserUpdate, UserInDB
)
from app.core.security import get_password_hash
from app.api.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all users (Admin only)
    """
    users = db.query(User).filter(User.company_id == current_user.company_id).offset(skip).limit(limit).all()
    return users


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new user (Admin only)
    """
    # Check if email exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role=user_in.role or "worker",
        company_id=current_user.company_id, # Link to admin's company
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a user (Admin only)
    """
    user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
        
    if user_in.email and user_in.email != user.email:
         existing_user = db.query(User).filter(User.email == user_in.email).first()
         if existing_user:
             raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )
         user.email = user_in.email

    if user_in.first_name:
        user.first_name = user_in.first_name
    if user_in.last_name:
        user.last_name = user_in.last_name
    if user_in.role:
        user.role = user_in.role
        
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user (Admin only)
    """
    user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Users cannot delete themselves",
        )
        
    # We doing soft delete (deactivate) or hard delete?
    # Let's do hard delete for now as requested, or just deactivate.
    # Given the requirements usually imply removing access, deactivation is safer but delete is cleaner for management.
    # Let's simple delete for now to keep it clean.
    db.delete(user)
    db.commit()
    return user


@router.post("/users/{user_id}/password", response_model=UserResponse)
async def reset_password(
    user_id: UUID,
    password: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Reset user password (Admin only)
    """
    user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
        
    user.hashed_password = get_password_hash(password)
    db.commit()
    db.refresh(user)
    return user
