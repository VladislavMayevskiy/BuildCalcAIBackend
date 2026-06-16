from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.floors import FloorInsulationInput, FloorLaminateInput, FloorScreedInput
from app.services.floors_service import (
    calculate_floor_insulation_v2,
    calculate_floor_laminate_v2,
    calculate_floor_screed_v2,
)

router = APIRouter(prefix="/floors", tags=["Floors"])


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


@router.post("/screed/v2", response_model=CalculationResult)
def floor_screed_v2(
    data: FloorScreedInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_floor_screed_v2(data=data)
    _persist(db, current_user.id, "floors_screed_v2", data, response)
    return response


@router.post("/insulation/v2", response_model=CalculationResult)
def floor_insulation_v2(
    data: FloorInsulationInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_floor_insulation_v2(data=data)
    _persist(db, current_user.id, "floors_insulation_v2", data, response)
    return response


@router.post("/laminate/v2", response_model=CalculationResult)
def floor_laminate_v2(
    data: FloorLaminateInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_floor_laminate_v2(data=data)
    _persist(db, current_user.id, "floors_laminate_v2", data, response)
    return response
