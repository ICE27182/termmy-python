

from dataclasses import dataclass

from .shape import Shape
from ..fills import Fill
from ..stroke import Stroke
from ...core import AbsoFloat

@dataclass(slots=True)
class Circle(Shape):
    """
    The uv coordinates of the center of a circle are (0.5, 0.5).
    """
    radius: AbsoFloat
    fill: Fill | None = None
    stroke: Stroke | None = None
    