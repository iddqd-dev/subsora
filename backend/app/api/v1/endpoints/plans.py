from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import crud
from backend.app.schemas.plan import PlanRead, PlanCreate, PlanUpdate
from backend.app.db.session import get_async_session
# from app.api import deps # Здесь будут зависимости, например, get_current_active_user

router = APIRouter()

@router.post("/", response_model=PlanRead)
async def create_plan(
    *,
    session: AsyncSession = Depends(get_async_session),
    plan_in: PlanCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser) # Пример защиты
):
    plan = await crud.plan.create(db=session, obj_in=plan_in)
    return plan

@router.get("/", response_model=List[PlanRead])
async def read_plans(
    session: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
):
    plans = await crud.plan.get_multi(db=session, skip=skip, limit=limit)
    return plans

@router.get("/{id}", response_model=PlanRead)
async def read_plan_by_id(
    _id: int,
    session: AsyncSession = Depends(get_async_session),
):
    plan = await crud.plan.get(db=session, id=_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.put("/{id}", response_model=PlanRead)
async def update_plan(
    *,
    session: AsyncSession = Depends(get_async_session),
    _id: int,
    plan_in: PlanUpdate,
):
    plan = await crud.plan.get(db=session, id=_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan = await crud.plan.update(db=session, db_obj=plan, obj_in=plan_in)
    return plan