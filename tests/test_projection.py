"""тесты проекции fdf.projection"""

from pathlib import Path

from fdf.model import Point
from fdf.parser import parse_map
from fdf.projection import Camera

MAPS_DIR = Path(__file__).parent.parent / "maps"


def test_projection_origin() -> None:
    camera = Camera(scale=1.0, offset_x=0.0, offset_y=0.0, z_scale=1.0)
    pt = Point(0, 0, 0)
    x, y = camera.project(pt)
    assert round(x, 5) == 0.0
    assert round(y, 5) == 0.0


def test_projection_altitude_negative_y() -> None:
    camera = Camera(scale=1.0, offset_x=0.0, offset_y=0.0, z_scale=1.0)
    pt = Point(0, 0, 1)
    _x, y = camera.project(pt)
    assert y < 0.0


def test_camera_fit_bounds() -> None:
    grid = parse_map(MAPS_DIR / "elem.fdf")
    width = 800
    height = 600

    camera = Camera()
    camera.fit(grid, width, height)

    for pt in grid:
        x, y = camera.project(pt)
        assert 0 <= x <= width
        assert 0 <= y <= height
