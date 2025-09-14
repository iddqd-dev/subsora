from fastapi import APIRouter

# Теперь импортируем из локальной папки endpoints
from .endpoints import auth, plans, subscriptions, users, coupons, transactions, referrals, bot, client_auth, misc

# Роутер для версии v1
router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["v1_auth"])
router.include_router(plans.router, prefix="/plans", tags=["v1_plans"])
router.include_router(subscriptions.router, prefix="/subscriptions", tags=["v1_subscriptions"])
router.include_router(users.router, prefix="/users", tags=["v1_users"])
router.include_router(coupons.router, prefix="/coupons", tags=["v1_coupons"])
router.include_router(transactions.router, prefix="/transactions", tags=["v1_transactions"])
router.include_router(referrals.router, prefix="/referrals", tags=["v1_referrals"])
router.include_router(bot.router, prefix="/bot", tags=["v1_bot_gateway"])
router.include_router(client_auth.router, prefix="/client-auth", tags=["v1_client_auth"])
router.include_router(misc.router, prefix="/misc", tags=["v1_misc"])


@router.get("/")
async def root():
    return {"message": "Subsora API is running!", "version": "0.1.0"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "subsora-api"}