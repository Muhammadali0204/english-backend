from typing import List
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from app.core.deps import CurrentUserDep
from app.core.enums import FriendshipStatus
from app.models.models import Friendship, User

from tortoise.expressions import Q

from app.schemas.friends_schema import OutPutRequest, OutPutUser


router = APIRouter()


@router.get("/all", response_model=List[OutPutUser])
async def get_friends(user: CurrentUserDep):
    friendships = await Friendship.filter(
        Q(requester=user) | Q(receiver=user), status=FriendshipStatus.accepted
    ).prefetch_related("requester", "receiver").all()

    friends = []
    for friendship in friendships:
        if friendship.requester_id == user.id:
            friends.append(friendship.receiver)
        else:
            friends.append(friendship.requester)
    return friends


@router.get("/requests", response_model=List[OutPutRequest])
async def get_friends_requests(user: CurrentUserDep):
    requests = await Friendship.filter(
        receiver=user, status=FriendshipStatus.pending
    ).prefetch_related("requester").all()

    return requests


@router.post("/send-request/{user_id}")
async def send_friend_request(user: CurrentUserDep, user_id: int):
    if user.id == user_id:
        return JSONResponse(
            status_code=400,
            content={"error": "You cannot send a friend request to yourself."},
        )

    existing_request = await Friendship.filter(
        (Q(requester=user) & Q(receiver_id=user_id))
        | (Q(requester_id=user_id) & Q(receiver=user))
    ).first()

    if existing_request:
        return JSONResponse(
            status_code=400, content={"error": "Friend request already exists."}
        )

    reciever = await Friendship.filter(id=user_id).first()
    if not reciever:
        return JSONResponse(status_code=404, content={"error": "User not found."})

    await Friendship.create(
        requester=user, receiver=reciever, status=FriendshipStatus.pending
    )
    return JSONResponse(
        status_code=201,
        content='OK'
    )


@router.post("/cancel-request/{user_id}")
async def cancel_friend_request(user: CurrentUserDep, user_id: int):
    if user.id == user_id:
        return JSONResponse(
            status_code=400,
            content={"error": "You cannot cancel a friend request to yourself."},
        )

    friendship = await Friendship.filter(
        requester=user, receiver_id=user_id, status=FriendshipStatus.pending
    ).first()

    if not friendship:
        return JSONResponse(
            status_code=404, content={"error": "Friend request not found."}
        )

    await friendship.delete()
    return JSONResponse(
        status_code=204,
        content='OK'
    )


@router.post("/accept-request/{request_id}")
async def accept_friend_request(user: CurrentUserDep, request_id: int):
    friendship = await Friendship.filter(
        id=request_id, receiver=user, status=FriendshipStatus.pending
    ).first()

    if not friendship:
        return JSONResponse(
            status_code=404, content={"error": "Friend request not found."}
        )

    friendship.status = FriendshipStatus.accepted
    await friendship.save()
    return JSONResponse(
        status_code=200,
        content='OK'
    )


@router.post("/reject-request/{request_id}")
async def reject_friend_request(user: CurrentUserDep, request_id: int):
    friendship = await Friendship.filter(
        id=request_id, receiver=user, status=FriendshipStatus.pending
    ).first()

    if not friendship:
        return JSONResponse(
            status_code=404, content={"error": "Friend request not found."}
        )

    await friendship.delete()
    return JSONResponse(
        status_code=204,
        content='OK'
    )


@router.post("/unfriend/{user_id}")
async def unfriend(user: CurrentUserDep, user_id: int):
    if user.id == user_id:
        return JSONResponse(
            status_code=400, content={"error": "You cannot unfriend yourself."}
        )

    friendship = await Friendship.filter(
        (Q(requester=user) & Q(receiver_id=user_id))
        | (Q(requester_id=user_id) & Q(receiver=user)),
        status=FriendshipStatus.accepted,
    ).first()

    if not friendship:
        return JSONResponse(status_code=404, content={"error": "Friendship not found."})

    await friendship.delete()
    return JSONResponse(
        status_code=204,
        content='OK'
    )


@router.post("/block/{user_id}")
async def block_user(user: CurrentUserDep, user_id: int):
    if user.id == user_id:
        return JSONResponse(
            status_code=400, content={"error": "You cannot block yourself."}
        )
    friendship = await Friendship.filter(
        (Q(requester=user) & Q(receiver_id=user_id))
        | (Q(requester_id=user_id) & Q(receiver=user)),
        status=FriendshipStatus.accepted,
    ).first()

    if not friendship:
        return JSONResponse(status_code=404, content={"error": "Friendship not found."})

    friendship.status = FriendshipStatus.blocked
    await friendship.save()

    return JSONResponse(
        status_code=204,
        content='OK'
    )


@router.get("/search", response_model=List[OutPutUser])
async def search_friends(user: CurrentUserDep, username: str):
    users = (
        await User.filter(username__icontains=username).exclude(id=user.id).limit(10)
    )
    return users
