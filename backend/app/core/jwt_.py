from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import HTTPException, status
from backend.app.core.config import settings


def create_tokens(subject: str | Any) -> Dict[str, str]:
    """
    Создает ЕДИНУЮ пару access и refresh токенов для ЛЮБОГО клиента.
    """
    now = datetime.now(timezone.utc)

    # Access Token
    access_expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_payload = {"exp": access_expire, "sub": str(subject), "type": "access"}
    access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Refresh Token
    refresh_expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_payload = {"exp": refresh_expire, "sub": str(subject), "type": "refresh"}
    refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return {"access_token": access_token, "refresh_token": refresh_token}


def decode_token(token: str) -> Dict[str, Any]:
    """
    Декодирует ЛЮБОЙ токен и возвращает payload, проверяя срок жизни.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
