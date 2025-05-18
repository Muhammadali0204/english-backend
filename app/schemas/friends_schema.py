from pydantic import BaseModel

from app.core.enums import FriendshipStatus


class OutPutUser(BaseModel):
    id: int
    username: str
    name: str

    class Config:
        from_attributes = True


class OutPutRequest(BaseModel):
    id: int
    requester: OutPutUser
    status: FriendshipStatus
