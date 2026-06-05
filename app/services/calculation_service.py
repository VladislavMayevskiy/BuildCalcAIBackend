from app.schemas.calculation import CalculationInput, CalculationResponse
from app.schemas.calculation_result import (CalculationResult, CalculationStep, CalculationAssumption, CalculationWarning,MaterialItem)


def floor(length: float, width: float) -> float:
    return length * width


def ceiling(length: float, width: float) -> float:
    return length * width


def perimeter(length: float, width: float) -> float:
    return 2 * (length + width)


def walls(
    perimeter_value: float,
    height: float,
    windows_area: float,
    doors_area: float,
) -> float:
    return perimeter_value * height - windows_area - doors_area


def tile_required_sqm(length: float, width: float) -> float:
    floor_area = floor(length=length, width=width)
    reserve_multiplier = 1.1
    tile_required = round(floor_area * reserve_multiplier, 2)
    return tile_required


def calculate_room(data: CalculationInput) -> CalculationResponse:
    floor_area = floor(data.length, data.width)
    ceiling_area = ceiling(data.length, data.width)
    perimeter_value = perimeter(data.length, data.width)

    wall_area_before_openings = perimeter_value * data.height
    openings_area = data.windows_area + data.doors_area

    if openings_area > wall_area_before_openings:
        raise ValueError("Windows and doors area cannot exceed total wall area")

    wall_area = walls(
        perimeter_value=perimeter_value,
        height=data.height,
        windows_area=data.windows_area,
        doors_area=data.doors_area,
    )

    wall_area_with_reserve = round(wall_area * 1.1, 2)
    paint_liters = round(wall_area_with_reserve / 9, 2)
    tile_required = tile_required_sqm(length=data.length, width=data.width)

    return CalculationResponse(
        floor_area=floor_area,
        ceiling_area=ceiling_area,
        wall_area=wall_area,
        wall_area_with_reserve=wall_area_with_reserve,
        paint_liters=paint_liters,
        tile_required_sqm=tile_required,
    )


def calculate_room_v2(data: CalculationInput) -> CalculationResult:
    floor_area = floor(data.length, data.width)
    ceiling_area = ceiling(data.length, data.width)
    perimeter_value = perimeter(data.length, data.width)

    wall_area_before_openings = perimeter_value * data.height
    openings_area = data.windows_area + data.doors_area

    if openings_area > wall_area_before_openings:
        raise ValueError("Windows and doors area cannot exceed total wall area")

    wall_area = walls(
        perimeter_value=perimeter_value,
        height=data.height,
        windows_area=data.windows_area,
        doors_area=data.doors_area,
    )

    wall_area_with_reserve = round(wall_area * 1.1, 2)
    paint_liters = round(wall_area_with_reserve / 9, 2)
    tile_required = tile_required_sqm(length=data.length, width=data.width)

    warnings: list[CalculationWarning] = []

    if openings_area > wall_area_before_openings * 0.7:
        warnings.append(
            CalculationWarning(
                code="large_openings_area",
                message="Windows and doors area is more than 70% of total wall area.",
                severity="warning",
            )
        )

    return CalculationResult(
        calculation_type="room_calculation",
        steps=[
            CalculationStep(
                label="Floor area",
                formula="length * width",
                input_values={
                    "length": data.length,
                    "width": data.width,
                },
                result=floor_area,
                unit="m2",
            ),
            CalculationStep(
                label="Ceiling area",
                formula="length * width",
                input_values={
                    "length": data.length,
                    "width": data.width,
                },
                result=ceiling_area,
                unit="m2",
            ),
            CalculationStep(
                label="Room perimeter",
                formula="2 * (length + width)",
                input_values={
                    "length": data.length,
                    "width": data.width,
                },
                result=perimeter_value,
                unit="m",
            ),
            CalculationStep(
                label="Wall area before openings",
                formula="perimeter * height",
                input_values={
                    "perimeter": perimeter_value,
                    "height": data.height,
                },
                result=wall_area_before_openings,
                unit="m2",
            ),
            CalculationStep(
                label="Openings area",
                formula="windows_area + doors_area",
                input_values={
                    "windows_area": data.windows_area,
                    "doors_area": data.doors_area,
                },
                result=openings_area,
                unit="m2",
            ),
            CalculationStep(
                label="Net wall area",
                formula="wall_area_before_openings - openings_area",
                input_values={
                    "wall_area_before_openings": wall_area_before_openings,
                    "openings_area": openings_area,
                },
                result=wall_area,
                unit="m2",
            ),
            CalculationStep(
                label="Wall area with reserve",
                formula="wall_area * 1.10",
                input_values={
                    "wall_area": wall_area,
                    "reserve_percent": 10,
                },
                result=wall_area_with_reserve,
                unit="m2",
            ),
            CalculationStep(
                label="Paint required",
                formula="wall_area_with_reserve / paint_coverage",
                input_values={
                    "wall_area_with_reserve": wall_area_with_reserve,
                    "paint_coverage_m2_per_liter": 9,
                },
                result=paint_liters,
                unit="liters",
            ),
            CalculationStep(
                label="Floor tile required",
                formula="floor_area * 1.10",
                input_values={
                    "floor_area": floor_area,
                    "reserve_percent": 10,
                },
                result=tile_required,
                unit="m2",
            ),
        ],
        materials=[
            MaterialItem(
                name="Paint",
                quantity=paint_liters,
                unit="liters",
                waste_percent=None,
            ),
            MaterialItem(
                name="Floor tiles",
                quantity=tile_required,
                unit="m2",
                waste_percent=10,
            ),
        ],
        assumptions=[
            CalculationAssumption(
                key="wall_reserve",
                description="Wall area reserve is assumed as 10%.",
                source="default_norm",
            ),
            CalculationAssumption(
                key="paint_coverage",
                description="Paint coverage is assumed as 9 m2 per liter.",
                source="default_norm",
            ),
            CalculationAssumption(
                key="tile_reserve",
                description="Floor tile reserve is assumed as 10%.",
                source="default_norm",
            ),
        ],
        warnings=warnings,
    )