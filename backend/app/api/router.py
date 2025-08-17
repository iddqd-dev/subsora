from fastapi import APIRouter
from .v1.router import router as v1_router

# Этот роутер будет корневым для всего API
api_router = APIRouter(prefix="/api")

# Подключаем роутер для версии v1
api_router.include_router(v1_router, prefix="/v1")

# Когда появится v2, мы просто добавим здесь еще одну строчку:
# from .v2 import router as v2_router
# api_router.include_router(v2_router, prefix="/v2")