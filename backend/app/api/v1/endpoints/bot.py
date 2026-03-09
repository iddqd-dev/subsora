from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select
from sqlalchemy import or_

from backend.app import crud
from backend.app.db.session import get_async_session
from backend.app.core.config import settings
from backend.app.models import Plan
from backend.app.schemas.subscription import SubscriptionCreateRequest
from backend.app.schemas.user import UserCreateFromTelegram
from backend.app.services.subscription import prepare_purchase, confirm_purchase
from backend.app.services.vpn_manager import VpnManager # Наш VPN-менеджер
# Возможно, понадобятся схемы для ответа
# from backend.app.schemas.bot import BotUserProfileResponse

router = APIRouter()

class BotPurchaseRequest(BaseModel):
    telegram_id: int
    plan_id: int

# --- Зависимость для проверки секретного токена ---
async def verify_bot_token(x_bot_token: str = Header(..., description="Секретный токен для аутентификации бота")):
    if x_bot_token != settings.TELEGRAM_BOT_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid bot token")

# --- Эндпоинты для Бота ---

@router.get(
    "/profile/{telegram_id}",
    # response_model=BotUserProfileResponse, # <- Добавим схему ответа позже
    dependencies=[Depends(verify_bot_token)] # 👈 Защищаем эндпоинт
)
async def get_user_profile_by_telegram_id(
    telegram_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получает полный профиль пользователя для Telegram-бота.
    Включает данные из Subsora DB и статус из Marzban.
    """
    print('Getting user profile by telegram id:', telegram_id)
    # 1. Ищем пользователя в нашей основной базе по telegram_id
    user = await crud.user.get_by_telegram_id(db, telegram_id=telegram_id)
    if not user:
        # Если пользователь не найден, бот должен будет предложить ему зарегистрироваться
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this Telegram ID not found in Subsora")

    # 2. Получаем его активную подписку из нашей базы
    active_subscription = await crud.subscription.get_active_subscription_with_details(db, user_id=user.id)

    # 3. (Опционально, но полезно) Получаем актуальные данные из Marzban
    vpn_stats = None
    if user.email: # Используем email как username в Marzban
        try:
            async with VpnManager() as vpn:
                # Здесь нужно будет реализовать метод get_user_stats в vpn_manager
                # vpn_stats = await vpn.get_user_stats(username=user.email)
                pass # Пока пропустим, чтобы не усложнять
        except Exception as e:
            # Не страшно, если Marzban недоступен, вернем данные из нашей БД
            print(f"Could not fetch stats from Marzban: {e}")

    # 4. Собираем и возвращаем полный ответ
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "telegram_id": user.telegram_id,
            "referral_code": user.referral_code,
            "subscription_url": user.subscription_url,
        },
        "active_subscription": active_subscription, # Может быть None, если подписки нет
        "vpn_stats": vpn_stats # Может быть None
    }


@router.post(
    "/register-trial",
    dependencies=[Depends(verify_bot_token)]
)
async def register_user_and_grant_trial(
        user_data: UserCreateFromTelegram,
        db: AsyncSession = Depends(get_async_session)
):
    """
    Регистрирует пользователя (если нет) и выдает триал (если не было подписок).
    """
    # 1. Ищем пользователя или создаем нового
    user = await crud.user.get_by_telegram_id(db, telegram_id=user_data.telegram_id)
    if not user:
        user = await crud.user.create_from_telegram(db, obj_in=user_data)

    # 2. Проверяем, не пользовался ли он уже сервисом (защита от абуза)
    # Получаем все подписки пользователя (и активные, и архивные)
    user_subs = await crud.subscription.get_user_subscriptions(db, user_id=user.id)
    if user_subs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trial period already used or user has history."
        )

    # 3. Ищем подходящий тарифный план
    # Ищем план с ценой 0 ИЛИ с именем, содержащим "пробный"/"trial"
    query = select(Plan).where(
        Plan.is_active == True,
        or_(
            Plan.price == 0,
            Plan.name.ilike('%пробный%'),
            Plan.name.ilike('%trial%'),
            Plan.name.ilike('%free%')
        )
    ).order_by(Plan.price)  # Берем самый дешевый (бесплатный)

    plan_result = await db.execute(query)
    trial_plan = plan_result.scalars().first()

    if not trial_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No trial plan configured in database (create a plan with price 0)."
        )

    # 4. Выдаем подписку
    try:
        # Создаем транзакцию
        req = SubscriptionCreateRequest(plan_id=trial_plan.id)
        transaction = await prepare_purchase(user=user, request=req, db=db)

        # Подтверждаем транзакцию (активация VPN)
        final_subscription = await confirm_purchase(transaction_id=transaction.id, db=db)

    except Exception as e:
        await db.rollback()
        print(f"Error granting trial: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to activate VPN: {e}"
        )

    return {
        "message": "Trial granted successfully.",
        "user_id": user.id,
        "subscription": final_subscription
    }


@router.post("/grant-subscription", dependencies=[Depends(verify_bot_token)])
async def grant_subscription_via_bot(
        data: BotPurchaseRequest,
        db: AsyncSession = Depends(get_async_session)
):
    """Выдать подписку пользователю (например, после оплаты вручную или через бота)"""
    user = await crud.user.get_by_telegram_id(db, telegram_id=data.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan = await crud.plan.get(db, _id=data.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Создаем транзакцию и сразу подтверждаем
    req = SubscriptionCreateRequest(plan_id=plan.id)
    # prepare_purchase вернет ошибку, если уже есть активная подписка - это ок
    transaction = await prepare_purchase(user=user, request=req, db=db)
    sub = await confirm_purchase(transaction_id=transaction.id, db=db)

    return {"status": "success", "subscription_id": sub.id}


@router.get(
    "/plans",
    dependencies=[Depends(verify_bot_token)]
)
async def get_active_plans(
        db: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает список активных тарифных планов для бота.
    Сортирует по цене (от дешевых к дорогим).
    """
    # Выбираем только активные планы (is_active=True)
    # Сортируем по цене, чтобы в боте они шли по возрастанию
    query = select(Plan).where(Plan.is_active == True).order_by(Plan.price)

    result = await db.execute(query)
    plans = result.scalars().all()

    # Возвращаем список. FastAPI сам сериализует SQLAlchemy модели в JSON
    return {"plans": plans}