from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pydantic import ValidationError
from app import oauth2
from app.oauth2 import get_current_user
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.models.project import Project
from app.schemas.calculation import CalculationHistoryResponse, CalculationInput, CalculationResponse
from app.schemas.calculation_result import CalculationResult
from app.schemas.estimate import EstimateResult
from app.services.calculation_service import calculate_room, calculate_room_v2
from app.services.estimate_service import generate_estimate_from_calculation

router = APIRouter(tags=["Calculation"])


@router.get("/calculations/history", response_model=list[CalculationHistoryResponse])
def get_calculation_history(
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    history = db.query(Calculation).filter(Calculation.user_id == current_user.id).all()
    return history


@router.post("/calculate", response_model=CalculationResponse)
def calculate(
    data: CalculationInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    try:
        response = calculate_room(data)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    calculation = Calculation(
        user_id=current_user.id,
        room_project_id=None,
        calculation_type="room_calculation",
        input_data=data.model_dump(),
        result_data=response.model_dump(),
    )
    db.add(calculation)
    db.commit()
    return response


@router.post("/calculate/v2", response_model=CalculationResult)
def calculate_v2(
    data: CalculationInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    try:
        response = calculate_room_v2(data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    calculation = Calculation(
        user_id=current_user.id,
        room_project_id=None,
        calculation_type="room_calculation_v2",
        input_data=data.model_dump(),
        result_data=response.model_dump(),
    )

    db.add(calculation)
    db.commit()
    db.refresh(calculation)

    return response


@router.post("/calculations/{calculation_id}/estimate", response_model=EstimateResult)
def calculate_estimate(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    calculation = (
        db.query(Calculation)
        .filter(
            Calculation.id == calculation_id,
            Calculation.user_id == current_user.id,
        )
        .first()
    )

    if calculation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    if not calculation.calculation_type.endswith("_v2"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estimate is available only for v2 calculations.",
        )

    try:
        calculation_result = CalculationResult.model_validate(
            calculation.result_data
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stored calculation result has invalid format for estimate generation.",
        )

    estimate_calculation = generate_estimate_from_calculation(
        calculation_result=calculation_result
    )

    return estimate_calculation