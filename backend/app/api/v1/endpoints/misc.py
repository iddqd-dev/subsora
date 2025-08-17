import aiohttp
import ipaddress
from fastapi import Request, APIRouter, Depends, HTTPException

from backend.app.api.v1 import deps
from backend.app.models import User

router = APIRouter()

@router.get("/geo")  # 👈 Можно добавить сюда response_model для красоты
async def get_geo_info(request: Request, current_user: User = Depends(deps.get_current_active_user)):
    client_host = request.client.host if request.client else "1.1.1.1"
    print('client host:', client_host)
    # Пытаемся получить реальный IP из заголовков, которые мог добавить прокси (Nginx)
    forwarded_for = request.headers.get("x-forwarded-for")
    print('Forwarded for:', forwarded_for)
    if forwarded_for:
        # Берем первый IP из списка
        client_host = forwarded_for.split(",")[0].strip()

    # Проверяем, что IP не локальный
    try:
        is_global = ipaddress.ip_address(client_host).is_global
        ip_to_check = client_host if is_global else "91.108.243.42"  # Fallback на IP Google
    except ValueError:
        ip_to_check = "8.8.8.8"

    url = f"http://ipwho.is/{ip_to_check}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=502, detail="Geo service is unavailable")
                data = await resp.json()
                if not data.get("success", True):  # ipwho.is возвращает success: false при ошибке
                    raise HTTPException(status_code=400, detail=data.get("message", "Invalid IP address"))

                # Возвращаем только нужные поля
                return {
                    "ip": data["ip"],
                    "country": data["country"],
                    "country_code": data["country_code"],
                    "city": data["city"],
                    "lat": data["latitude"],
                    "lon": data["longitude"],
                    "flag": data["flag"]['img'],
                    "emoji": data["flag"]['emoji'],
                    "emoji_unicode": data["flag"]['emoji_unicode'],
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Geo API error: {e}")