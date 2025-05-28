from fastapi.responses import JSONResponse
from fastapi import APIRouter, Query, status

from app.models.models import Word
from app.core.config import settings
from app.core.deps import CurrentUserDep


router = APIRouter()


@router.get("/")
async def get_dictionary():
    """
    Get the dictionary data.
    """

    return {
        "words_count": settings.WORDS_COUNT,
        "words_in_one_unit": settings.WORDS_IN_ONE_UNIT,
        "units_in_one_book": settings.UNITS_IN_ONE_BOOK,
        "books_count": settings.BOOKS_COUNT,
    }


@router.get("/words", status_code=status.HTTP_200_OK)
async def get_words(
    user: CurrentUserDep,
    book: int = Query(1, ge=1, le=settings.BOOKS_COUNT),
    unit: int = Query(1, ge=1, le=settings.UNITS_IN_ONE_BOOK),
):
    """
    Get words for a specific book and unit.
    """
    offset = (book - 1) * settings.UNITS_IN_ONE_BOOK * settings.WORDS_IN_ONE_UNIT + (
        unit - 1
    ) * settings.WORDS_IN_ONE_UNIT
    limit = settings.WORDS_IN_ONE_UNIT

    words = await Word.all().offset(offset).limit(limit).values("data")

    return {
        "book": book,
        "unit": unit,
        "words": words,
    }


@router.post("/complete-unit", status_code=status.HTTP_200_OK)
async def mark_completed_unit(
    user: CurrentUserDep,
    book: int = Query(1, ge=1, le=settings.BOOKS_COUNT),
    unit: int = Query(1, ge=1, le=settings.UNITS_IN_ONE_BOOK),
):
    absolute_unit = (book - 1) * settings.UNITS_IN_ONE_BOOK + unit
    if user.completed_unit >= absolute_unit:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "You have already completed this unit."},
        )
    user.completed_unit = absolute_unit
    await user.save()

    return JSONResponse(status_code=status.HTTP_200_OK, content="Succesful")
