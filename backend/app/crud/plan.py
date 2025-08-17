from backend.app.crud.base import CRUDBase
from backend.app.models.plan import Plan
from backend.app.schemas.plan import PlanCreate, PlanUpdate

class CRUDPlan(CRUDBase[Plan, PlanCreate, PlanUpdate]):
    # TODO: Здесь можно добавлять специфичные для планов методы
    pass

plan = CRUDPlan(Plan)