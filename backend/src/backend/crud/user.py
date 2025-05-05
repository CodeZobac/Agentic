"""
CRUD operations for user management.
"""
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from backend.core.security import get_password_hash, verify_password
from backend.crud.base import CRUDBase
from backend.db.models import User
from backend.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.
    """
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            db: Database session.
            email: User email.
            
        Returns:
            Optional[User]: User if found, None otherwise.
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            db: Database session.
            username: Username.
            
        Returns:
            Optional[User]: User if found, None otherwise.
        """
        return db.query(User).filter(User.username == username).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            db: Database session.
            obj_in: User data.
            
        Returns:
            User: Created user.
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user.
        
        Args:
            db: Database session.
            db_obj: Existing user.
            obj_in: Updated user data.
            
        Returns:
            User: Updated user.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            db: Database session.
            username: Username.
            password: Plaintext password.
            
        Returns:
            Optional[User]: User if authentication succeeds, None otherwise.
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """
        Check if a user is active.
        
        Args:
            user: User to check.
            
        Returns:
            bool: True if user is active, False otherwise.
        """
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """
        Check if a user is a superuser.
        
        Args:
            user: User to check.
            
        Returns:
            bool: True if user is a superuser, False otherwise.
        """
        return user.is_superuser


user = CRUDUser(User)