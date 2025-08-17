from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from backend.app.core.jwt_ import decode_token
from backend.app.db.session import get_async_session
from backend.app import crud
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_async_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        # 👇 Добавляем проверку, что это именно access токен
        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except (JWTError, HTTPException):  # Ловим и свои исключения
        raise credentials_exception

    user = await crud.user.get(db, _id=int(user_id))
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    # Здесь можно добавить проверку на is_active если добавите это поле в модель User
    return current_user


# Функция для проверки суперпользователя (опционально)
async def get_current_active_superuser(
        current_user: User = Depends(get_current_user)
) -> User:
    # Здесь нужно добавить поле is_superuser в модель User
    # if not current_user.is_superuser:
    #     raise HTTPException(
    #         status_code=400, detail="The user doesn't have enough privileges"
    #     )
    return current_user