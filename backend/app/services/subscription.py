from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
import time  # 👈 Импортируем time
import logging  # 👈 Импортируем logging

from backend.app import crud
from backend.app.core.config import settings
from backend.app.models import User, Plan, Subscription, Transaction, Referral
from backend.app.schemas.subscription import SubscriptionCreateRequest
from fastapi import HTTPException
from backend.app.services.vpn_manager import VpnManager

async def prepare_purchase(
        user: User,
        request: SubscriptionCreateRequest,
        db: AsyncSession
) -> Transaction:
    """
    Шаг 1: Подготовка к покупке.
    - Проверяет все условия (активная подписка, план, купон).
    - Рассчитывает финальную стоимость со всеми скидками.
    - Создает транзакцию со статусом 'pending'.
    - Возвращает созданную транзакцию.
    """
    # ... (все твои проверки на активную подписку и план, они остаются здесь) ...
    await db.execute(
        select(User).where(User.id == user.id).with_for_update()
    )

    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,  # type: ignore
            Subscription.end_date > now
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User already has an active subscription")

    pending_result = await db.execute(
        select(Transaction)
        .where(
            Transaction.user_id == user.id,
            Transaction.plan_id == request.plan_id,
            Transaction.status == "pending"
        )
        .order_by(Transaction.created_at.desc())
        .limit(1)
    )
    existing_pending = pending_result.scalars().first()
    if existing_pending:
        return existing_pending

    plan = await db.get(Plan, request.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=404, detail="Plan not found or inactive")

    # --- Расчет скидки (остается здесь) ---
    coupon_discount = 0.0
    referral_discount = 0.0

    coupon_to_use = None
    if request.coupon_code:
        coupon = await crud.coupon.validate_coupon(db, code=request.coupon_code)
        if not coupon:
            raise HTTPException(status_code=400, detail="Coupon is not valid or has expired")
        coupon_discount = coupon.discount_percent
        coupon_to_use = coupon  # Сохраняем объект купона

    num_referrals = await crud.referral.count_user_referrals(db, referrer_id=user.id)  # type: ignore

    for required_referrals, discount_percent in settings.REFERRAL_TIERS:
        if num_referrals >= required_referrals:
            referral_discount = discount_percent
            break

    final_discount_percent = max(coupon_discount, referral_discount)
    final_amount = plan.price * (1 - final_discount_percent / 100)

    # --- Создание PENDING транзакции ---
    transaction = Transaction(
        user_id=user.id,
        plan_id=plan.id,
        amount=final_amount,
        status="pending",
        currency=request.currency or "USD",
    )
    db.add(transaction)

    # Если купон был использован (т.е. его скидка была максимальной)
    if coupon_to_use and coupon_discount >= referral_discount:
        coupon_to_use.uses += 1
        db.add(coupon_to_use)

    await db.commit()
    await db.refresh(transaction)

    return transaction


async def confirm_purchase(
        transaction_id: int,
        db: AsyncSession
) -> Subscription:
    """
    Шаг 2: Подтверждение покупки.
    - Находит 'pending' транзакцию.
    - Меняет ее статус на 'completed'.
    - Создает подписку в Subsora.
    - **Создает/обновляет пользователя в Marzban.**
    - Сохраняет ссылку на подключение.
    - Возвращает созданную подписку.
    """
    logging.basicConfig(filename='main.log', filemode='w', level=logging.DEBUG)

    start_time = time.time()
    logging.info(f"[{transaction_id}] - Purchase confirmation started.")


    # 1. Находим транзакцию и связанный с ней план
    result = await db.execute(
        select(Transaction, Plan)
        .join(Plan, Transaction.plan_id == Plan.id) # type: ignore
        .where(Transaction.id == transaction_id)
    )
    res = result.first()
    if not res:
        raise HTTPException(status_code=404, detail="Transaction not found")

    time_after_db_select = time.time()
    logging.info(f"[{transaction_id}] - DB Select finished in: {time_after_db_select - start_time:.4f}s")

    transaction, plan = res

    if transaction.status != "pending":
        raise HTTPException(status_code=400, detail="Transaction is not pending")

    # 2. Меняем статус транзакции
    transaction.status = "completed"

    # 3. Создаем подписку в базе Subsora
    now = datetime.now(timezone.utc)
    new_sub = Subscription(
        user_id=transaction.user_id,
        plan_id=transaction.plan_id,
        start_date=now,
        end_date=now + timedelta(days=plan.duration_days),
    )
    db.add(new_sub)
    await db.flush()  # Получаем ID для new_sub перед коммитом

    # 4. Связываем транзакцию с новой подпиской
    transaction.subscription_id = new_sub.id

    # 5. 👇 --- НОВАЯ ЛОГИКА: Работа с VPN ---
    # Получаем объект пользователя, для которого создается подписка
    user = await crud.user.get(db, _id=transaction.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User for this transaction not found")

    time_before_vpn = time.time()
    logging.info(f"[{transaction_id}] - Starting VPN provisioning...")

    try:
        # Создаем экземпляр VpnManager и вызываем метод provision_user
        async with VpnManager() as vpn:
            vpn_data = await vpn.provision_user(user=user, plan=plan)
            # Сохраняем полученную ссылку на подключение в нашей базе
            user.subscription_url = vpn_data['subscription_url']
            db.add(user)
    except Exception as e:
        # ВАЖНО: Если что-то пошло не так с Marzban, мы должны откатить транзакцию
        # и сообщить об ошибке, чтобы не получилось, что деньги списаны, а VPN не выдан.
        await db.rollback()
        raise HTTPException(status_code=503, detail=f"VPN service unavailable: {e}")

    time_after_vpn = time.time()
    logging.info(f"[{transaction_id}] - VPN provisioning finished in: {time_after_vpn - time_before_vpn:.4f}s")

    # 6. Коммитим все изменения в базу (статус транзакции, новая подписка, ссылка для юзера)
    await db.commit()

    time_after_commit = time.time()
    logging.info(f"[{transaction_id}] - DB Commit finished in: {time_after_commit - time_after_vpn:.4f}s")

    end_time = time.time()
    logging.info(f"[{transaction_id}] - Purchase confirmation finished. Total time: {end_time - start_time:.4f}s")

    # 7. Возвращаем созданную подписку с "жадной" загрузкой деталей
    full_subscription = await crud.subscription.get(db, _id=new_sub.id)
    if not full_subscription:
        raise HTTPException(status_code=500, detail="Could not retrieve created subscription")

    return full_subscription


async def revoke_subscription(
        subscription_id: int,
        db: AsyncSession,
) -> Subscription:
    """
    Отзывает подписку:
    - завершает её немедленно (end_date = now),
    - убирает пользователя из рантайма Xray (revoke доступа),
    - НЕ удаляет ни пользователя, ни историю подписок/транзакций из БД.
    """
    subscription = await crud.subscription.get(db, _id=subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    user = await crud.user.get(db, _id=subscription.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User for this subscription not found")

    now = datetime.now(timezone.utc)
    if subscription.end_date > now:
        subscription.end_date = now
        db.add(subscription)

    async with VpnManager() as vpn:
        # Отзываем доступ в рантайме, не трогая сущность пользователя.
        await vpn.drop_user_from_xray_runtime(user)

    await db.commit()
    await db.refresh(subscription)
    return subscription


async def delete_user_completely(
        user_id: int,
        db: AsyncSession,
) -> None:
    """
    Полное удаление пользователя:
    - удаляет пользователя из рантайма Xray,
    - удаляет все его подписки, транзакции и реферальные связи,
    - удаляет саму запись пользователя из БД.
    """
    user = await crud.user.get(db, _id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Чистим рантайм Xray (если нужно полностью снести доступ)
    async with VpnManager() as vpn:
        await vpn.drop_user_from_xray_runtime(user)

    # 2. Удаляем реферальные связи
    await db.execute(
        delete(Referral).where(
            or_(
                Referral.referrer_id == user_id,
                Referral.referred_id == user_id,
            )
        )
    )

    # 3. Удаляем транзакции пользователя
    await db.execute(delete(Transaction).where(Transaction.user_id == user_id))

    # 4. Удаляем подписки пользователя
    await db.execute(delete(Subscription).where(Subscription.user_id == user_id))

    # 5. Удаляем самого пользователя
    await db.delete(user)

    await db.commit()
