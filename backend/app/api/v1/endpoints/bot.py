from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

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

# --- Зависимость для проверки секретного токена ---
async def verify_bot_token(x_bot_token: str = Header(..., description="Секретный токен для аутентификации бота")):
    print(x_bot_token)
    print(settings.TELEGRAM_BOT_SECRET)
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
    # response_model=... # <- пока оставим без модели ответа для простоты
    dependencies=[Depends(verify_bot_token)]
)
async def register_user_and_grant_trial(
        user_data: UserCreateFromTelegram,
        db: AsyncSession = Depends(get_async_session)
):
    """
    Регистрирует нового пользователя из Telegram и выдает ему триальную подписку.
    """
    # 1. Проверяем, не существует ли уже пользователь
    existing_user = await crud.user.get_by_telegram_id(db, telegram_id=user_data.telegram_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this Telegram ID already exists."
        )

    # 2. Находим триальный тарифный план в базе
    plan_result = await db.execute(
        select(Plan).where(Plan.name.ilike('%пробный%'))
    )
    trial_plan = plan_result.scalars().first()
    if not trial_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trial plan not found in the database."
        )

    # 3. Создаем нового пользователя
    new_user = await crud.user.create_from_telegram(db, obj_in=user_data)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create a new user."
        )

    # 4. Имитируем процесс покупки для этого пользователя и триального плана
    try:
        # Шаг 1: Создаем "pending" транзакцию (она будет с нулевой суммой)
        purchase_request = SubscriptionCreateRequest(plan_id=trial_plan.id)
        pending_transaction = await prepare_purchase(user=new_user, request=purchase_request, db=db)

        # Шаг 2: Сразу же "подтверждаем" эту транзакцию
        final_subscription = await confirm_purchase(transaction_id=pending_transaction.id, db=db)

    except Exception as e:
        # Если что-то пошло не так, откатываем создание пользователя, чтобы избежать "мусора"
        await db.rollback()
        # Можно даже удалить пользователя, если он успел создаться
        # await db.delete(new_user)
        # await db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to grant trial subscription: {e}"
        )

    # 5. Возвращаем успешный результат
    # Можно вернуть созданную подписку или просто сообщение об успехе
    return {
        "message": "User successfully registered and trial granted.",
        "user_id": new_user.id,
        "subscription": final_subscription
    }