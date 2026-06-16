import math

from app.schemas.mep import (
    ElectricalLoadBasicInput,
    HeatLossBasicInput,
    PhaseType,
    PipeVolumeInput,
)
from app.schemas.calculation_result import (
    CalculationResult,
    CalculationStep,
    CalculationAssumption,
    CalculationWarning,
    MaterialItem,
)

# Volumetric heat capacity of air, ~0.34 Wh/(m3*K), used for simplified
# ventilation heat-loss estimates.
AIR_HEAT_CAPACITY_WH_M3K = 0.34


def calculate_heat_loss_basic_v2(data: HeatLossBasicInput) -> CalculationResult:
    ua = sum(s.area_m2 * s.u_value_w_m2k for s in data.surfaces)
    transmission_loss = round(ua * data.delta_t_k, 2)

    ventilation_loss = 0.0
    if data.air_volume_m3 is not None and data.air_change_rate_h is not None:
        ventilation_loss = round(
            AIR_HEAT_CAPACITY_WH_M3K * data.air_volume_m3 * data.air_change_rate_h * data.delta_t_k, 2
        )

    total_loss = round(transmission_loss + ventilation_loss, 2)

    return CalculationResult(
        calculation_type="mep_hvac_heat_loss_basic",
        steps=[
            CalculationStep(
                label="Transmission heat loss",
                formula="sum(area_m2 * u_value_w_m2k) * delta_t_k",
                input_values={"UA_w_per_k": round(ua, 3), "delta_t_k": data.delta_t_k},
                result=transmission_loss,
                unit="W",
            ),
            CalculationStep(
                label="Ventilation heat loss",
                formula="0.34 * air_volume_m3 * air_change_rate_h * delta_t_k",
                input_values={
                    "air_volume_m3": data.air_volume_m3,
                    "air_change_rate_h": data.air_change_rate_h,
                    "delta_t_k": data.delta_t_k,
                },
                result=ventilation_loss,
                unit="W",
            ),
            CalculationStep(
                label="Total heat loss",
                formula="transmission_loss + ventilation_loss",
                input_values={"transmission_loss": transmission_loss, "ventilation_loss": ventilation_loss},
                result=total_loss,
                unit="W",
            ),
        ],
        materials=[
            MaterialItem(name="Preliminary heating capacity (work item)", quantity=total_loss, unit="W"),
        ],
        assumptions=[
            CalculationAssumption(
                key="air_heat_capacity",
                description="Ventilation loss uses volumetric air heat capacity ~0.34 Wh/(m3*K).",
                source="standard_value",
            ),
            CalculationAssumption(
                key="steady_state",
                description="Steady-state heat loss with user-provided U-values and temperature difference.",
                source="simplified_model",
            ),
        ],
        warnings=[
            CalculationWarning(
                code="preliminary_heat_loss",
                message="This is a preliminary heat-loss estimate, not a certified HVAC design. Thermal bridges, infiltration, and standards are not fully accounted for.",
                severity="warning",
            ),
        ],
    )


def calculate_electrical_load_basic_v2(data: ElectricalLoadBasicInput) -> CalculationResult:
    power_factor = data.power_factor or 0.9
    installed_power = round(sum(load.power_kw for load in data.loads), 3)
    demand_power = round(sum(load.power_kw * load.demand_factor for load in data.loads), 3)
    apparent_power = round(demand_power / power_factor, 3)

    if data.phase_type == PhaseType.single_phase:
        current = round(apparent_power * 1000 / data.voltage_v, 2)
        current_formula = "apparent_power_kVA * 1000 / voltage_v"
    else:
        current = round(apparent_power * 1000 / (math.sqrt(3) * data.voltage_v), 2)
        current_formula = "apparent_power_kVA * 1000 / (sqrt(3) * voltage_v)"

    return CalculationResult(
        calculation_type="mep_electrical_load_basic",
        steps=[
            CalculationStep(
                label="Installed power",
                formula="sum(power_kw)",
                input_values={"load_count": len(data.loads)},
                result=installed_power,
                unit="kW",
            ),
            CalculationStep(
                label="Demand-adjusted power",
                formula="sum(power_kw * demand_factor)",
                input_values={"load_count": len(data.loads)},
                result=demand_power,
                unit="kW",
            ),
            CalculationStep(
                label="Apparent power",
                formula="demand_power / power_factor",
                input_values={"demand_power": demand_power, "power_factor": power_factor},
                result=apparent_power,
                unit="kVA",
            ),
            CalculationStep(
                label="Approximate current",
                formula=current_formula,
                input_values={"apparent_power_kVA": apparent_power, "voltage_v": data.voltage_v},
                result=current,
                unit="A",
            ),
        ],
        materials=[
            MaterialItem(name="Preliminary electrical demand (work item)", quantity=apparent_power, unit="kVA"),
        ],
        assumptions=[
            CalculationAssumption(
                key="power_factor",
                description="Apparent power uses a default power factor of 0.9 unless provided.",
                source="default" if data.power_factor is None else "user_input",
            ),
            CalculationAssumption(
                key="demand_factors",
                description="Demand-adjusted power applies per-load demand factors provided by the user.",
                source="user_input",
            ),
        ],
        warnings=[
            CalculationWarning(
                code="preliminary_electrical_load",
                message="This is a preliminary load estimate, not a certified electrical design. Diversity, cable sizing, and protection must be designed separately.",
                severity="warning",
            ),
        ],
    )


def calculate_pipe_volume_v2(data: PipeVolumeInput) -> CalculationResult:
    total_volume_l = 0.0
    total_length = 0.0
    for run in data.pipe_runs:
        radius_m = run.inner_diameter_mm / 1000 / 2
        volume_m3 = math.pi * radius_m ** 2 * run.length_m
        total_volume_l += volume_m3 * 1000
        total_length += run.length_m

    total_volume_l = round(total_volume_l, 3)
    total_length = round(total_length, 3)

    return CalculationResult(
        calculation_type="mep_plumbing_pipe_volume",
        steps=[
            CalculationStep(
                label="Total pipe length",
                formula="sum(length_m)",
                input_values={"run_count": len(data.pipe_runs)},
                result=total_length,
                unit="m",
            ),
            CalculationStep(
                label="Water volume inside pipes",
                formula="sum(pi * (inner_diameter_mm/2000)^2 * length_m) * 1000",
                input_values={"run_count": len(data.pipe_runs)},
                result=total_volume_l,
                unit="l",
            ),
        ],
        materials=[
            MaterialItem(name="Water volume in pipes", quantity=total_volume_l, unit="l"),
        ],
        assumptions=[
            CalculationAssumption(
                key="circular_pipe",
                description="Each pipe run is treated as a full circular cross-section using the inner diameter.",
                source="standard_geometry",
            ),
        ],
        warnings=[
            CalculationWarning(
                code="preliminary_pipe_volume",
                message="Volume is the internal water content of the pipes only; fittings and tanks are not included.",
                severity="info",
            ),
        ],
    )
