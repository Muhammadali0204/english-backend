from typing import List
from fastapi import Query, APIRouter
from fastapi.responses import JSONResponse

from app.core.deps import CurrentUserDep
from app.models.models import Friendship, User
from app.core.config import CONNECTION_MANAGER
from app.core.enums import FriendshipStatus, WSMessageTypes

from tortoise.expressions import Q

from app.schemas.friends_schema import OutPutMyRequest, OutPutRequest, OutPutUser


router = APIRouter()


@router.get("/all", response_model=List[OutPutUser])
async def get_friends(user: CurrentUserDep):
    friendships = (
        await Friendship.filter(
            Q(requester=user) | Q(receiver=user), status=FriendshipStatus.accepted
        )
        .prefetch_related("requester", "receiver")
        .all()
    )

    friends = []
    for friendship in friendships:
        if friendship.requester_id == user.id:
            friends.append(friendship.receiver)
        else:
            friends.append(friendship.requester)
    return friends


@router.get("/requests", response_model=List[OutPutRequest])
async def get_friends_requests(user: CurrentUserDep):
    requests = (
        await Friendship.filter(receiver=user, status=FriendshipStatus.pending)
        .prefetch_related("requester")
        .all()
    )

    return requests


@router.get("/my-requests", response_model=List[OutPutMyRequest])
async def get_friends_requests(user: CurrentUserDep):
    myrequests = (
        await Friendship.filter(requester=user, status=FriendshipStatus.pending)
        .prefetch_related("receiver")
        .all()
    )

    return myrequests


@router.post("/send-request")
async def send_friend_request(user: CurrentUserDep, user_id: int = Query(...)):
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

    receiver = await User.get_or_none(id=user_id)
    if not receiver:
        return JSONResponse(status_code=404, content={"error": "User not found."})

    await Friendship.create(
        requester=user, receiver=receiver, status=FriendshipStatus.pending
    )

    await CONNECTION_MANAGER.send_message(
        receiver.username, type=WSMessageTypes.RECEIVE_FRIENDSHIP_REQUEST, data={}
    )

    return JSONResponse(status_code=201, content="OK")


@router.post("/cancel-request")
async def cancel_friend_request(user: CurrentUserDep, request_id: int = Query(...)):
    friendship = await Friendship.filter(
        id=request_id, status=FriendshipStatus.pending
    ).first()

    if not friendship:
        return JSONResponse(
            status_code=404, content={"error": "Friend request not found."}
        )

    receiver: User = await friendship.receiver
    await friendship.delete()
    await CONNECTION_MANAGER.send_message(
        receiver.username, type=WSMessageTypes.USER_CANCEL_REQUEST
    )
    return JSONResponse(status_code=200, content="OK")


@router.post("/accept-request")
async def accept_friend_request(user: CurrentUserDep, request_id: int = Query(...)):
    friendship = await Friendship.filter(
        id=request_id, receiver=user, status=FriendshipStatus.pending
    ).first()

    if not friendship:
        return JSONResponse(
            status_code=404, content={"error": "Friend request not found."}
        )

    friendship.status = FriendshipStatus.accepted
    requester: User = await friendship.requester
    await CONNECTION_MANAGER.send_message(
        requester.username, type=WSMessageTypes.ACCEPT_REQUEST,
        data={
            "user": {
                "name": user.name
            }
        }
    )
    await friendship.save()
    return JSONResponse(status_code=200, content="OK")


@router.post("/reject-request")
async def reject_friend_request(user: CurrentUserDep, request_id: int = Query(...)):
    friendship = await Friendship.filter(
        id=request_id, receiver=user, status=FriendshipStatus.pending
    ).first()

    if not friendship:
        return JSONResponse(
            status_code=404, content={"error": "Friend request not found."}
        )

    await friendship.delete()
    receiver: User = await friendship.receiver
    await CONNECTION_MANAGER.send_message(
        receiver.username, type=WSMessageTypes.REJECT_REQUEST, data={
            "user": {
                "name": receiver.name
            }
        }
    )
    return JSONResponse(status_code=200, content="OK")


@router.post("/unfriend")
async def unfriend(user: CurrentUserDep, user_id: int = Query()):
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
        status_code=200,
        content="OK"
    )


@router.get("/search", response_model=List[OutPutUser])
async def search_friends(user: CurrentUserDep, query: str = Query(...)):
    friendship_users = await Friendship.filter(
        Q(requester_id=user.id) | Q(receiver_id=user.id)
    ).values_list("requester_id", "receiver_id")

    related_ids = set()
    for requester_id, receiver_id in friendship_users:
        related_ids.add(requester_id)
        related_ids.add(receiver_id)

    related_ids.add(user.id)

    users = await User.filter(
        username__icontains=query
    ).exclude(id__in=related_ids).limit(10)

    return users
