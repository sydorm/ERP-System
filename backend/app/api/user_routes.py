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
from app.core.permissions import permissions_registry_payload, sanitize_permissions
from app.api.dependencies import PermissionChecker, get_current_active_user
from app.services.mail_service import send_new_password_email
from app.services.audit_service import create_audit_log
import secrets
import string

router = APIRouter()

USER_ACTIVITY_ACTIONS = {
    "login",
    "logout",
    "open_page",
    "create",
    "update",
    "delete",
    "status_change",
    "print",
    "export",
    "permission_change",
}


@router.get("/permissions/registry")
async def read_permissions_registry(
    current_user: User = Depends(PermissionChecker(["users.view"]))
):
    return permissions_registry_payload()


@router.get("/users/colleagues", response_model=List[UserResponse])
async def read_colleagues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Return all users in the same company (available to any authenticated user)."""
    return db.query(User).filter(User.company_id == current_user.company_id).all()


@router.get("/users/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """Return the currently authenticated user's profile."""
    return current_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Return a user by ID. Users can only access their own profile; admins can access any."""
    if str(current_user.id) != str(user_id) and not (
        current_user.is_superuser or current_user.role == "admin" or
        (current_user.permissions or {}).get("users.view")
    ):
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == current_user.company_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return user


@router.get("/users", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(PermissionChecker(["users.view"])),
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
    current_user: User = Depends(PermissionChecker(["users.create"])),
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
        phone=user_in.phone,
        avatar_url=user_in.avatar_url,
        role=user_in.role or "manager",
        permissions=sanitize_permissions(user_in.permissions),
        company_id=current_user.company_id,
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Log action
    create_audit_log(
        db, 
        user_id=current_user.id,
        action="create",
        entity_type="user",
        entity_id=user.id,
        changes=user_in.dict(exclude={"password"})
    )

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(PermissionChecker(["users.edit"])),
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
    old_permissions = user.permissions or {}

    if user_in.role:
        user.role = user_in.role
    if user_in.permissions is not None:
        user.permissions = sanitize_permissions(user_in.permissions)
    if user_in.phone is not None:
        user.phone = user_in.phone
    if user_in.avatar_url is not None:
        user.avatar_url = user_in.avatar_url
        
    db.commit()
    db.refresh(user)

    # Log action
    create_audit_log(
        db, 
        user_id=current_user.id,
        action="update",
        entity_type="user",
        entity_id=user.id,
        changes=user_in.dict(exclude_unset=True)
    )

    if user_in.permissions is not None and old_permissions != user.permissions:
        create_audit_log(
            db,
            user_id=current_user.id,
            action="permission_change",
            entity_type="user",
            entity_id=user.id,
            changes={"old": old_permissions, "new": user.permissions}
        )

    return user


@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(PermissionChecker(["users.delete"])),
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
    create_audit_log(
        db,
        user_id=current_user.id,
        action="delete",
        entity_type="user",
        entity_id=user.id,
        changes={"email": user.email}
    )
    return user


@router.post("/users/{user_id}/password-reset", response_model=UserResponse)
async def reset_user_password(
    user_id: UUID,
    send_email: bool = False,
    current_user: User = Depends(PermissionChecker(["users.manage"])),
    db: Session = Depends(get_db)
):
    """
    Reset user password to a random one and optionally send via email
    """
    user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Generate random password
    alphabet = string.ascii_letters + string.digits
    new_password = ''.join(secrets.choice(alphabet) for i in range(10))
    
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    
    # Send email if requested
    email_sent = False
    if send_email and user.email:
        email_sent = await send_new_password_email(user.email, new_password, user.first_name)
    
    # Log action
    create_audit_log(
        db, 
        user_id=current_user.id,
        action="status_change",
        entity_type="user",
        entity_id=user.id,
        changes={"method": "random_gen", "email_sent": email_sent}
    )
    
    # We return the user object, but also we can add a custom header or detail if needed.
    # For now, let's just return the user. The password will be shown in the UI once after reset.
    user.temp_password = new_password # Temporal property for response (not in DB)
    return user


@router.patch("/users/{user_id}/block")
async def block_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["users.manage"])),
):
    from datetime import datetime
    user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
        
    user.blocked_at = datetime.utcnow()
    db.commit()
    create_audit_log(
        db,
        user_id=current_user.id,
        action="status_change",
        entity_type="user",
        entity_id=user.id,
        changes={"blocked_at": user.blocked_at.isoformat()}
    )
    return {"status": "blocked", "blocked_at": user.blocked_at.isoformat()}


@router.patch("/users/{user_id}/unblock")
async def unblock_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["users.manage"])),
):
    user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
        
    user.blocked_at = None
    db.commit()
    create_audit_log(
        db,
        user_id=current_user.id,
        action="status_change",
        entity_type="user",
        entity_id=user.id,
        changes={"blocked_at": None}
    )
    return {"status": "active"}


@router.get("/users/{user_id}/activity")
async def read_user_activity(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["users.view"]))
):
    from sqlalchemy import desc
    from app.models.audit_log import AuditLog

    user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == "user", AuditLog.entity_id == user_id)
        .order_by(desc(AuditLog.created_at))
        .limit(100)
        .all()
    )
    return [
        {
            "id": log.id,
            "action": log.action,
            "changes": log.changes,
            "created_at": log.created_at,
            "actor_id": log.user_id,
        }
        for log in logs
        if log.action in USER_ACTIVITY_ACTIONS
    ]
