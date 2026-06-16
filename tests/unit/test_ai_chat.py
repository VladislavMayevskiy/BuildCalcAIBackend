from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.routes.ai import ai_chat
from app.schemas.ai import AIRequest
from app.services.ai_prompt_service import build_ai_chat_prompt


def test_ai_chat_requires_prompt():
    with pytest.raises(HTTPException) as exc_info:
        ai_chat(request=AIRequest(prompt=""), db=MagicMock(), current_user=SimpleNamespace(id=1))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Request is empty"


def test_ai_chat_logs_response_and_commits():
    user = SimpleNamespace(id=1)
    calculation = SimpleNamespace(
        id=123,
        calculation_type="room",
        input_data={"length": 4, "width": 5},
        result_data={
            "materials": [
                {"name": "cement", "quantity": 10, "unit": "bags"},
                {"name": "sand", "quantity": 2, "unit": "m3"},
            ],
            "assumptions": ["standard mix"],
            "warnings": [],
        },
        room_project_id=999,
        created_at="2026-05-15T00:00:00Z",
    )

    query = MagicMock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.all.return_value = [calculation]

    db = MagicMock()
    db.query.return_value = query

    with patch("app.api.routes.ai.generate_ai_response", return_value="AI answer") as mocked_generate:
        result = ai_chat(request=AIRequest(prompt="How much cement is needed?"), db=db, current_user=user)

    assert result == {"response": "AI answer"}
    mocked_generate.assert_called_once()
    db.add.assert_called_once()
    db.commit.assert_called_once()

    saved_log = db.add.call_args.args[0]
    assert saved_log.user_id == 1
    assert saved_log.prompt == "How much cement is needed?"
    assert saved_log.response == "AI answer"
    assert saved_log.status == "success"
    assert saved_log.error_message is None


def test_ai_chat_logs_error_when_generation_fails():
    user = SimpleNamespace(id=7)

    query = MagicMock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.all.return_value = []

    db = MagicMock()
    db.query.return_value = query

    with patch(
        "app.api.routes.ai.generate_ai_response",
        side_effect=RuntimeError("boom"),
    ) as mocked_generate:
        with pytest.raises(HTTPException) as exc_info:
            ai_chat(request=AIRequest(prompt="hello?"), db=db, current_user=user)

    assert exc_info.value.status_code == 503
    mocked_generate.assert_called_once()
    db.commit.assert_called_once()

    saved_log = db.add.call_args.args[0]
    assert saved_log.status == "error"
    assert saved_log.response is None
    assert saved_log.error_message == "boom"


def test_build_ai_chat_prompt_includes_hard_constraints():
    prompt = build_ai_chat_prompt(user_prompt="hi", user_calculations=[])

    # No-arithmetic and no-invention rules must be present.
    assert "Do not perform primary arithmetic" in prompt
    assert "missing" in prompt.lower()
    assert "Do not claim exact prices" in prompt
    # Newly implemented endpoints should be advertised.
    assert "/rebar/linear/v2" in prompt
    assert "/foundation/formwork/v2" in prompt


def test_build_ai_chat_prompt_summarizes_calculations():
    calculations = [
        {
            "id": 1,
            "calculation_type": "strip foundation",
            "created_at": "2026-05-15T00:00:00Z",
            "result_data": {
                "materials": [
                    {"name": "concrete", "quantity": 12.5, "unit": "m3"},
                    {"name": "rebar", "quantity": 45, "unit": "kg"},
                ],
                "assumptions": ["2% waste"],
                "warnings": ["verify soil conditions"],
            },
        }
    ]

    prompt = build_ai_chat_prompt(user_prompt="What should I do next?", user_calculations=calculations)

    assert "strip foundation" in prompt
    assert "concrete" in prompt
    assert "rebar" in prompt
    assert "verify soil conditions" in prompt
    assert "What should I do next?" in prompt
