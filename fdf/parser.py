"""парсер файлов fdf"""

from pathlib import Path

from fdf.exceptions import MapFormatError
from fdf.model import Map, Point


def parse_token(token: str, line_num: int, col_num: int) -> tuple[int, str | None]:
    parts = token.split(",")
    if len(parts) > 2:
        raise MapFormatError(
            f"'{token}' — неверный формат значения",
            line=line_num,
            column=col_num,
        )

    # парсинг высоты z
    try:
        z = int(parts[0])
    except ValueError:
        raise MapFormatError(
            f"'{parts[0]}' — не целое число",
            line=line_num,
            column=col_num,
        ) from None

    # парсинг цвета если задан
    color: str | None = None
    if len(parts) == 2:
        raw_color = parts[1].strip()
        if not raw_color.lower().startswith("0x"):
            raise MapFormatError(
                f"'{raw_color}' — неверный префикс цвета (нужен 0x)",
                line=line_num,
                column=col_num,
            )
        hex_digits = raw_color[2:]
        if not hex_digits:
            raise MapFormatError(
                f"'{raw_color}' — нет значения цвета",
                line=line_num,
                column=col_num,
            )
        try:
            color_int = int(hex_digits, 16)
        except ValueError:
            raise MapFormatError(
                f"'{raw_color}' — не hex цвет",
                line=line_num,
                column=col_num,
            ) from None

        if color_int < 0 or color_int > 0xFFFFFF or len(hex_digits) > 8:
            raise MapFormatError(
                f"'{raw_color}' — цвет вне rgb диапазона",
                line=line_num,
                column=col_num,
            )
        color = f"#{color_int:06X}"

    return z, color


def parse_map(file_path: str | Path) -> Map:
    path = Path(file_path)

    # oserror не ловим по тз
    with path.open("r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    lines = [line.strip() for line in raw_lines]
    while lines and not lines[-1]:
        lines.pop()

    if not lines:
        raise MapFormatError("пустой файл")

    points: list[Point] = []
    width: int | None = None

    for y, line in enumerate(lines):
        line_num = y + 1
        tokens = line.split()
        if not tokens:
            raise MapFormatError(
                "пустая строка в середине файла",
                line=line_num,
            )

        if width is None:
            width = len(tokens)
        elif len(tokens) != width:
            raise MapFormatError(
                f"строки разной длины: ожидалось {width} значений, получено {len(tokens)}",
                line=line_num,
            )

        for x, token in enumerate(tokens):
            col_num = x + 1
            z, color = parse_token(token, line_num, col_num)
            points.append(Point(x=x, y=y, z=z, color=color))

    assert width is not None
    height = len(lines)
    return Map(width=width, height=height, points=points)
