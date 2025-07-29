

from __future__ import annotations

from .shape import Shape
from .triangle import Triangle
from ..fills import Fill, SolidFill
from ..stroke import Stroke, SimpleStroke
from ..node import Node
from ...core import AbsoFloat, Transform2D, Vec2, Vertex2
from ...colors import Colors

from dataclasses import dataclass

@dataclass(slots=True)
class Rectangle(Shape):
    width: AbsoFloat
    height: AbsoFloat
    fill: Fill | None = None
    stroke: Stroke | None = None

    @classmethod
    def at(cls, corner1: Vec2, corner2: Vec2, 
           fill: Fill | None | bool = True, stroke: Stroke | None = None,
           z: float = 0.0, parent_node: Node | None = None) -> Rectangle:
        """Create a new rectangle at the given corners with optional fill and stroke.
        Args:
            corner1 (Vec2): The x-coordinate of the rectangle.
            corner2 (Vec2): The y-coordinate of the rectangle.
            fill (Fill | None | bool): The fill color of the rectangle. 
                - If True is passed, defaults to a yellow solid fill.
                - If None or False is passed, no fill will be set to None.
            stroke (Stroke | None): The stroke of the rectangle.
            z (float): The depth of the rectangle.
            parent_node (Node | None): The optional parent node of the rectangle.
        """
        fill = fill if isinstance(fill, Fill) else SolidFill(Colors.yellow()) if fill else None
        width = abs(corner2.x - corner1.x)
        height = abs(corner2.y - corner1.y)
        translate = Vec2(corner1.x if corner1.x < corner2.x else corner2.x,
                         corner1.y if corner1.y < corner2.y else corner2.y)
        pivot = Vec2(translate.x + width / 2, translate.y + height / 2)
        return cls(
            width=width,
            height=height,
            fill=fill,
            stroke=stroke,
            z=z,
            transform=Transform2D(
                translate=translate,
                pivot=pivot,
                # No circular ref here because it's a new object
                _parent= None if parent_node is None else parent_node.transform,
            ),
            # No circular ref here because it's a new object
            _parent=parent_node,
        )


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
