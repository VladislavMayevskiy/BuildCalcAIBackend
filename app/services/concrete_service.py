import math

from app.schemas.concrete import ConcreteMixInput, ConcreteShape, ConcreteVolumeInput
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)


def _unit_volume(data: ConcreteVolumeInput) -> tuple[float, str, dict]:
    if data.shape_type in (ConcreteShape.rectangular_prism, ConcreteShape.beam):
        vol = data.length_m * data.width_m * data.height_m
        return vol, "length_m * width_m * height_m", {
            "length_m": data.length_m, "width_m": data.width_m, "height_m": data.height_m
        }
    if data.shape_type == ConcreteShape.slab:
        vol = data.length_m * data.width_m * data.thickness_m
        return vol, "length_m * width_m * thickness_m", {
            "length_m": data.length_m, "width_m": data.width_m, "thickness_m": data.thickness_m
        }
    if data.shape_type == ConcreteShape.column:
        depth = data.length_m if data.length_m is not None else data.width_m
        vol = data.width_m * depth * data.height_m
        return vol, "width_m * depth_m * height_m", {
            "width_m": data.width_m, "depth_m": depth, "height_m": data.height_m
        }
    # cylinder
    vol = math.pi / 4 * data.diameter_m ** 2 * data.height_m
    return vol, "pi/4 * diameter_m^2 * height_m", {
        "diameter_m": data.diameter_m, "height_m": data.height_m
    }


def calculate_concrete_volume_v2(data: ConcreteVolumeInput) -> CalculationResult:
    reserve = data.reserve_percent or 0
    unit_volume, formula, inputs = _unit_volume(data)
    unit_volume = round(unit_volume, 4)
    total_volume = round(unit_volume * data.count, 4)
    volume_with_reserve = round(total_volume * (1 + reserve / 100), 4)

    warnings: list[CalculationWarning] = []
    if total_volume == 0:
        warnings.append(
            CalculationWarning(
                code="zero_volume",
                message="Calculated concrete volume is zero; check dimensions.",
                severity="error",
            )
        )

    return CalculationResult(
        calculation_type="concrete_volume",
        steps=[
            CalculationStep(
                label=f"Unit volume ({data.shape_type.value})",
                formula=formula,
                input_values=inputs,
                result=unit_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Total volume",
                formula="unit_volume * count",
                input_values={"unit_volume": unit_volume, "count": data.count},
                result=total_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Volume with reserve",
                formula="total_volume * (1 + reserve_percent / 100)",
                input_values={"total_volume": total_volume, "reserve_percent": reserve},
                result=volume_with_reserve,
                unit="m3",
            ),
        ],
        materials=[
            MaterialItem(name="Concrete", quantity=volume_with_reserve, unit="m3", waste_percent=reserve),
        ],
        assumptions=[
            CalculationAssumption(
                key="shape_geometry",
                description=f"Volume uses the idealized geometry of a {data.shape_type.value}.",
                source="standard_geometry",
            ),
            CalculationAssumption(
                key="reserve_percent",
                description="Concrete reserve is based on input reserve_percent.",
                source="user_input",
            ),
        ],
        warnings=warnings,
    )


def calculate_concrete_mix_materials_v2(data: ConcreteMixInput) -> CalculationResult:
    dry_factor = data.dry_volume_factor or 1.54
    cement_density = data.cement_density_kg_per_m3 or 1440
    bag_weight = data.cement_bag_weight_kg or 50
    wcr = data.water_cement_ratio or 0.5

    total_parts = data.mix_ratio_cement + data.mix_ratio_sand + data.mix_ratio_gravel
    dry_volume = round(data.concrete_volume_m3 * dry_factor, 4)
    cement_volume = round(dry_volume * data.mix_ratio_cement / total_parts, 4)
    sand_volume = round(dry_volume * data.mix_ratio_sand / total_parts, 4)
    gravel_volume = round(dry_volume * data.mix_ratio_gravel / total_parts, 4)
    cement_kg = round(cement_volume * cement_density, 2)
    cement_bags = float(math.ceil(cement_kg / bag_weight))
    water_liters = round(cement_kg * wcr, 2)

    return CalculationResult(
        calculation_type="concrete_mix_materials",
        steps=[
            CalculationStep(
                label="Dry volume",
                formula="concrete_volume_m3 * dry_volume_factor",
                input_values={"concrete_volume_m3": data.concrete_volume_m3, "dry_volume_factor": dry_factor},
                result=dry_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Cement volume",
                formula="dry_volume * cement_part / total_parts",
                input_values={"dry_volume": dry_volume, "cement_part": data.mix_ratio_cement, "total_parts": total_parts},
                result=cement_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Sand volume",
                formula="dry_volume * sand_part / total_parts",
                input_values={"dry_volume": dry_volume, "sand_part": data.mix_ratio_sand, "total_parts": total_parts},
                result=sand_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Gravel volume",
                formula="dry_volume * gravel_part / total_parts",
                input_values={"dry_volume": dry_volume, "gravel_part": data.mix_ratio_gravel, "total_parts": total_parts},
                result=gravel_volume,
                unit="m3",
            ),
            CalculationStep(
                label="Cement mass",
                formula="cement_volume * cement_density_kg_per_m3",
                input_values={"cement_volume": cement_volume, "cement_density_kg_per_m3": cement_density},
                result=cement_kg,
                unit="kg",
            ),
            CalculationStep(
                label="Water quantity",
                formula="cement_kg * water_cement_ratio",
                input_values={"cement_kg": cement_kg, "water_cement_ratio": wcr},
                result=water_liters,
                unit="l",
            ),
        ],
        materials=[
            MaterialItem(name="Cement", quantity=cement_kg, unit="kg"),
            MaterialItem(name="Cement bags", quantity=cement_bags, unit="bags"),
            MaterialItem(name="Sand", quantity=sand_volume, unit="m3"),
            MaterialItem(name="Gravel", quantity=gravel_volume, unit="m3"),
            MaterialItem(name="Water", quantity=water_liters, unit="l"),
        ],
        assumptions=[
            CalculationAssumption(
                key="dry_volume_factor",
                description="Dry material volume = wet concrete volume * dry_volume_factor (default 1.54) to account for voids.",
                source="default" if data.dry_volume_factor is None else "user_input",
            ),
            CalculationAssumption(
                key="cement_density",
                description="Cement bulk density default 1440 kg/m3; bag weight default 50 kg.",
                source="default",
            ),
        ],
        warnings=[
            CalculationWarning(
                code="approximate_mix_design",
                message="This is an approximate volumetric estimate. Final mix design depends on concrete class, aggregate properties, lab design, and supplier specs.",
                severity="warning",
            ),
        ],
    )
