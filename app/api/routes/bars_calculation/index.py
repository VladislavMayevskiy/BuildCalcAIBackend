from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app import oauth2
from app.database import get_db
from app.models.ai_chat import AIChat
from app.models.ai_request_log import AIRequestLog
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.bars_calculation.index import BarsCalculationInput, BarsCalculationResponse
from app.services.bars_calculation.index import bars_calculation_service
from app.services.ai_prompt_service import build_calculation_explanation_prompt, build_ai_chat_prompt
from app.services.openai_service import generate_ai_response

router = APIRouter(prefix="/rebar", tags=["Rebar"])

@router.post("/calculation", response_model=BarsCalculationResponse)
def bars_calculation(data: BarsCalculationInput, current_user: Users = Depends(oauth2.get_current_user)):
    response = bars_calculation_service(data=data)
    return response