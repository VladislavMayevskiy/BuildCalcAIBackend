from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.facade import (
    FacadeAreaInput,
    FacadeInsulationInput,
    FacadePaintInput,
    FacadePlasterInput,
)
from app.services.facade_service import (
    calculate_facade_area_v2,
    calculate_facade_insulation_v2,
    calculate_facade_paint_v2,
    calculate_facade_plaster_v2,
)

router = APIRouter(prefix="/facade", tags=["Facade"])


def _persist(db: Session, user_id: int, calculation_type: str, data, response) -> None:
    calculation = Calculation(
        user_id=user_id,
        room_project_id=None,
        calculation_type=calculation_type,
        input_data=data.model_dump(),
        result_data=response.model_dump(),
    )
    db.add(calculation)
    db.commit()
    db.refresh(calculation)


@router.post("/area/v2", response_model=CalculationResult)
def facade_area_v2(
    data: FacadeAreaInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_facade_area_v2(data=data)
    _persist(db, current_user.id, "facade_area_v2", data, response)
    return response


@router.post("/insulation/v2", response_model=CalculationResult)
def facade_insulation_v2(
    data: FacadeInsulationInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_facade_insulation_v2(data=data)
    _persist(db, current_user.id, "facade_insulation_v2", data, response)
    return response


@router.post("/plaster/v2", response_model=CalculationResult)
def facade_plaster_v2(
    data: FacadePlasterInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_facade_plaster_v2(data=data)
    _persist(db, current_user.id, "facade_plaster_v2", data, response)
    return response


@router.post("/paint/v2", response_model=CalculationResult)
def facade_paint_v2(
    data: FacadePaintInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_facade_paint_v2(data=data)
    _persist(db, current_user.id, "facade_paint_v2", data, response)
    return response
