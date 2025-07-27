

from dataclasses import dataclass

from .shape import Shape
from ..fills import Fill
from ..stroke import Stroke
from ...core import Vertex2

@dataclass(slots=True)
class Triangle(Shape):
    a: Vertex2
    b: Vertex2
    c: Vertex2
    fill: Fill | None = None
    stroke: Stroke | None = None
    