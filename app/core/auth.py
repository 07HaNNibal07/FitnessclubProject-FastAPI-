from passlib.context import CryptContext
import jwt
from jwt import ExpiredSignatureError,InvalidTokenError
from datetime import datetime, timedelta
from .config import settings
from fastapi import HTTPException,status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key,
    algorithm: str = settings.auth_jwt.algorithm,
    access_token_expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
) -> str:
    
    to_encode = payload.copy()
    cur_time = datetime.utcnow()
    to_encode.update(exp=cur_time + timedelta(minutes=access_token_expire_minutes))
    return jwt.encode(to_encode, private_key, algorithm=algorithm)


def decode_jwt(
    token: str,
    public_key: str = settings.auth_jwt.public_key,
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    
    try:
        return jwt.decode(token, public_key, algorithms=[algorithm])
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def create_access_token(payload: dict) -> str:
    payload = payload.copy()
    payload.update({"type": "access"})

    return encode_jwt(
        payload=payload,
        access_token_expire_minutes=settings.auth_jwt.access_token_expire_minutes
    )


def create_refresh_token(payload: dict) -> str:
    payload = payload.copy()
    payload.update({"type": "refresh"})

    expire = datetime.utcnow() + timedelta(days=settings.auth_jwt.refresh_token_expire_days)

    payload.update({"exp": expire})

    return jwt.encode(
        payload,
        settings.auth_jwt.private_key,
        algorithm=settings.auth_jwt.algorithm
    )