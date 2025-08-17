# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.ext.asyncio import AsyncSession
# import stripe
# import json
#
# from app.core.config import settings
# from app.db.session import get_async_session
# from app import crud
#
# router = APIRouter()
#
# stripe.api_key = settings.STRIPE_SECRET_KEY
#
#
# @router.post("/stripe")
# async def stripe_webhook(
#         request: Request,
#         db: AsyncSession = Depends(get_async_session)
# ):
#     """Обработка webhook от Stripe"""
#     payload = await request.body()
#     sig_header = request.headers.get('stripe-signature')
#
#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#         )
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid payload")
#     except stripe.error.SignatureVerificationError:
#         raise HTTPException(status_code=400, detail="Invalid signature")
#
#     # Обрабатываем событие
#     if event['type'] == 'payment_intent.succeeded':
#         payment_intent = event['data']['object']
#
#         # Находим транзакцию по payment_intent_id
#         # и обновляем статус подписки
#         # transaction = await crud.transaction.get_by_payment_intent_id(
#         #     db, payment_intent_id=payment_intent['id']
#         # )
#
#     return {"status": "success"}