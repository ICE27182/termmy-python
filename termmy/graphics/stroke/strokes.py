

from __future__ import annotations

from .stroke import Stroke
from ..fills import Fill
from ...core import AbsoFloat, Vertex2

from dataclasses import dataclass
from typing import override, overload, TYPE_CHECKING

if TYPE_CHECKING:
    from ..shapes import Shape, SimpleLine, SimpleRing
    from ..shapes import Triangle, Circle, Ring, Line, Rectangle

type ShapeSupportedBySimpleStroke = Circle | Ring | Line | Rectangle | Triangle

@dataclass(slots=True)
class SimpleStroke(Stroke):
    # A simple stroke must have a fill and must not have a stroke
    fill: Fill
    # The shape that owns this stroke
    shape: ShapeSupportedBySimpleStroke 

    @classmethod
    def from_simple_stroke(
        cls, 
        simple_stroke: SimpleStroke, 
        shape: ShapeSupportedBySimpleStroke
    ) -> SimpleStroke:
        if isinstance(shape, ShapeSupportedBySimpleStroke):
            return cls(simple_stroke.fill, shape)
        else:
            raise ValueError("`shape` must be an instance of "
                             "`ShapeSupportedBySimpleStroke`. "
                             f"Got {type(shape).__name__}")


    @override
    def get_stroke(self) -> tuple[Shape]:
        """Get a tuple of shapes that outlines the 
        """
        from ..shapes import Shape, SimpleLine, SimpleRing
        from ..shapes import Triangle, Circle, Ring, Line, Rectangle
        shape = self.shape
        fill = self.fill
        if type(shape) == Triangle:
            return (
                SimpleLine(start=self.shape.a, end=self.shape.b,
                           fill=fill, transform=shape.transform),
                SimpleLine(start=self.shape.b, end=self.shape.c,
                           fill=fill, transform=shape.transform),
                SimpleLine(start=self.shape.a, end=self.shape.c,
                           fill=fill, transform=shape.transform),
            )
        elif type(shape) == Rectangle:
            a = Vertex2(0.0, 0.0, 0.0, 0.0)
            b = Vertex2(shape.width, 0.0, 1.0, 0.0)
            c = Vertex2(shape.width, shape.height, 1.0, 1.0)
            d = Vertex2(0.0, shape.height, 0.0, 1.0)
            return (
                SimpleLine(start=a, end=b, fill=fill, transform=shape.transform),
                SimpleLine(start=b, end=c, fill=fill, transform=shape.transform),
                SimpleLine(start=c, end=d, fill=fill, transform=shape.transform),
                SimpleLine(start=a, end=d, fill=fill, transform=shape.transform),
            )
        elif type(shape) == Line:
            return (SimpleStroke
                        .from_simple_stroke(self, shape.rectangulate())
                        .get_stroke())
        elif type(shape) == Circle:
            return (
                SimpleRing(shape.radius, self.fill, transform=shape.transform),
            )
        elif type(shape) == Ring:
            raise NotImplementedError
        else:
            # This may occur when the user manually set `shape` to a shape
            # that is not supported
            raise ValueError(f"Unsupported shape type: {type(shape)}")


