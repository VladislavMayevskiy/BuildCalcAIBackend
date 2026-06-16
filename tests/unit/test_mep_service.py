import math

import pytest
from pydantic import ValidationError

from app.schemas.mep import (
    ElectricalLoadBasicInput,
    HeatLossBasicInput,
    PhaseType,
    PipeVolumeInput,
)
from app.services.mep_service import (
    calculate_electrical_load_basic_v2,
    calculate_heat_loss_basic_v2,
    calculate_pipe_volume_v2,
)


def test_heat_loss_transmission_and_ventilation():
    data = HeatLossBasicInput(
        surfaces=[{"area_m2": 50, "u_value_w_m2k": 0.3}, {"area_m2": 20, "u_value_w_m2k": 1.2}],
        delta_t_k=25,
        air_volume_m3=120,
        air_change_rate_h=0.5,
    )
    result = calculate_heat_loss_basic_v2(data)

    assert result.calculation_type == "mep_hvac_heat_loss_basic"
    # UA = 50*0.3 + 20*1.2 = 15 + 24 = 39 ; transmission = 39*25 = 975
    assert result.steps[0].result == pytest.approx(975.0)
    # ventilation = 0.34*120*0.5*25 = 510
    assert result.steps[1].result == pytest.approx(510.0)
    assert result.steps[2].result == pytest.approx(1485.0)
    assert any(w.code == "preliminary_heat_loss" for w in result.warnings)


def test_heat_loss_requires_surfaces():
    with pytest.raises(ValidationError):
        HeatLossBasicInput(surfaces=[], delta_t_k=25)


def test_heat_loss_rejects_non_positive_delta():
    with pytest.raises(ValidationError):
        HeatLossBasicInput(surfaces=[{"area_m2": 10, "u_value_w_m2k": 0.3}], delta_t_k=0)


def test_electrical_load_three_phase_current():
    data = ElectricalLoadBasicInput(
        loads=[{"name": "sockets", "power_kw": 10, "demand_factor": 0.8}],
        voltage_v=400,
        phase_type=PhaseType.three_phase,
        power_factor=0.9,
    )
    result = calculate_electrical_load_basic_v2(data)

    # demand = 8 kW ; apparent = 8/0.9 = 8.889 kVA
    assert result.steps[1].result == pytest.approx(8.0)
    apparent = round(8 / 0.9, 3)
    expected_current = round(apparent * 1000 / (math.sqrt(3) * 400), 2)
    current_step = next(s for s in result.steps if s.label == "Approximate current")
    assert current_step.result == pytest.approx(expected_current)
    assert any(w.code == "preliminary_electrical_load" for w in result.warnings)


def test_electrical_load_single_phase_current():
    data = ElectricalLoadBasicInput(
        loads=[{"name": "heater", "power_kw": 2, "demand_factor": 1}],
        voltage_v=230,
        phase_type=PhaseType.single_phase,
        power_factor=1,
    )
    result = calculate_electrical_load_basic_v2(data)
    current_step = next(s for s in result.steps if s.label == "Approximate current")
    assert current_step.result == pytest.approx(round(2 * 1000 / 230, 2))


def test_electrical_requires_loads():
    with pytest.raises(ValidationError):
        ElectricalLoadBasicInput(loads=[], voltage_v=230, phase_type=PhaseType.single_phase)


def test_pipe_volume_total_liters():
    data = PipeVolumeInput(
        pipe_runs=[{"length_m": 10, "inner_diameter_mm": 20}, {"length_m": 5, "inner_diameter_mm": 25}]
    )
    result = calculate_pipe_volume_v2(data)

    expected = (math.pi * (0.02 / 2) ** 2 * 10 + math.pi * (0.025 / 2) ** 2 * 5) * 1000
    assert result.steps[0].result == 15  # total length
    assert result.steps[1].result == pytest.approx(round(expected, 3))


def test_pipe_volume_requires_runs():
    with pytest.raises(ValidationError):
        PipeVolumeInput(pipe_runs=[])
