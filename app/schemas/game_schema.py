from pydantic import BaseModel, Field

from app.core.config import settings


class CretaeGameSchema(BaseModel):
    book: int = Field(
        ..., ge=1, le=settings.BOOKS_COUNT
    )
    unit: int = Field(
        ..., ge=1, le=settings.UNITS_IN_ONE_BOOK
    )
