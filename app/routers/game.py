import asyncio
import app.routers
from tkinter import NO
from fastapi import Query, status, APIRouter
from fastapi.responses import JSONResponse
from tortoise.expressions import RawSQL

from app.core.config import CONNECTION_MANAGER, GAMES, settings
from app.core.deps import CurrentUserDep
from app.core.enums import WSMessageTypes
from app.models.models import User, Word
from app.schemas.game_schema import InputUsers
from app.services.game_manager import GameSession


router = APIRouter()


@router.post("/create")
async def create_game(user: CurrentUserDep, credentials: InputUsers):
    has_game = GAMES.get(user.username)
    if has_game:
        return JSONResponse(
            status_code=400, content={"message": "Siz allaqachon o'yin yaratgansiz"}
        )
    users_status = [
        {
            "user": {
                "id": user.id,
                "name": user.name,
                "username": user.username
            },
            "status": True
        }
    ]
    status_count = 0
    for friend in credentials.users:
        friend_data = await User.filter(username=friend).first()
        if friend_data:
            user_status = await CONNECTION_MANAGER.send_message(
                friend,
                type=WSMessageTypes.REQUEST_JOIN_GAME,
                data={
                    "user": {
                        "name": user.name,
                        "username": user.username
                    }
                }
            )
            users_status.append({
                "user": {
                    "id": friend_data.id,
                    "name": friend_data.name,
                    "username": friend_data.username
                },
                "status": user_status
            })
            if user_status:
                status_count += 1
    if status_count < 1:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Online do'stlaringiz yo'q"
            }
        )
    words = await Word.raw(f"SELECT * FROM words ORDER BY RANDOM() LIMIT {settings.ROUND_WORDS_COUNT}")
    GAMES[user.username] = GameSession(
        owner=user,
        owner_ws=CONNECTION_MANAGER.active_connections[user.username],
        words=words,
        round_duration=settings.ROUND_DURATION
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "O'yin yaratildi",
            "game": {
                "owner": user.username,
                "words_len": len(words),
                "round_duration": settings.ROUND_DURATION
            },
            "users_status": users_status
        }
    )


@router.post("/join")
async def join_game(user: CurrentUserDep, username: str = Query(..., alias="game_id")):
    if user.username == username:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": "You are creator that game"}
        )
    game_session: GameSession = GAMES.get(username, None)
    if game_session:
        if game_session.started:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content='Game already started'
            )
        game_session.players.append({
            "user": user,
            "point": 0,
            "ws": CONNECTION_MANAGER.active_connections[user.username],
            "seconds": 0
        })
        users_status = []
        for player in game_session.players:
            user_status = await CONNECTION_MANAGER.send_message(
                player["user"].username,
                type=WSMessageTypes.JOIN_PLAYER,
                data={
                    "user": {
                        "name": user.name,
                        "username": user.username
                    }
                }
            )
            users_status.append({
                "user": {
                    "id": player['user'].id,
                    "name": player['user'].name,
                    "username": player['user'].username
                },
                "status": user_status
            })
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "O'yinga qo'shildingiz",
                "game": {
                    "owner": game_session.owner.username,
                    "words_len": len(game_session.words),
                    "round_duration": game_session.round_duration
                },
                "users_status": users_status
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='GameSession not found'
        )


@router.post('/start')
async def start_game(
    user: CurrentUserDep
):
    game_session: GameSession = GAMES.get(user.username, None)
    if game_session:
        if game_session.started:
            return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content='GameSession already started'
                )
        is_started = await game_session.start_game()
        if is_started:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Game started"
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Game not started"
                }
            )
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='GameSession not found'
        )
