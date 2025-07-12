

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
    fill: SolidFill = None
    