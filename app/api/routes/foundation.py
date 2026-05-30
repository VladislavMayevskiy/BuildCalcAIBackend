from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.slab_foundation import SlabFoundationInput
from app.schemas.strip_foundation import StripFoundationInput, StripFoundationResponse
from app.services.slab_foundation_service import calculate_slab_foundation_v2
from app.services.strip_foundation_service import calculate_strip_foundation, calculate_strip_foundation_v2

router = APIRouter(prefix="/foundation", tags=["Foundation"])


@router.post("/strip", response_model=StripFoundationResponse)
def strip_foundation(
    data: StripFoundationInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_strip_foundation(data=data)
    calculation = Calculation(
        user_id=current_user.id,
        room_project_id=None,
        calculation_type="strip_foundation",
        input_data=data.model_dump(),
        result_data=response.model_dump(),
    )
    db.add(calculation)
    db.commit()
    db.refresh(calculation)

    return response


@router.post("/strip/v2", response_model=CalculationResult)
def strip_foundation_v2(
    data: StripFoundationInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_strip_foundation_v2(data=data)
    calculation = Calculation(
        user_id=current_user.id,
        room_project_id=None,
        calculation_type="strip_foundation_v2",
        input_data=data.model_dump(),
        result_data=response.model_dump(),
    )
    db.add(calculation)
    db.commit()
    db.refresh(calculation)

    return response


@router.post("/slab/v2", response_model=CalculationResult)
def slab_foundation_v2(
    data: SlabFoundationInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_slab_foundation_v2(data=data)
    calculation = Calculation(
        user_id=current_user.id,
        room_project_id=None,
        calculation_type="slab_foundation_v2",
        input_data=data.model_dump(),
        result_data=response.model_dump(),
    )
    db.add(calculation)
    db.commit()
    db.refresh(calculation)

    return response

