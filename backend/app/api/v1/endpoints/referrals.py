from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import crud
from backend.app.api.v1 import deps
from backend.app.core.config import settings
from backend.app.db.session import get_async_session
from backend.app.models.user import User
from backend.app.schemas.referral import ReferralRead, ReferralTierResponse

router = APIRouter()

@router.get("/my", response_model=List[ReferralRead])
async def read_my_referrals(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get a list of users referred by the current user.
    """
    referrals = await crud.referral.get_user_referrals(db, referrer_id=current_user.id)
    return referrals

@router.get("/my/code")
async def get_my_referral_code(
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get the referral code of the current user.
    """
    # Предполагается, что реферальный код генерируется при регистрации
    # или по первому запросу и сохраняется в модели User.
    return {"referral_code": current_user.referral_code}


# 2. Указываем в декораторе, что эндпоинт вернет список таких моделей
@router.get("/tiers", response_model=List[ReferralTierResponse])
def get_referral_tiers():
    """
    Get a list of referral tiers.
    """
    tiers_as_dicts = [
        {"referrals": referrals, "discount": discount}
        for referrals, discount in settings.REFERRAL_TIERS
    ]

    return tiers_as_dicts