

from __future__ import annotations

from .shape import Shape
from ..fills import Fill, SolidFill
from ..stroke import Stroke
from ..node import Node
from ...core import AbsoFloat, Transform2D, Vec2
from ...colors import Colors

from dataclasses import dataclass

@dataclass(slots=True)
class Circle(Shape):
    """
    The uv coordinates of the center of a circle are (0.5, 0.5).
    """
    radius: AbsoFloat
    fill: Fill | None = None
    stroke: Stroke | None = None
    
    @classmethod
    def at(cls, x: AbsoFloat, y: AbsoFloat, radius: AbsoFloat, 
           fill: Fill | None | bool = True, stroke: Stroke | None = None,
           z: float = 0.0, parent_node: Node | None = None) -> Circle:
        """Create a circle at the specified position with optional fill and stroke.
        Args:
            x (AbsoFloat): The x-coordinate of the circle.
            y (AbsoFloat): The y-coordinate of the circle.
            radius (AbsoFloat): The radius of the circle.
            fill (Fill | None | bool): The fill color of the circle. 
                - If True is passed, defaults to an orange solid fill.
                - If None or False is passed, no fill will be set to None.
            stroke (Stroke | None): The stroke of the circle.
            z (float): The depth of the circle.
            parent_node (Node | None): The optional parent node of the circle.
        """
        fill = fill if isinstance(fill, Fill) else SolidFill(Colors.orange()) if fill else None
        return cls(
            radius=radius,
            fill=fill,
            stroke=stroke,
            z=z,
            transform=Transform2D(
                translate=Vec2(x, y),
                pivot=Vec2(0, 0),
                # No circular ref here because it's a new object
                _parent= None if parent_node is None else parent_node.transform,
            ),
            # No circular ref here because it's a new object
            _parent=parent_node,
        )
