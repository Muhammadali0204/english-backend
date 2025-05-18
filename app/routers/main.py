from fastapi import APIRouter

from app.routers import auth, dictionary, friends, game, websocket


router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authorization"])
router.include_router(dictionary.router, prefix="/dict", tags=["Dictionary"])
router.include_router(friends.router, prefix="/friends", tags=["Friends"])
router.include_router(game.router, prefix="/game", tags=["Game"])
router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
