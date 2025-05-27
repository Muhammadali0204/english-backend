from typing import List
from pydantic import BaseModel, Field

from app.core.config import settings


class InputUsers(BaseModel):
    users: List
