"""проекция и камера"""

import math

from fdf.model import Map, Point


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    s = hex_code.lstrip("#")
    if len(s) != 6:
        s = s.zfill(6)
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    r_cl = max(0, min(255, r))
    g_cl = max(0, min(255, g))
    b_cl = max(0, min(255, b))
    return f"#{r_cl:02X}{g_cl:02X}{b_cl:02X}"


def lerp_color(color_a: str, color_b: str, t: float) -> str:
    # линейная интерполяция цвета
    t_cl = max(0.0, min(1.0, t))
    r1, g1, b1 = hex_to_rgb(color_a)
    r2, g2, b2 = hex_to_rgb(color_b)
    r = round(r1 + (r2 - r1) * t_cl)
    g = round(g1 + (g2 - g1) * t_cl)
    b = round(b1 + (b2 - b1) * t_cl)
    return rgb_to_hex(r, g, b)


def height_color(z: int, z_min: int, z_max: int) -> str:
    # градиент синий -> зеленый -> желтый -> красный
    if z_max <= z_min:
        return "#0000FF"
    t = max(0.0, min(1.0, (z - z_min) / (z_max - z_min)))

    palette = [
        (0.0, "#0000FF"),
        (0.33, "#00FF00"),
        (0.66, "#FFFF00"),
        (1.0, "#FF0000"),
    ]
    for i in range(len(palette) - 1):
        t1, c1 = palette[i]
        t2, c2 = palette[i + 1]
        if t <= t2:
            loc_t = (t - t1) / (t2 - t1)
            return lerp_color(c1, c2, loc_t)
    return "#FF0000"


class Camera:
    """управление положением и масштабом"""

    def __init__(
        self,
        scale: float = 1.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        z_scale: float = 1.0,
    ) -> None:
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.z_scale = z_scale
        self.angle: float = math.radians(30)
        self.isometric: bool = True

    def project(self, point: Point) -> tuple[float, float]:
        if self.isometric:
            # изометрия по формулам
            cos_a = math.cos(self.angle)
            sin_a = math.sin(self.angle)
            x_prime = (point.x - point.y) * cos_a
            y_prime = (point.x + point.y) * sin_a - (point.z * self.z_scale)
        else:
            # параллельная проекция вид сверху
            x_prime = float(point.x)
            y_prime = float(point.y)

        x_screen = x_prime * self.scale + self.offset_x
        y_screen = y_prime * self.scale + self.offset_y
        return x_screen, y_screen

    def fit(self, grid: Map, width: int, height: int) -> None:
        # автоподгон масштаба под окно
        if len(grid) == 0:
            return

        temp_cam = Camera(scale=1.0, offset_x=0.0, offset_y=0.0, z_scale=self.z_scale)
        temp_cam.angle = self.angle
        temp_cam.isometric = self.isometric

        proj = [temp_cam.project(p) for p in grid]
        xs = [pt[0] for pt in proj]
        ys = [pt[1] for pt in proj]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        bbox_w = max_x - min_x
        bbox_h = max_y - min_y

        if bbox_w > 0 and bbox_h > 0:
            scale_x = width / bbox_w
            scale_y = height / bbox_h
            self.scale = min(scale_x, scale_y) * 0.9
        elif bbox_w > 0:
            self.scale = (width / bbox_w) * 0.9
        elif bbox_h > 0:
            self.scale = (height / bbox_h) * 0.9
        else:
            self.scale = 20.0

        self.center(grid, width, height)

    def center(self, grid: Map, width: int, height: int) -> None:
        if len(grid) == 0:
            return

        temp_cam = Camera(scale=1.0, offset_x=0.0, offset_y=0.0, z_scale=self.z_scale)
        temp_cam.angle = self.angle
        temp_cam.isometric = self.isometric

        proj = [temp_cam.project(p) for p in grid]
        xs = [pt[0] for pt in proj]
        ys = [pt[1] for pt in proj]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        cnt_x = (min_x + max_x) / 2.0 * self.scale
        cnt_y = (min_y + max_y) / 2.0 * self.scale
        self.offset_x = (width / 2.0) - cnt_x
        self.offset_y = (height / 2.0) - cnt_y

    def zoom_at(self, factor: float, cx: float, cy: float) -> None:
        # зум с фиксацией фокуса на курсоре
        new_scale = max(0.1, self.scale * factor)
        actual_ratio = new_scale / self.scale
        self.offset_x = cx - (cx - self.offset_x) * actual_ratio
        self.offset_y = cy - (cy - self.offset_y) * actual_ratio
        self.scale = new_scale
