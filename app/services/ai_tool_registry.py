from app.schemas.ai_tool_definition import AIToolDefinition
from app.schemas.slab_foundation import SlabFoundationInput
from app.services.slab_foundation_service import calculate_slab_foundation_v2
from app.services.builders.slab_foundation import build_slab_foundation_parameters

SLAB_FOUNDATION_TOOL = AIToolDefinition(
    intent="foundation_slab",
    description="Calculates concrete volume for a rectangular slab foundation using length, width and slab thickness.",
    input_schema=SlabFoundationInput,
    handler=calculate_slab_foundation_v2,
    parameter_builder=build_slab_foundation_parameters,
    aliases=["slab_foundation", "concrete_slab"],
)


AI_TOOL_REGISTRY = {
    "foundation_slab": SLAB_FOUNDATION_TOOL,
}