from app.schemas.bars_calculation.index import BarsCalculationInput, BarsCalculationResponse

def bars_calculation_service(data: BarsCalculationInput) -> BarsCalculationResponse:
    weight_per_one_meter_kg = data.diameter_mm ** 2 / 162
    weight_per_bar_kg = data.length_per_bar_m * weight_per_one_meter_kg
    overall_length_m = data.length_per_bar_m * data.quantity
    overall_weight_kg = weight_per_one_meter_kg * overall_length_m
    reserve_multiplier = 1 + data.reserve_percent / 100
    overall_length_with_reserve_m = overall_length_m * reserve_multiplier
    overall_weight_with_reserve_kg = overall_weight_kg * reserve_multiplier
    return BarsCalculationResponse(
        overall_length_m=overall_length_m,
        overall_weight_kg=overall_weight_kg,
        weight_per_bar_kg=weight_per_bar_kg,
        weight_per_meter_kg=weight_per_one_meter_kg,
        overall_length_with_reserve_m=overall_length_with_reserve_m,
        overall_weight_with_reserve_kg=overall_weight_with_reserve_kg,
        reserve_multiplier=reserve_multiplier
    )