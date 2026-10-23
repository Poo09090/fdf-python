"""модель карты и точек"""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Point:
    """точка с коорд x, y, z и цветом"""

    x: int
    y: int
    z: int
    color: str | None = None


class Map:
    """сетка точек карты"""

    def __init__(self, width: int, height: int, points: list[Point]) -> None:
        self.width = width
        self.height = height
        self._points = points

    def __len__(self) -> int:
        return len(self._points)

    def __iter__(self) -> Iterator[Point]:
        return iter(self._points)

    def at(self, x: int, y: int) -> Point:
        # получение точки по x и y
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"коорд ({x}, {y}) вне карты {self.width}x{self.height}")
        return self._points[y * self.width + x]

    def neighbors(self, point: Point) -> list[Point]:
        # соседи справа и снизу чтоб не двоить ребра
        res: list[Point] = []
        if point.x + 1 < self.width:
            res.append(self.at(point.x + 1, point.y))
        if point.y + 1 < self.height:
            res.append(self.at(point.x, point.y + 1))
        return res

    @property
    def min_z(self) -> int:
        return min((p.z for p in self._points), default=0)

    @property
    def max_z(self) -> int:
        return max((p.z for p in self._points), default=0)
