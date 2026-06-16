from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.estimate import (
    AggregateMaterialsInput,
    FromCalculationsInput,
    MaterialAggregationResult,
)
from app.services.estimate_service import aggregate_materials

router = APIRouter(prefix="/estimates", tags=["Estimates"])


@router.post("/aggregate-materials/v2", response_model=MaterialAggregationResult)
def aggregate_materials_v2(
    data: AggregateMaterialsInput,
    current_user: Users = Depends(oauth2.get_current_user),
):
    return aggregate_materials(data.calculations)


@router.post("/from-calculations/v2", response_model=MaterialAggregationResult)
def aggregate_from_calculations_v2(
    data: FromCalculationsInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    calculations = (
        db.query(Calculation)
        .filter(
            Calculation.user_id == current_user.id,
            Calculation.id.in_(data.calculation_ids),
        )
        .all()
    )

    found_ids = {calculation.id for calculation in calculations}
    missing = [cid for cid in data.calculation_ids if cid not in found_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calculations not found: {missing}",
        )

    results: list[CalculationResult] = []
    for calculation in calculations:
        try:
            results.append(CalculationResult.model_validate(calculation.result_data))
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Calculation {calculation.id} is not a v2 CalculationResult and cannot be aggregated.",
            )

    return aggregate_materials(results)
