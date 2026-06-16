from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.rebar import (
    RebarLapLengthInput,
    RebarLinearInput,
    RebarMeshInput,
    RebarStirrupsInput,
)
from app.services.rebar_service import (
    calculate_rebar_lap_length_v2,
    calculate_rebar_linear_v2,
    calculate_rebar_mesh_v2,
    calculate_rebar_stirrups_v2,
)

router = APIRouter(prefix="/rebar", tags=["Rebar"])


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


@router.post("/linear/v2", response_model=CalculationResult)
def rebar_linear_v2(
    data: RebarLinearInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_rebar_linear_v2(data=data)
    _persist(db, current_user.id, "rebar_linear_v2", data, response)
    return response


@router.post("/mesh/v2", response_model=CalculationResult)
def rebar_mesh_v2(
    data: RebarMeshInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_rebar_mesh_v2(data=data)
    _persist(db, current_user.id, "rebar_mesh_v2", data, response)
    return response


@router.post("/stirrups/v2", response_model=CalculationResult)
def rebar_stirrups_v2(
    data: RebarStirrupsInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_rebar_stirrups_v2(data=data)
    _persist(db, current_user.id, "rebar_stirrups_v2", data, response)
    return response


@router.post("/lap-length/v2", response_model=CalculationResult)
def rebar_lap_length_v2(
    data: RebarLapLengthInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_rebar_lap_length_v2(data=data)
    _persist(db, current_user.id, "rebar_lap_length_v2", data, response)
    return response
