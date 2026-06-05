from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import oauth2
from app.database import get_db
from app.models.ai_chat import AIChat
from app.models.ai_request_log import AIRequestLog
from app.models.calculation_history import Calculation
from app.models.users import Users
from app.schemas.ai import (
    AIChatResponse,
    AIExplanationResponse,
    AIRequest,
    AIRequestLogResponse,
    AIResponse,
)
from app.services.ai_prompt_service import build_calculation_explanation_prompt, build_ai_chat_prompt
from app.services.openai_service import generate_ai_response

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/explain-calculation/{calculation_id}", response_model=AIExplanationResponse)
def explain_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    calculation = (
        db.query(Calculation)
        .filter(Calculation.id == calculation_id, Calculation.user_id == current_user.id)
        .first()
    )
    if not calculation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")

    prompt = build_calculation_explanation_prompt(
        input_data=calculation.input_data,
        result_data=calculation.result_data,
    )

    try:
        explanation = generate_ai_response(prompt)
        log = AIRequestLog(
            user_id=current_user.id,
            prompt=prompt,
            calculation_id=calculation.id,
            response=explanation,
            error_message=None,
            status="success",
        )
        db.add(log)
        db.commit()

    except Exception as error:
        log = AIRequestLog(
            user_id=current_user.id,
            prompt=prompt,
            calculation_id=calculation.id,
            response=None,
            error_message=str(error),
            status="error",
        )
        db.add(log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is temporarily unavailable",
        )

    return {"calculation_id": calculation.id, "explanation": explanation}


@router.get("/logs", response_model=list[AIRequestLogResponse])
def get_ai_logs(
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    logs = (
        db.query(AIRequestLog)
        .filter(AIRequestLog.user_id == current_user.id)
        .order_by(AIRequestLog.created_at.desc())
        .all()
    )
    return logs


@router.get("/logs/{log_id}", response_model=AIRequestLogResponse)
def get_ai_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    log = (
        db.query(AIRequestLog)
        .filter(AIRequestLog.user_id == current_user.id, AIRequestLog.id == log_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log


@router.get("/chat/logs", response_model=list[AIChatResponse])
def get_ai_chat_logs(
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    logs = (
        db.query(AIChat)
        .filter(AIChat.user_id == current_user.id)
        .order_by(AIChat.created_at.desc())
        .all()
    )
    return logs


@router.get("/chat/logs/{log_id}", response_model=AIChatResponse)
def get_ai_chat_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    log = db.query(AIChat).filter(AIChat.user_id == current_user.id, AIChat.id == log_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat log not found")
    return log


@router.post("/chat", response_model=AIResponse)
def ai_chat(
    request: AIRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(oauth2.get_current_user),
):
    if not request.prompt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is empty")
    recent_calculations = db.query(Calculation).filter(Calculation.user_id == current_user.id).order_by(Calculation.created_at.desc()).limit(5).all()
    recent_calculations_data = [
    {
        "id": calculation.id,
        "calculation_type": calculation.calculation_type,
        "input_data": calculation.input_data,
        "result_data": calculation.result_data,
        "room_project_id": calculation.room_project_id,
        "created_at": calculation.created_at,
    }
    for calculation in recent_calculations
]

    full_prompt = build_ai_chat_prompt(user_prompt=request.prompt, user_calculations=recent_calculations_data)
    try:
        response = generate_ai_response(full_prompt)
        log = AIChat(
            user_id=current_user.id,
            prompt=request.prompt,
            response=response,
            error_message=None,
            status="success",
        )
        db.add(log)
        db.commit()

    except Exception as error:
        log = AIChat(
            user_id=current_user.id,
            prompt=request.prompt,
            response=None,
            error_message=str(error),
            status="error",
        )
        db.add(log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is temporarily unavailable",
        )

    return {"response": response}

