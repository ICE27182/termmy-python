from dataclasses import dataclass
from typing import override

from .shape import Shape
from ...colors import Color
from ..fills import SolidFill
from ...core import Vec2Rela, NormFloat

@dataclass(slots=True)
class Line(Shape):
    start: Vec2Rela = None
    end: Vec2Rela = None
    weight: NormFloat = 0.02
    stroke: None = None

    def slope(self) -> float:
        return ((self.end.y - self.start.y) / (self.end.x - self.start.x) 
                if self.end.x != self.start.x else float('inf'))
    def slope_inv(self) -> float:
        return 1 / self.slope() if self.slope() != 0 else float('inf')
    
    def y_intercept(self) -> float:
        if self.end.x == self.start.x:
            raise ValueError("Vertical line has no y-intercept.")
        return self.start.y - (self.slope() * self.start.x)
    def x_intercept(self) -> float:
        if self.end.y == self.start.y:
            raise ValueError("Horizontal line has no x-intercept.")
        return (self.start.x - (self.start.y / self.slope()))

    @override
    def _render(
        self, 
        width: int, 
        height: int, 
        x_offset: NormFloat,
        y_offset: NormFloat,
        out: dict[int, Color],
    ) -> dict[int, Color]:
        dir_x = self.end.x - self.start.x
        dir_y = self.end.y - self.start.y
        len_inv = (dir_x*dir_x + dir_y*dir_y) ** -0.5
        weight: int = round((width*width + height*height) ** 0.5 * self.weight)
        dir_x *= len_inv
        dir_y *= len_inv
        x = width * (self.start.x + x_offset)
        y = height * (self.start.y + y_offset)
        end_x = width * (self.end.x + x_offset)
        end_y = height * (self.end.y + y_offset)
        while dir_x * (end_x - x) + dir_y * (end_y - y) > 0.0:
            for i in range(1-weight, weight):
                # (-dir_y, dir_x) is perpendicular to (dir_x, dir_y)
                dis_x = round(x + i * -dir_y)
                dis_y = round(y + i * dir_x)
                if 0 <= dis_x < width and 0 <= dis_y < height:
                    out[dis_y * width + dis_x] = self.fill.get_color(
                        dis_x / width - x_offset, 
                        dis_y / height - y_offset,
                    )
            x += dir_x
            y += dir_y
        
        return super(Line, self)._render(width, height, out=out,
                                         x_offset=x_offset + self.x, 
                                         y_offset=y_offset + self.y)
        
        
        
