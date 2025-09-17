from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from backend.app import crud
from backend.app.db.session import get_async_session
from backend.app.core.jwt_ import create_tokens, decode_token
from backend.app.schemas.token import Token
from backend.app.schemas.telegram import TelegramLoginData  # Создадим эту схему
from backend.app.services.telegram_validator import validate_telegram_hash  # Создадим этот сервис
from backend.app.core.config import settings

router = APIRouter()
oauth2_scheme_client = OAuth2PasswordBearer(tokenUrl="/api/v1/client/auth/refresh")  # Указываем на свой эндпоинт


@router.post("/telegram", response_model=Token)
async def login_via_telegram(
        tg_data: TelegramLoginData,
        db: AsyncSession = Depends(get_async_session)
):
    """Аутентификация для внешних клиентов (Flutter, бот) через Telegram."""
    if not validate_telegram_hash(tg_data.model_dump(), settings.TELEGRAM_BOT_TOKEN):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram data hash")

    db_user = await crud.user.get_by_telegram_id(db, telegram_id=tg_data.id)
    if not db_user:
        db_user = await crud.user.create_from_telegram(db, obj_in=tg_data)

    tokens = create_tokens(subject=db_user.id)
    return {"token_type": "bearer", **tokens}


@router.post("/refresh", response_model=Token)
async def refresh_client_token(
        token: str = Depends(oauth2_scheme_client),
        db: AsyncSession = Depends(get_async_session)
):
    """Обновление access/refresh токенов для внешних клиентов."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expected 'refresh' token")

    user_id = payload.get("sub")
    user = await crud.user.get(db, _id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    tokens = create_tokens(subject=user.id)
    return {"token_type": "bearer", **tokens}
