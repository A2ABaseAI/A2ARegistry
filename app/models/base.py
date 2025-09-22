"""Base database model."""

from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


class BaseModel:
    """Base class for all database models."""

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}  # type: ignore


Base = declarative_base(cls=BaseModel)
