

from dataclasses import dataclass

from .shape import Shape
from .triangle import Triangle
from ..fills import Fill
from ..stroke import Stroke
from ...core import AbsoFloat, Vertex2

@dataclass(slots=True)
class Rectangle(Shape):
    width: AbsoFloat
    height: AbsoFloat
    fill: Fill | None = None
    stroke: Stroke | None = None

    def triangulate(self) -> tuple[Triangle, Triangle]:
        a = Vertex2(0.0, 0.0, 0.0, 0.0)
        b = Vertex2(self.width, 0.0, 1.0, 0.0)
        c = Vertex2(self.width, self.height, 1.0, 1.0)
        d = Vertex2(0.0, self.height, 0.0, 1.0)
        return (
            Triangle(a, b, c, self.fill, None,
                     z=self.z, transform=self.transform),
            Triangle(a, d, c, self.fill, None,
                     z=self.z, transform=self.transform),
        )
        
