from typing import Callable, Optional, Any
from pydantic import BaseModel, Field

from app.schemas.ai import AIParsedParameter
from app.schemas.calculation_result import CalculationResult


class AIToolDefinition(BaseModel):
    intent: str
    description: str
    input_schema: type[BaseModel]
    handler: Callable[[BaseModel], CalculationResult]
    parameter_builder: Callable[[dict[str, AIParsedParameter]], dict[str, Any]]
    aliases: list[str] = Field(default_factory=list)