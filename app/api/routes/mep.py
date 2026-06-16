from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.mep import (
    ElectricalLoadBasicInput,
    HeatLossBasicInput,
    PipeVolumeInput,
)
from app.services.mep_service import (
    calculate_electrical_load_basic_v2,
    calculate_heat_loss_basic_v2,
    calculate_pipe_volume_v2,
)

router = APIRouter(prefix="/mep", tags=["MEP"])


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


@router.post("/hvac/heat-loss-basic/v2", response_model=CalculationResult)
def hvac_heat_loss_basic_v2(
    data: HeatLossBasicInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_heat_loss_basic_v2(data=data)
    _persist(db, current_user.id, "mep_hvac_heat_loss_basic_v2", data, response)
    return response


@router.post("/electrical/load-basic/v2", response_model=CalculationResult)
def electrical_load_basic_v2(
    data: ElectricalLoadBasicInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_electrical_load_basic_v2(data=data)
    _persist(db, current_user.id, "mep_electrical_load_basic_v2", data, response)
    return response


@router.post("/plumbing/pipe-volume/v2", response_model=CalculationResult)
def plumbing_pipe_volume_v2(
    data: PipeVolumeInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_pipe_volume_v2(data=data)
    _persist(db, current_user.id, "mep_plumbing_pipe_volume_v2", data, response)
    return response
