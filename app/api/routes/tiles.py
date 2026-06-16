from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.calculation_result import CalculationResult
from app.schemas.tiles import (
    TilesAdhesiveInput,
    TilesFloorInput,
    TilesGroutInput,
    TilesWallInput,
)
from app.services.tiles_service import (
    calculate_tiles_adhesive_v2,
    calculate_tiles_floor_v2,
    calculate_tiles_grout_v2,
    calculate_tiles_wall_v2,
)

router = APIRouter(prefix="/tiles", tags=["Tiles"])


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


@router.post("/floor/v2", response_model=CalculationResult)
def tiles_floor_v2(
    data: TilesFloorInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_tiles_floor_v2(data=data)
    _persist(db, current_user.id, "tiles_floor_v2", data, response)
    return response


@router.post("/wall/v2", response_model=CalculationResult)
def tiles_wall_v2(
    data: TilesWallInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_tiles_wall_v2(data=data)
    _persist(db, current_user.id, "tiles_wall_v2", data, response)
    return response


@router.post("/adhesive/v2", response_model=CalculationResult)
def tiles_adhesive_v2(
    data: TilesAdhesiveInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_tiles_adhesive_v2(data=data)
    _persist(db, current_user.id, "tiles_adhesive_v2", data, response)
    return response


@router.post("/grout/v2", response_model=CalculationResult)
def tiles_grout_v2(
    data: TilesGroutInput,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    response = calculate_tiles_grout_v2(data=data)
    _persist(db, current_user.id, "tiles_grout_v2", data, response)
    return response
