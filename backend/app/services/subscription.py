from datetime import datetime, timedelta, timezone
import logging
import time

from fastapi import HTTPException
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import crud
from backend.app.core.config import settings
from backend.app.models import Plan, Referral, Subscription, Transaction, User
from backend.app.schemas.subscription import SubscriptionCreateRequest
from backend.app.services.vpn_manager import VpnManager


async def prepare_purchase(
    user: User,
    request: SubscriptionCreateRequest,
    db: AsyncSession,
) -> Transaction:
    """Step 1. Validate and create a pending transaction."""
    # Serialize purchase creation per user to avoid duplicate pending rows.
    await db.execute(select(User).where(User.id == user.id).with_for_update())

    now = datetime.now(timezone.utc)
    active_sub_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,  # type: ignore
            Subscription.end_date > now,
        )
    )
    if active_sub_result.scalars().first():
        raise HTTPException(status_code=400, detail="User already has an active subscription")

    # Idempotency: if the latest request already created pending transaction for the same plan, reuse it.
    pending_result = await db.execute(
        select(Transaction)
        .where(
            Transaction.user_id == user.id,
            Transaction.plan_id == request.plan_id,
            Transaction.status == "pending",
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

    coupon_discount = 0.0
    referral_discount = 0.0

    coupon_to_use = None
    if request.coupon_code:
        coupon = await crud.coupon.validate_coupon(db, code=request.coupon_code)
        if not coupon:
            raise HTTPException(status_code=400, detail="Coupon is not valid or has expired")
        coupon_discount = coupon.discount_percent
        coupon_to_use = coupon

    num_referrals = await crud.referral.count_user_referrals(db, referrer_id=user.id)  # type: ignore

    for required_referrals, discount_percent in settings.REFERRAL_TIERS:
        if num_referrals >= required_referrals:
            referral_discount = discount_percent
            break

    final_discount_percent = max(coupon_discount, referral_discount)
    final_amount = plan.price * (1 - final_discount_percent / 100)

    transaction = Transaction(
        user_id=user.id,
        plan_id=plan.id,
        amount=final_amount,
        status="pending",
        currency=request.currency or "USD",
    )
    db.add(transaction)

    if coupon_to_use and coupon_discount >= referral_discount:
        coupon_to_use.uses += 1
        db.add(coupon_to_use)

    await db.commit()
    await db.refresh(transaction)
    return transaction


async def confirm_purchase(
    transaction_id: int,
    db: AsyncSession,
) -> Subscription:
    """Step 2. Confirm pending transaction, create subscription, provision VPN."""
    logging.basicConfig(filename="main.log", filemode="w", level=logging.DEBUG)

    start_time = time.time()
    logging.info("[%s] - Purchase confirmation started.", transaction_id)

    # Lock transaction row to avoid double-confirm under concurrency.
    result = await db.execute(
        select(Transaction, Plan)
        .join(Plan, Transaction.plan_id == Plan.id)  # type: ignore
        .where(Transaction.id == transaction_id)
        .with_for_update()
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")

    logging.info(
        "[%s] - DB Select finished in: %.4fs",
        transaction_id,
        time.time() - start_time,
    )

    transaction, plan = row

    # Idempotency for repeated confirms.
    if transaction.status == "completed" and transaction.subscription_id:
        existing_subscription = await crud.subscription.get(db, _id=transaction.subscription_id)
        if existing_subscription:
            return existing_subscription

    if transaction.status != "pending":
        raise HTTPException(status_code=400, detail="Transaction is not pending")

    # Lock user row and re-check active subscription before creating a new one.
    await db.execute(select(User).where(User.id == transaction.user_id).with_for_update())
    now = datetime.now(timezone.utc)
    active_sub_result = await db.execute(
        select(Subscription)
        .where(
            Subscription.user_id == transaction.user_id,  # type: ignore
            Subscription.end_date > now,
        )
        .order_by(Subscription.end_date.desc())
        .limit(1)
    )
    if active_sub_result.scalars().first():
        transaction.status = "failed"
        await db.commit()
        raise HTTPException(status_code=409, detail="User already has an active subscription")

    transaction.status = "completed"

    new_sub = Subscription(
        user_id=transaction.user_id,
        plan_id=transaction.plan_id,
        start_date=now,
        end_date=now + timedelta(days=plan.duration_days),
    )
    db.add(new_sub)
    await db.flush()

    transaction.subscription_id = new_sub.id

    user = await crud.user.get(db, _id=transaction.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User for this transaction not found")

    vpn_start = time.time()
    logging.info("[%s] - Starting VPN provisioning...", transaction_id)

    try:
        async with VpnManager() as vpn:
            vpn_data = await vpn.provision_user(user=user, plan=plan)
            user.subscription_url = vpn_data["subscription_url"]
            db.add(user)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=503, detail=f"VPN service unavailable: {exc}")

    logging.info(
        "[%s] - VPN provisioning finished in: %.4fs",
        transaction_id,
        time.time() - vpn_start,
    )

    await db.commit()
    logging.info("[%s] - Purchase confirmation finished. Total time: %.4fs", transaction_id, time.time() - start_time)

    full_subscription = await crud.subscription.get(db, _id=new_sub.id)
    if not full_subscription:
        raise HTTPException(status_code=500, detail="Could not retrieve created subscription")
    return full_subscription


async def revoke_subscription(
    subscription_id: int,
    db: AsyncSession,
) -> Subscription:
    """End subscription immediately and revoke runtime access in Xray."""
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
        await vpn.drop_user_from_xray_runtime(user)

    await db.commit()
    await db.refresh(subscription)
    return subscription


async def delete_user_completely(
    user_id: int,
    db: AsyncSession,
) -> None:
    """Delete user access from runtime and remove all related DB data."""
    user = await crud.user.get(db, _id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    async with VpnManager() as vpn:
        await vpn.drop_user_from_xray_runtime(user)

    await db.execute(
        delete(Referral).where(
            or_(
                Referral.referrer_id == user_id,
                Referral.referred_id == user_id,
            )
        )
    )
    await db.execute(delete(Transaction).where(Transaction.user_id == user_id))
    await db.execute(delete(Subscription).where(Subscription.user_id == user_id))
    await db.delete(user)
    await db.commit()
