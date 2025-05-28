from typing import List
from pydantic import BaseModel


class InputUsers(BaseModel):
    users: List
