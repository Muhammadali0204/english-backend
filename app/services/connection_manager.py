from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        print(f"User {username} connected.")

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)
        print(f"User {username} disconnected.")

    async def send_message(self, username: str, type: str, data: Dict = {}):
        ws = self.active_connections.get(username)
        if ws:
            try:
                await ws.send_json(
                    {"type": type, "data": data}
                )
                return True
            except:
                return False
