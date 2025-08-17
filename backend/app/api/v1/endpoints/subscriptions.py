from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, UTC

from backend.app import crud
from backend.app.api.v1 import deps
from backend.app.api.v1.deps import get_current_active_user
from backend.app.schemas.subscription import SubscriptionRead, SubscriptionCreate, SubscriptionCreateRequest
from backend.app.db.session import get_async_session
from backend.app.models.user import User
from backend.app.schemas.transaction import TransactionRead
from backend.app.services.subscription import prepare_purchase

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/", response_model=SubscriptionRead)
async def create_subscription(
        *,
        session: AsyncSession = Depends(get_async_session),
        subscription_request: SubscriptionCreateRequest,  # Используем новую схему
        current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Создает подписку для текущего пользователя.
    Принимает только plan_id, остальное вычисляет на сервере.
    """
    plan = await crud.plan.get(db=session, _id=subscription_request.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=404, detail="Plan not found or not active")

    active_sub = await crud.subscription.get_active_subscription(db=session, user_id=current_user.id)
    if active_sub:
        raise HTTPException(
            status_code=400,
            detail=f"User already has an active subscription until {active_sub.end_date.date()}"
        )

    start_date = datetime.now(UTC)
    end_date = start_date + timedelta(days=plan.duration_days)

    db_subscription_data = SubscriptionCreate(
        user_id=current_user.id,
        plan_id=subscription_request.plan_id,
        end_date=end_date,
        start_date=start_date  # не забываем и start_date
    )

    subscription = await crud.subscription.create(db=session, obj_in=db_subscription_data)

    return subscription

@router.post("/purchase", response_model=TransactionRead)
async def purchase_subscription_start(
    request: SubscriptionCreateRequest,
    user: User = Depends(deps.get_current_user), # get_current_user из deps.py
    db: AsyncSession = Depends(get_async_session)
):
    """Шаг 1: Инициировать покупку подписки."""
    transaction = await prepare_purchase(user, request, db)
    return transaction

@router.get("/my", response_model=List[SubscriptionRead])
async def get_my_subscriptions(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_active_user),
        skip: int = 0,
        limit: int = 100,
):
    """Получить все подписки текущего пользователя"""
    subscriptions = await crud.subscription.get_user_subscriptions(
        db=session, user_id=current_user.id
    )
    return subscriptions[skip:skip + limit]


@router.get("/my/active", response_model=SubscriptionRead)
async def get_my_active_subscription(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_active_user),
):
    """Получить активную подписку текущего пользователя"""
    subscription = await crud.subscription.get_active_subscription_with_details(
        db=session, user_id=current_user.id
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Active subscription not found")
    return subscription


@router.get("/{subscription_id}", response_model=SubscriptionRead)
async def get_subscription(
        subscription_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_active_user),
):
    """Получить подписку по ID (только свою)"""
    subscription = await crud.subscription.get(db=session, _id=subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Проверяем, что подписка принадлежит текущему пользователю
    if subscription.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return subscription