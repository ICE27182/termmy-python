

from __future__ import annotations

from .shape import Shape
from ..fills import Fill, SolidFill
from ..stroke import Stroke, SimpleStroke
from ..node import Node
from ...core import AbsoFloat, Transform2D, Vec2
from ...colors import Colors

from dataclasses import dataclass

@dataclass(slots=True)
class Ring(Shape):
    """
    The uv coordinates of the center of a ring are (0.5, 0.5).
    """
    inner_radius: AbsoFloat
    outer_radius: AbsoFloat
    fill: Fill | None = None
    stroke: Stroke | None = None

    @classmethod
    def at(cls, x: AbsoFloat, y: AbsoFloat, 
           inner_radius: AbsoFloat, outer_radius: AbsoFloat,
           fill: Fill | None | bool = True, stroke: Stroke | None = None, 
           z: float = 0.0, parent_node: Node | None = None) -> Ring:
        """Create a ring at the specified position with optional fill and stroke.
        Args:
            x (AbsoFloat): The x-coordinate of the ring.
            y (AbsoFloat): The y-coordinate of the ring.
            inner_radius (AbsoFloat): The inner radius of the ring.
            outer_radius (AbsoFloat): The outer radius of the ring.
            fill (Fill | None | bool): The fill color of the ring. 
                - If True is passed, defaults to an indigo solid fill.
                - If None or False is passed, no fill will be set to None.
            stroke (Stroke | None): The stroke of the ring.
            z (float): The depth of the ring.
            parent_node (Node | None): The optional parent node of the ring.
        """
        fill = fill if isinstance(fill, Fill) else SolidFill(Colors.indigo()) if fill else None
        return cls(
            inner_radius=inner_radius,
            outer_radius=outer_radius,
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
    