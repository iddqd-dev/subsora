from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.app import crud
from backend.app.api.v1 import deps
from backend.app.db.session import get_async_session
from backend.app.models.user import User
from backend.app.schemas.subscription import SubscriptionRead
from backend.app.schemas.transaction import TransactionRead, TransactionCreate
from backend.app.services.subscription import confirm_purchase

router = APIRouter()

@router.get("/my", response_model=List[TransactionRead])
async def read_my_transactions(
    db: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retrieve transactions for the current user.
    """
    transactions = await crud.transaction.get_user_transactions(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return transactions

@router.get("/all", response_model=List[TransactionRead])
async def read_all_transactions(
    db: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Retrieve all transactions (Admin only).
    """
    transactions = await crud.transaction.get_multi(db, skip=skip, limit=limit)
    return transactions


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
        *,
        db: AsyncSession = Depends(get_async_session),
        transaction_in: TransactionCreate,
        current_user: User = Depends(deps.get_current_active_superuser)  # <--- Только для админов!
):
    """
    Create a new transaction. (Admin only)

    This endpoint is for administrative purposes. Transactions for users
    should be created as part of a larger business process, e.g., creating a subscription.
    """
    # Проверим, существует ли пользователь, для которого создается транзакция
    user = await crud.user.get(db, _id=transaction_in.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {transaction_in.user_id} not found."
        )

    # (Опционально) Проверим, существует ли подписка, если указан subscription_id
    if transaction_in.subscription_id:
        subscription = await crud.subscription.get(db, _id=transaction_in.subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=404,
                detail=f"Subscription with id {transaction_in.subscription_id} not found."
            )

    transaction = await crud.transaction.create(db, obj_in=transaction_in)
    return transaction


@router.post("/{transaction_id}/confirm_payment_mock", response_model=SubscriptionRead)
async def confirm_payment_endpoint_mock(
    transaction_id: int,
    db: AsyncSession = Depends(get_async_session),
    # Для теста можно защитить админом или вообще убрать защиту
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Шаг 2 (МОК): Подтвердить оплату и создать подписку.
    Имитирует webhook от платежной системы.
    """
    subscription = await confirm_purchase(transaction_id, db)
    return subscription