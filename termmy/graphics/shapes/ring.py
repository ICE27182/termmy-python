

from dataclasses import dataclass

from .shape import Shape
from ..fills import Fill
from ..stroke import Stroke
from ...core import AbsoFloat

@dataclass(slots=True)
class Ring(Shape):
    """
    The uv coordinates of the center of a ring are (0.5, 0.5).
    """
    inner_radius: AbsoFloat
    outer_radius: AbsoFloat
    fill: Fill | None = None
    stroke: Stroke | None = None
    