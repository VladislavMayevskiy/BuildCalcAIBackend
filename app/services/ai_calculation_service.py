from app.schemas.ai import AIParsedCalculationRequest
from app.schemas.calculation_result import CalculationResult
from app.services.ai_tool_registry import AI_TOOL_REGISTRY


def ai_calculation_service(
    parsed_request: AIParsedCalculationRequest,
) -> CalculationResult:
    tool = AI_TOOL_REGISTRY.get(parsed_request.intent)

    if tool is None:
        raise ValueError(
            f"Unsupported intent: {parsed_request.intent}"
        )

    if parsed_request.missing_fields:
        missing = ", ".join(
            sorted(parsed_request.missing_fields)
        )
        raise ValueError(
            f"Missing fields: {missing}"
        )

    parameters_by_name = {
        parameter.name: parameter
        for parameter in parsed_request.parameters
    }

    input_data = tool.parameter_builder(
        parameters_by_name
    )

    typed_input = tool.input_schema(
        **input_data
    )

    result = tool.handler(
        typed_input
    )

    return result