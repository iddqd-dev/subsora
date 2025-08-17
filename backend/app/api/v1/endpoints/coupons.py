from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import crud
from backend.app.api.v1 import deps
from backend.app.db.session import get_async_session
from backend.app.models.user import User
from backend.app.schemas.coupon import CouponCreate, CouponRead

router = APIRouter()


@router.post("/", response_model=CouponRead, status_code=status.HTTP_201_CREATED)
async def create_coupon(
        *,
        db: AsyncSession = Depends(get_async_session),
        coupon_in: CouponCreate,
        current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Create a new coupon (Admin only).
    """
    coupon = await crud.coupon.create(db, obj_in=coupon_in)
    return coupon


@router.get("/{code}", response_model=CouponRead)
async def get_coupon_by_code(
        *,
        code: str,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get a specific coupon by its code. Can be used to validate a coupon.
    """
    coupon = await crud.coupon.get_by_code(db, code=code)
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")

    # Дополнительная проверка на валидность (можно вынести в сервис)
    if not coupon.is_active or coupon.uses >= coupon.max_uses:
        raise HTTPException(status_code=400, detail="Coupon is not valid or has expired")

    return coupon


@router.get("/", response_model=List[CouponRead])
async def read_coupons(
        db: AsyncSession = Depends(get_async_session),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Retrieve all coupons (Admin only).
    """
    coupons = await crud.coupon.get_multi(db, skip=skip, limit=limit)
    return coupons