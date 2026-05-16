from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    APIKeyHeader,
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app.models import User
from app.schemas import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db),
) -> User:
    """Authenticate via Bearer token OR X-API-Key header."""

    # Try API key first
    if api_key:
        user = db.query(User).filter(User.api_key == api_key).first()
        if user and user.is_active:
            return user

    # Try JWT token
    if token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception

        user = db.query(User).filter(User.username == token_data.username).first()
        if user is None or not user.is_active:
            raise credentials_exception
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Provide a Bearer token or X-API-Key header.",
        headers={"WWW-Authenticate": "Bearer"},
    )
