

from dataclasses import dataclass

from .shape import Shape
from ..fills import Fill
from ..stroke import Stroke
from ...core import Vec2

@dataclass(slots=True)
class Triangle(Shape):
    a: Vec2
    b: Vec2
    c: Vec2
    fill: Fill | None = None
    stroke: Stroke | None = None
    