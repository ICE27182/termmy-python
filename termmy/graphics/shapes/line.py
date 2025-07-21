

from dataclasses import dataclass, field
from typing import override

from .shape import Shape
from ..fills import Fill
from ..stroke import Stroke
from ...core import Vec2, AbsoFloat
from ...colors import Color

@dataclass(slots=True)
class SimpleLine(Shape):
    """A straight line with a start and end point.
    It has no customizable weight and is always one pixel wide.
    It draws faster but is less versatile comparing to `Line`, which
    supports weight and stroke.
    """
    start: Vec2 = None
    end: Vec2 = None
    fill: Fill | None = None

    width: float = field(init=False)
    height: float = field(init=False)

    def __post_init__(self):
        self.width = abs(self.end.x - self.start.x)
        self.height = abs(self.end.y - self.start.y)

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


@dataclass(slots=True)
class Line(SimpleLine):
    stroke: Stroke | None = None
    weight: AbsoFloat = 0.02
