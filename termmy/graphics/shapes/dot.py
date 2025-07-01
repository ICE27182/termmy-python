

from .shape import Shape
from ..fills import SolidFill
from ...colors import Color
from ...core import NormFloat

from dataclasses import dataclass
from typing import override

@dataclass(slots=True)
class Dot(Shape):
    width: NormFloat = 0.0
    height: NormFloat = 0.0
    fill: SolidFill | None
    stroke: None = None

    @override
    def _render(
        self, 
        width: int, 
        height: int,
        x_offset: NormFloat,
        y_offset: NormFloat,
        out: dict[int, Color],
    ) -> dict[int, Color]:
        fill = self.fill
        if fill:
            x = round(width * (self.x + x_offset))
            y = round(height * (self.y + y_offset))
            if 0 <= x < width and 0 <= y < height:
                out[y * width + x] = fill.color
        return super(Dot, self)._render(width, height, out=out,
                               x_offset=x_offset + self.x, 
                               y_offset=y_offset + self.y)
    