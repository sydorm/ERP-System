"""
Authentication API routes
Handles user registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.models import User
from app.schemas import (
    UserCreate, UserLogin, UserResponse, UserUpdate, Token,
    CompanyRegistrationRequest, UserPasswordUpdate
)
from app.core.security import (
    get_password_hash, verify_password, create_access_token
)
from app.api.dependencies import get_current_active_user
from app.core.config import settings

router = APIRouter()


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        company_id=user_data.company_id,
        is_active=True,
        is_superuser=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/auth/register-company", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_company(reg_data: CompanyRegistrationRequest, db: Session = Depends(get_db)):
    """
    Register a new company and admin user
    """
    # 1. Check if user email already exists
    existing_user = db.query(User).filter(User.email == reg_data.admin.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Check if company tax_id already exists
    from app.models import Company, Warehouse
    existing_company = db.query(Company).filter(Company.tax_id == reg_data.company.taxId).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company already registered with this Tax ID"
        )
        
    try:
        # 3. Create Company
        new_company = Company(
            name=reg_data.company.name,
            legal_name=reg_data.company.name, # Use name as legal name for now
            tax_id=reg_data.company.taxId,
            company_type=reg_data.company.legalForm,
            is_active=True
        )
        db.add(new_company)
        db.flush() # Flush to get company ID
        
        # 4. Create Admin User
        new_user = User(
            email=reg_data.admin.email,
            hashed_password=get_password_hash(reg_data.admin.password),
            first_name=reg_data.admin.firstName,
            last_name=reg_data.admin.lastName,
            company_id=new_company.id,
            role="admin", # Explicitly set as admin
            is_active=True,
            is_superuser=True # First user is superuser/admin
        )
        db.add(new_user)
        
        # 5. Seed default dictionaries
        from app.services.dictionary_service import seed_company_dictionaries
        seed_company_dictionaries(db, new_company.id)

        # 6. Create Default Warehouse
        new_warehouse = Warehouse(
            name=reg_data.settings.warehouseName,
            is_default=True,
            is_active=True,
            company_id=new_company.id
        )
        db.add(new_warehouse)
        
        db.commit()
        db.refresh(new_user)
        
        return new_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    
    Args:
        credentials: User login credentials
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "company_id": str(user.company_id)
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    
    Args:
        current_user: Authenticated user from dependency
        
    Returns:
        Current user data
    """
    return current_user


@router.put("/auth/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    
    Args:
        user_update: User update data
        current_user: Authenticated user from dependency
        db: Database session
        
    Returns:
        Updated user data
        
    Raises:
        HTTPException: If email is already taken by another user
    """
    # Check if email is being updated and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        current_user.email = user_update.email
    
    # Update fields if provided
    if user_update.first_name:
        current_user.first_name = user_update.first_name
    if user_update.last_name:
        current_user.last_name = user_update.last_name
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/auth/password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
        
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}
