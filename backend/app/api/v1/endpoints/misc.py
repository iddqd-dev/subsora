import aiohttp
import ipaddress

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1 import deps
from backend.app.core.jwt_ import create_tokens
from backend.app.core.security import hash_password
from backend.app.db.session import get_async_session
from backend.app.models import User
from backend.app.schemas.bootstrap import BootstrapAdminCreate, BootstrapStatus
from backend.app.schemas.token import Token

router = APIRouter()


@router.get("/bootstrap-status", response_model=BootstrapStatus)
async def bootstrap_status(
    db: AsyncSession = Depends(get_async_session),
):
    users_count_result = await db.execute(select(func.count(User.id)))
    users_count = users_count_result.scalar_one()
    return BootstrapStatus(needs_bootstrap=users_count == 0)


@router.post("/bootstrap-admin", response_model=Token)
async def bootstrap_admin(
    payload: BootstrapAdminCreate,
    db: AsyncSession = Depends(get_async_session),
):
    users_count_result = await db.execute(select(func.count(User.id)))
    users_count = users_count_result.scalar_one()
    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bootstrap already completed",
        )

    existing_user_result = await db.execute(select(User).where(User.email == payload.email))
    if existing_user_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    db_user = User(
        email=payload.email,
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        is_active=True,
        is_superuser=True,
    )
    db_user.generate_referral_code()
    db.add(db_user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bootstrap already completed",
        )

    await db.refresh(db_user)
    tokens = create_tokens(subject=str(db_user.id))
    return {"token_type": "bearer", **tokens}


@router.get("/geo")
async def get_geo_info(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
):
    client_host = request.client.host if request.client else "1.1.1.1"
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_host = forwarded_for.split(",")[0].strip()

    try:
        is_global = ipaddress.ip_address(client_host).is_global
        ip_to_check = client_host if is_global else "91.108.243.42"
    except ValueError:
        ip_to_check = "8.8.8.8"

    url = f"http://ipwho.is/{ip_to_check}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=502, detail="Geo service is unavailable")
                data = await resp.json()
                if not data.get("success", True):
                    raise HTTPException(
                        status_code=400,
                        detail=data.get("message", "Invalid IP address"),
                    )

                return {
                    "ip": data["ip"],
                    "country": data["country"],
                    "country_code": data["country_code"],
                    "city": data["city"],
                    "lat": data["latitude"],
                    "lon": data["longitude"],
                    "flag": data["flag"]["img"],
                    "emoji": data["flag"]["emoji"],
                    "emoji_unicode": data["flag"]["emoji_unicode"],
                }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Geo API error: {exc}")
