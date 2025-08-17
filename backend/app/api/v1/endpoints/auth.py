from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.token import Token
from backend.app.schemas.user import UserCreate, UserRead
from backend.app.models.user import User
from backend.app.core.security import verify_password
from backend.app.core.jwt_ import create_tokens
from backend.app.db.session import get_async_session
from sqlalchemy.future import select
from backend.app import crud

router = APIRouter()


@router.get("/")
async def test():
    return {"message": "Auth endpoint is working"}


@router.post("/register", response_model=UserRead)
async def register(
        user_create: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):
    # Проверяем, существует ли пользователь с таким email
    existing_user = await crud.user.get_user_by_email(db=session, email=user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    referrer = None
    if user_create.referral_code:
        # Ищем пользователя, которому принадлежит этот реферальный код
        result = await session.execute(
            select(User).where(User.referral_code == user_create.referral_code) # type: ignore
        )
        referrer = result.scalars().first()

    # Создаем нового пользователя
    new_user = await crud.user.create(db=session, obj_in=user_create)

    # Если нашли того, кто пригласил, создаем реферальную связь
    if referrer:
        referral_in = {
            "referrer_id": referrer.id,
            "referred_id": new_user.id
        }
        await crud.referral.create(db=session, obj_in=referral_in)

    return new_user


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    # Ищем пользователя по email
    result = await session.execute(select(User).filter_by(email=form_data.username))
    user = result.scalars().first()

    # Проверяем пользователя и пароль
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создаем access token
    tokens = create_tokens(subject=str(user.id))
    return {"token_type": "bearer", **tokens}