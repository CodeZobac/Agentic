"""
Base CRUD operations for the Agentic backend.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.database import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize with SQLAlchemy model class.
        
        Args:
            model: The SQLAlchemy model class.
        """
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            db: Database session.
            id: Record ID.
            
        Returns:
            Optional[ModelType]: Record if found, None otherwise.
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            db: Database session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List[ModelType]: List of records.
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session.
            obj_in: Schema with data to create.
            
        Returns:
            ModelType: Created record.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        
        Args:
            db: Database session.
            db_obj: Existing record to update.
            obj_in: Schema or dict with data to update.
            
        Returns:
            ModelType: Updated record.
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Remove a record.
        
        Args:
            db: Database session.
            id: Record ID.
            
        Returns:
            ModelType: Removed record.
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj