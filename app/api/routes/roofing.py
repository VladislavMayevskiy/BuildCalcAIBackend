from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.roofing import (
    RoofAreaInput,
    RoofCoveringInput,
    RoofGuttersInput,
    RoofInsulationInput,
    RoofMembraneInput,
)
from app.services.roofing_service import (
    calculate_roof_area_v2,
    calculate_roof_covering_v2,
    calculate_roof_gutters_v2,
    calculate_roof_insulation_v2,
    calculate_roof_membrane_v2,
)

router = APIRouter(prefix="/roof", tags=["Roofing"])


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
def roof_area_v2(
    data: RoofAreaInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_roof_area_v2(data=data)
    _persist(db, current_user.id, "roof_area_v2", data, response)
    return response


@router.post("/covering/v2", response_model=CalculationResult)
def roof_covering_v2(
    data: RoofCoveringInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_roof_covering_v2(data=data)
    _persist(db, current_user.id, "roof_covering_v2", data, response)
    return response


@router.post("/membrane/v2", response_model=CalculationResult)
def roof_membrane_v2(
    data: RoofMembraneInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_roof_membrane_v2(data=data)
    _persist(db, current_user.id, "roof_membrane_v2", data, response)
    return response


@router.post("/insulation/v2", response_model=CalculationResult)
def roof_insulation_v2(
    data: RoofInsulationInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_roof_insulation_v2(data=data)
    _persist(db, current_user.id, "roof_insulation_v2", data, response)
    return response


@router.post("/gutters/v2", response_model=CalculationResult)
def roof_gutters_v2(
    data: RoofGuttersInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_roof_gutters_v2(data=data)
    _persist(db, current_user.id, "roof_gutters_v2", data, response)
    return response
