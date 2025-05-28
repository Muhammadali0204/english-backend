from fastapi import APIRouter, Query, WebSocket

from app.core.enums import WSMessageTypes
from app.core.config import CONNECTION_MANAGER, GAMES
from app.core.deps import get_current_user_from_ws_token
from app.services.game_manager import GameSession


router = APIRouter()


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    if not token:
        await websocket.close(code=4000)
    try:
        user = await get_current_user_from_ws_token(token=token)
    except ValueError:
        await websocket.close(code=1008)
        return

    await CONNECTION_MANAGER.connect(user.username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data['type'] == WSMessageTypes.SEND_ANSWER:
                try :
                    game_session: GameSession = GAMES.get(data['data']['game_username'])
                    if game_session:
                        await game_session.submit_answer(
                            websocket,
                            user.username,
                            data['data']['answer']
                        )
                except:
                    pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        CONNECTION_MANAGER.disconnect(user.username)
