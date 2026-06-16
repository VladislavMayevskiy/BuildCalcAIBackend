from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.earthworks import BackfillInput, ExcavationInput, TrenchInput
from app.services.earthworks_service import (
    calculate_backfill_v2,
    calculate_excavation_v2,
    calculate_trench_v2,
)

router = APIRouter(prefix="/earthworks", tags=["Earthworks"])


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


@router.post("/excavation/v2", response_model=CalculationResult)
def excavation_v2(
    data: ExcavationInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_excavation_v2(data=data)
    _persist(db, current_user.id, "earthworks_excavation_v2", data, response)
    return response


@router.post("/trench/v2", response_model=CalculationResult)
def trench_v2(
    data: TrenchInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_trench_v2(data=data)
    _persist(db, current_user.id, "earthworks_trench_v2", data, response)
    return response


@router.post("/backfill/v2", response_model=CalculationResult)
def backfill_v2(
    data: BackfillInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_backfill_v2(data=data)
    _persist(db, current_user.id, "earthworks_backfill_v2", data, response)
    return response
