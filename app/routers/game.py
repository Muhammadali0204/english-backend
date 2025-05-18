from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.core.config import CONNECTIONS, GAMES, settings
from app.core.deps import CurrentUserDep
from app.models.models import Word
from app.schemas.game_schema import CretaeGameSchema
from app.services.game_manager import GameSession


router = APIRouter()


@router.post("/create")
async def create_game(
    user: CurrentUserDep,
    credentials: CretaeGameSchema
):
    has_game = GAMES.get(user.username, {})
    if has_game != {}:
        return JSONResponse(
            status_code=400, content={"message": "You already have a game"}
        )
    offset = (credentials.book - 1) * settings.UNITS_IN_ONE_BOOK * settings.WORDS_IN_ONE_UNIT + (credentials.unit - 1)*settings.WORDS_IN_ONE_UNIT
    words = await Word.all().offset(offset).limit(settings.WORDS_IN_ONE_UNIT)
    GAMES[user.username] = GameSession(
        owner=user,
        owner_ws=CONNECTIONS.active_connections,
        
    )


@router.post("/join")
async def join_game(
    user: CurrentUserDep,
    username: str = Query(..., alias='game_id')
):
    if user.username == username:
        return JSONResponse(
            status_code=400, content={"message": "You are creator that game"}
        )
    
