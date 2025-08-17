from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


async def database_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Обработчик ошибок базы данных (нарушение ограничений)"""
    logger.error(f"Database error on {request.url}: {exc}")

    # Анализируем тип ошибки для более понятного сообщения
    error_message = "Database constraint violation"

    if "unique constraint" in str(exc).lower():
        error_message = "This record already exists"
    elif "foreign key constraint" in str(exc).lower():
        error_message = "Referenced record does not exist"
    elif "not null constraint" in str(exc).lower():
        error_message = "Required field is missing"

    return JSONResponse(
        status_code=400,
        content={
            "detail": error_message,
            "type": "database_error"
        }
    )


async def validation_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Обработчик ошибок валидации"""
    logger.error(f"Validation error on {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": str(exc),
            "type": "validation_error"
        }
    )


# Кастомные исключения для бизнес-логики
class SubscriptionNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Subscription not found"
        )


class PlanNotActiveError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Plan is not active"
        )


class ActiveSubscriptionExistsError(HTTPException):
    def __init__(self, end_date: str):
        super().__init__(
            status_code=400,
            detail=f"User already has an active subscription until {end_date}"
        )


class CouponInvalidError(HTTPException):
    def __init__(self, reason: str = "Coupon is invalid"):
        super().__init__(
            status_code=400,
            detail=reason
        )