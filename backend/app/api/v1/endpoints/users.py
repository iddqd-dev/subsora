from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import crud
from backend.app.core.security import verify_password
from backend.app.schemas.user import UserRead, UserUpdate, UserUpdatePassword
from backend.app.db.session import get_async_session
from backend.app.api.v1 import deps
from backend.app.models.user import User
from backend.app.schemas.vpn import VpnStats
from backend.app.services.vpn_manager import VpnManager

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
):
    """Получить информацию о текущем пользователе"""
    return current_user

@router.put("/me", response_model=UserRead)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_async_session),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Обновить информацию о текущем пользователе"""
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_user_password(
        *,
        db: AsyncSession = Depends(get_async_session),
        password_in: UserUpdatePassword,
        current_user: User = Depends(deps.get_current_active_user),
):
    """
    Смена пароля текущего пользователя.
    """
    # 1. Проверяем старый пароль
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль",
        )

    # 2. Проверяем, что новый пароль не совпадает со старым (опционально)
    if password_in.current_password == password_in.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый пароль не может совпадать со старым",
        )

    # 3. Обновляем
    await crud.user.update_password(
        db, db_obj=current_user, new_password=password_in.new_password
    )

    return {"message": "Пароль успешно изменен"}

@router.get("/", response_model=List[UserRead])
async def read_users(
    db: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Получить список всех пользователей (только для админов)"""
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserRead)
async def read_user_by_id(
    user_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(get_async_session),
):
    """Получить пользователя по ID (только для админов)"""
    user = await crud.user.get(db, _id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/me/vpn-stats", response_model=VpnStats)
async def read_user_vpn_stats(
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Получает актуальную статистику использования VPN из Marzban для текущего пользователя.
    """
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot fetch VPN stats for user without an email."
        )

    try:
        async with VpnManager() as vpn:
            stats = await vpn.get_user_stats(username=current_user.email)
            return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not fetch stats from VPN panel: {e}"
        )