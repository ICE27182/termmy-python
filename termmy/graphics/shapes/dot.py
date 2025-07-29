

from __future__ import annotations

from .shape import Shape
from ..fills import SolidFill
from ..node import Node
from ...core import AbsoFloat, Transform2D, Vec2
from ...colors import Colors

from dataclasses import dataclass

@dataclass(slots=True)
class Dot(Shape):
    fill: SolidFill = None

    @classmethod
    def at(cls, x: AbsoFloat, y: AbsoFloat,
           fill: SolidFill | None = None,
           z: float = 0.0, parent_node: Node | None = None) -> Dot:
        """Create a dot at the specified position with optional fill.

        Args:
            x (AbsoFloat): The x-coordinate of the dot.
            y (AbsoFloat): The y-coordinate of the dot.
            fill (SolidFill | None): The fill color of the Dot. 
                If not provided, defaults to a red solid fill.
            z (float): The depth of the dot.
            parent_node (Node | None): The optional parent node of the dot.
        """
        return cls(
            # instances of `Fill` are always True
            fill=fill or SolidFill(Colors.red()),
            z=z,
            transform=Transform2D(
                translate=Vec2(x, y),
                pivot=Vec2(x, y),
                # No circular ref here because it's a new object
                _parent= None if parent_node is None else parent_node.transform,
            ),
            # No circular ref here because it's a new object
            _parent=parent_node,
        )
    
    @classmethod
    def create_with(cls, pos: Vec2,
                    fill: SolidFill | None = None,
                    z: float = 0.0, parent_node: Node | None = None) -> Dot:
        """Create a new dot at pos.

        `pos` will be stored as a reference for the translate of the 
        returned object, and it will be copied for the pivot of 
        the returned object.

        Args:
            pos (Vec2): The position of the dot. Will be stored as a 
                reference for the translate of the returned object, 
                and it will be copied for the pivot.
            fill (SolidFill | None): The fill color of the Dot. 
                If not provided, defaults to a red solid fill.
            z (float): The depth of the dot.
            parent_node (Node | None): The optional parent node of the dot.
        """
        return Dot(
            # instances of `Fill` are always True
            fill=fill or SolidFill(Colors.red()),
            z=z,
            transform=Transform2D(
                translate=pos,
                pivot=Vec2(pos.x, pos.y),
                # No circular ref here because it's a new object
                _parent= None if parent_node is None else parent_node.transform,
            ),
            # No circular ref here because it's a new object
            _parent=parent_node,
        )
    