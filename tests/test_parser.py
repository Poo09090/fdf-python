"""тесты парсера fdf.parser"""

from pathlib import Path

import pytest

from fdf.exceptions import MapFormatError
from fdf.parser import parse_map, parse_token

MAPS_DIR = Path(__file__).parent.parent / "maps"


def test_parse_elem_map() -> None:
    elem_path = MAPS_DIR / "elem.fdf"
    grid = parse_map(elem_path)

    assert grid.width == 5
    assert grid.height == 5
    assert len(grid) == 25

    # центр точка (x=2, y=2) выс 5
    center = grid.at(2, 2)
    assert center.x == 2
    assert center.y == 2
    assert center.z == 5
    assert center.color is None

    # угол (0, 0)
    corner = grid.at(0, 0)
    assert corner.x == 0
    assert corner.y == 0
    assert corner.z == 0


@pytest.mark.parametrize(
    ("token", "expected_z", "expected_color"),
    [
        ("7", 7, None),
        ("-3", -3, None),
        ("2,0xFF8800", 2, "#FF8800"),
        ("1,0xff", 1, "#0000FF"),
    ],
)
def test_parse_token_parametrized(
    token: str,
    expected_z: int,
    expected_color: str | None,
) -> None:
    z, color = parse_token(token, line_num=1, col_num=1)
    assert z == expected_z
    assert color == expected_color


def test_bad_map_empty() -> None:
    with pytest.raises(MapFormatError):
        parse_map(MAPS_DIR / "bad" / "empty.fdf")


def test_bad_map_jagged_row() -> None:
    with pytest.raises(MapFormatError, match="строка 2"):
        parse_map(MAPS_DIR / "bad" / "jagged_row.fdf")


def test_bad_map_non_integer() -> None:
    with pytest.raises(MapFormatError, match="не целое число"):
        parse_map(MAPS_DIR / "bad" / "non_integer.fdf")


def test_bad_map_invalid_color() -> None:
    with pytest.raises(MapFormatError, match="не hex цвет"):
        parse_map(MAPS_DIR / "bad" / "invalid_color.fdf")


def test_file_not_found_raises_os_error() -> None:
    with pytest.raises(OSError):
        parse_map(MAPS_DIR / "non_existent_map.fdf")
