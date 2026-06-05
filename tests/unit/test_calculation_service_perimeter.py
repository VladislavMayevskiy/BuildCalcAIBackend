from app.schemas.calculation import CalculationInput
from app.services.calculation_service import calculate_room


def test_wall_and_perimeter():
    data = CalculationInput(
        length=4,
        width=5,
        height=2.7,
        doors_area=2,
        windows_area=3,
    )

    result = calculate_room(data)

    assert result.wall_area == 43.6

