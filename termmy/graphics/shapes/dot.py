

from .shape import Shape
from ..fills import SolidFill

from dataclasses import dataclass

@dataclass(slots=True)
class Dot(Shape):
    fill: SolidFill = None
    