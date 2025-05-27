from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import settings
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    auth_exception = HTTPException(status_code=401, detail="Authentication is required")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        username = payload.get("sub")
        if not username:
            raise auth_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

    user = await User.get_or_none(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
) -> Optional[User]:
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        username = payload.get("username")
        if not username:
            return None
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None

    user = await User.get_or_none(username=username)
    return user


OptionalUserDep = Annotated[Optional[User], Depends(get_optional_user)]


async def get_current_user_from_ws_token(token: str) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if not username:
            raise ValueError("Invalid token payload")
    except ExpiredSignatureError:
        raise ValueError("Token expired")
    except JWTError:
        raise ValueError("Invalid token")

    user = await User.get_or_none(username=username)
    if not user:
        raise ValueError("User not found")

    return user
