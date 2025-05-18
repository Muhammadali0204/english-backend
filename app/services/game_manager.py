import asyncio
import datetime
from typing import Dict, List
from fastapi import WebSocket
from app.models.models import User
from app.core.enums import GameStatus
from datetime import datetime as innerdatetime, timedelta


class GameSession:

    def __init__(
        self,
        owner: User,
        owner_ws: WebSocket,
        question_words: List[str],
        answer_words: List[str],
        round_duration: int,
    ):
        self.players = {
            owner.username: {
                "user": owner,
                "point": 0,
                "ws": owner_ws,
                "seconds": 0
            }
        }
        self.owner = owner
        self.question_words = question_words
        self.answer_words = answer_words
        self.current_word_id = 0
        self.game_status = GameStatus.pending
        self.round_duration = round_duration
        self.running_task = None
        self.answered_players = set()
        self.lock = asyncio.Lock()
    
    async def start_game(self):
        if len(self.players) > 1:
            async with self.lock:
                self.game_status = GameStatus.active
                self.running_task = asyncio.create_task(self.round_timer_loop())
        else:
            return False
    
    async def round_timer_loop(self):
        async with self.lock:
            await self.broadcast(
                'game start',
                {
                    'users_count': len(self.players),
                    'words_count': len(self.question_words)
                }
            )
        for question_word, index in enumerate(self.question_words):
            async with self.lock:
                self.answered_players = set()
                self.current_word_id = index
                self.current_question = question_word
                self.current_deadline = innerdatetime.now(datetime.timezone.utc) + timedelta(seconds=self.round_duration)

            await asyncio.sleep(self.round_duration)

            async with self.lock:
                ...

    async def submit_answer(self, user_id: str, word: str):
        async with self.lock:
            now = datetime.utcnow()
            if now > self.current_deadline:
                await self.send_to(user_id, "Too late! Time's up.")
                return
            if user_id in self.answered_players:
                await self.send_to(user_id, "You already answered this round.")
                return

            if word.lower() == self.current_word.lower():
                self.players[user_id]["score"] += 1
                self.answered_players.add(user_id)
                await self.send_to(user_id, "Correct! You got 1 point.")
            else:
                await self.send_to(user_id, "Incorrect.")

    async def end_game(self):
        self.started = False
        sorted_scores = sorted(self.players.items(), key=lambda x: x[1]["score"], reverse=True)
        winner = sorted_scores[0][1]["username"] if sorted_scores else "No one"
        if self.running_task:
            self.running_task.cancel()

    async def broadcast(self, type: str, data: Dict):
        for player in self.players:
            await self.send_to(
                player,
                type=type,
                data=data
            )

    async def send_to(self, player, type: str, data: Dict):
        ws: WebSocket = player['ws']
        try:
            await ws.send_json(
                {
                    'type': type,
                    'data': data
                }
            )
        except:
            pass
