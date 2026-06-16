from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.walls import WallBlocksInput, WallBricksInput, WallMortarInput
from app.services.walls_service import (
    calculate_wall_blocks_v2,
    calculate_wall_bricks_v2,
    calculate_wall_mortar_v2,
)

router = APIRouter(prefix="/walls", tags=["Walls"])


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


@router.post("/blocks/v2", response_model=CalculationResult)
def wall_blocks_v2(
    data: WallBlocksInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_wall_blocks_v2(data=data)
    _persist(db, current_user.id, "walls_blocks_v2", data, response)
    return response


@router.post("/bricks/v2", response_model=CalculationResult)
def wall_bricks_v2(
    data: WallBricksInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_wall_bricks_v2(data=data)
    _persist(db, current_user.id, "walls_bricks_v2", data, response)
    return response


@router.post("/mortar/v2", response_model=CalculationResult)
def wall_mortar_v2(
    data: WallMortarInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_wall_mortar_v2(data=data)
    _persist(db, current_user.id, "walls_mortar_v2", data, response)
    return response
