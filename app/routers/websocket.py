import asyncio
from fastapi import APIRouter, Query, WebSocket

from app.core.config import CONNECTION_MANAGER
from app.core.deps import get_current_user_from_ws_token


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
            print(f"Received data: {data}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        CONNECTION_MANAGER.disconnect(user.username)
