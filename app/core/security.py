import bcrypt
import datetime
from jose import jwt
from app.core.config import settings
from datetime import datetime as innerdatetime, timedelta


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    if not password:
        return False
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hashed password."""
    if not hashed or not password:
        return False
    if not isinstance(password, str) or not isinstance(hashed, str):
        return False
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
) -> str:
    """Create a JWT token with an expiration time."""

    to_encode = data.copy()
    expire = innerdatetime.now(datetime.timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
