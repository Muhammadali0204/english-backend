from enum import Enum


class FriendshipStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    blocked = "blocked"


class GameStatus(str, Enum):
    pending = "pending"
    active = "active"
    finished = 'finished'
