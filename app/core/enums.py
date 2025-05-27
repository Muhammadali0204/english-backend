from enum import Enum


class FriendshipStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"


class GameStatus(str, Enum):
    pending = "pending"
    active = "active"
    finished = "finished"


class WSMessageTypes(str, Enum):

    # Friend
    RECEIVE_FRIENDSHIP_REQUEST = "receive_friendship_request"
    USER_CANCEL_REQUEST = "user_cancel_request"
    ACCEPT_REQUEST = "accept_request"
    REJECT_REQUEST = "reject_request"
    REQUEST_JOIN_GAME = 'request_join_game'

    # Game
    GAME_STARTED = 'game_started'
    NEXT_WORD = 'next_word'
    ALREADY_ANSWERED = 'already_answered'
    CORRECT_ANSWER = 'correct_answer'
    INCORRECT_ANSWER = 'incorrect_answer'
    JOIN_PLAYER = 'join_player'
    SEND_ANSWER = 'send_answer'
    END_GAME = 'end_game'
