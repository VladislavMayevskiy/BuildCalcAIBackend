from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.concrete import ConcreteMixInput, ConcreteVolumeInput
from app.services.concrete_service import (
    calculate_concrete_mix_materials_v2,
    calculate_concrete_volume_v2,
)

router = APIRouter(prefix="/concrete", tags=["Concrete"])


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


@router.post("/volume/v2", response_model=CalculationResult)
def concrete_volume_v2(
    data: ConcreteVolumeInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_concrete_volume_v2(data=data)
    _persist(db, current_user.id, "concrete_volume_v2", data, response)
    return response


@router.post("/mix-materials/v2", response_model=CalculationResult)
def concrete_mix_materials_v2(
    data: ConcreteMixInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_concrete_mix_materials_v2(data=data)
    _persist(db, current_user.id, "concrete_mix_materials_v2", data, response)
    return response
