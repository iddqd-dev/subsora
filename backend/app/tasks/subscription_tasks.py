from celery import Celery
from datetime import datetime, timedelta, timezone
from backend.app.db.session import async_session
from backend.app import crud

celery_app = Celery("subsora")


@celery_app.task
async def check_expired_subscriptions():
    """Проверяет истекшие подписки и отправляет уведомления"""
    async with async_session() as db:
        # Находим подписки, которые истекают завтра
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        expiring_subscriptions = await crud.subscription.get_expiring_subscriptions(
            db, expiring_date=tomorrow
        )

        for subscription in expiring_subscriptions:
            # Отправляем email уведомление
            await send_expiration_notification(subscription.user.email)


@celery_app.task
async def send_expiration_notification(email: str):
    """Отправляет уведомление об истечении подписки"""
    # Здесь логика отправки email
    pass