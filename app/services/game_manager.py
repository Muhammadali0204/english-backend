import asyncio
import datetime
from typing import Dict, List
from fastapi import WebSocket
from app.core.config import GAMES
from app.models.models import User, Word
from app.core.enums import GameStatus, WSMessageTypes
from datetime import datetime as innerdatetime, timedelta


class GameSession:
    def __init__(
        self,
        owner: User,
        owner_ws: WebSocket,
        words: List[dict],
        round_duration: int,
    ):
        self.players = [
            {"user": owner, "point": 0, "ws": owner_ws, "seconds": 0}
        ]
        self.owner = owner
        self.words: List[Word] = words
        self.current_word_id = 0
        self.game_status = GameStatus.pending
        self.round_duration = round_duration
        self.started = False
        self.running_task = None
        self.answered_players = set()
        self.lock = asyncio.Lock()

    def broadcast(self, type: str, data: Dict):
        for player in self.players:
            self.send_to(player['ws'], type=type, data=data)

    def send_to(self, ws: WebSocket, type: str, data: Dict = {}):
        try:
            asyncio.create_task(ws.send_json({"type": type, "data": data}))
        except:
            pass

    async def start_game(self):
        if len(self.players) > 1:
            async with self.lock:
                self.game_status = GameStatus.active
                self.running_task = asyncio.create_task(self.round_timer_loop())
        else:
            return False

    async def round_timer_loop(self):
        self.broadcast(
            WSMessageTypes.GAME_STARTED,
            {
                "users_count": len(self.players),
            },
        )
        await asyncio.sleep(3)
        for index, word in enumerate(self.words):
            async with self.lock:
                self.started = True
                self.answered_players = set()
                self.current_word = word.data
                self.current_deadline = innerdatetime.now(
                    datetime.timezone.utc
                ) + timedelta(seconds=self.round_duration)
            self.broadcast(
                type=WSMessageTypes.NEXT_WORD,
                data={
                    "index": index,
                    "word": word.data['uz']
                }
            )

            await asyncio.sleep(self.round_duration)

            async with self.lock:
                for player in self.players:
                    if player['user'].username not in self.answered_players:
                        player['seconds'] += self.round_duration
        await self.end_game()


    async def submit_answer(self, ws: WebSocket, username: str, word: str):
        async with self.lock:
            now = datetime.datetime.now(datetime.timezone.utc)
            if username in self.answered_players:
                self.send_to(ws, type=WSMessageTypes.ALREADY_ANSWERED)
                return

            player = next((p for p in self.players if p["user"].username == username), None)
            if not player:
                return

            if word.lower() in self.current_word['en']:
                player["point"] += 1
                player['seconds'] += (now - self.current_deadline).seconds
                self.answered_players.add(username)
                self.send_to(ws, type=WSMessageTypes.CORRECT_ANSWER)
            else:
                self.send_to(ws, type=WSMessageTypes.INCORRECT_ANSWER)
                player['seconds'] += (now - self.current_deadline).seconds
                self.answered_players.add(username)

    async def end_game(self):
        self.started = False
        players = [{
            "user": {
                "id": player['user'].id,
                "name": player['user'].name,
                "username": player['user'].username
            },
            "point": player['point'],
            "seconds": player['seconds']
        } for player in self.players]
        sorted_players = sorted(players, key=lambda x: (-x["point"], x["seconds"]))
        self.broadcast(
            type=WSMessageTypes.END_GAME,
            data={
                "result": sorted_players
            }
        )
        GAMES.pop(self.owner.username)
        if self.running_task:
            self.running_task.cancel()
