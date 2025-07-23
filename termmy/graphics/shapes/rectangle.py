

from dataclasses import dataclass

from .shape import Shape
from ..fills import Fill
from ..stroke import Stroke
from ...core import AbsoFloat

@dataclass(slots=True)
class Rectangle(Shape):
    width: AbsoFloat
    height: AbsoFloat
    fill: Fill | None = None
    stroke: Stroke | None = None
