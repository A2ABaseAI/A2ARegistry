"""Common Pydantic schemas."""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")


class SuccessResponse(BaseModel):
    """Success response schema."""
    
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    total_count: Optional[int] = Field(None, description="Total number of items")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema."""
    
    items: list[T] = Field(..., description="List of items")
    pagination: PaginationParams = Field(..., description="Pagination information")
    total_count: int = Field(..., description="Total number of items")
