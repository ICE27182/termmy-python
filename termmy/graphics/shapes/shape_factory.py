

from typing import overload

from ..node import Node
from ..fills import Fill, SolidFill, FillFactory
from ..stroke import Stroke
from ...core import Vec2, AbsoFloat, Transform2D
from ...colors import Color, Colors
from .shape import Shape
from .dot import Dot
from .line import SimpleLine
from .circle import Circle

class ShapeFactory:
    @staticmethod
    def create_dot_at(x: AbsoFloat, y: AbsoFloat,
                      fill: SolidFill | None = None, 
                      z: float = 0.0,
                      parent_node: Node | None = None) -> Dot:
        """Create a dot at the specified position with optional fill.

        Args:
            x (AbsoFloat): The x-coordinate of the dot.
            y (AbsoFloat): The y-coordinate of the dot.
            fill (SolidFill | None): The fill color of the dot. 
                If not provided, defaults to red.
            z (float): The depth of the dot.
            parent_node (Node | None): The optional parent node of the dot.
        """
        return Dot(
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
    
    @staticmethod
    def create_dot_with_vec(pos: Vec2,
                            fill: SolidFill | None = None, 
                            z: float = 0.0,
                            parent_node: Node | None = None) -> Dot:
        """Create a new dot at pos.

        `pos` will be stored as a reference for the translate of the 
        returned object, and it will be copied for the pivot of 
        the returned object.

        Args:
            pos (Vec2): The position of the dot. Will be stored as a 
                reference for the translate of the returned object, 
                and it will be copied for the pivot.
            fill (SolidFill | None): The fill of the dot.
                If not provided, defaults to red.
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

    @staticmethod
    def create_simple_line_from_points(
        start: Vec2, 
        end: Vec2,
        fill: Fill | None = None,
        z: float = 0.0,
        parent_node: Node | None = None
    ) -> SimpleLine:
        """Create a simple line from two points.
        
        Args:
            start (Vec2Rela): The starting point of the line. 
                Will be stored as a reference in the returned object
            end (Vec2Rela): The ending point of the line.
                Will be stored as a reference in the returned object
            fill (Fill | None): The fill of the line. 
                Defaults to a gray solid fill if not provided.
            z (float): The depth of the line.
            parent_node (Node | None): The optional parent node of the line.
        """
        return SimpleLine(start=start,
                          end=end,
                          # instances of `Filler` are always True
                          fill=fill or SolidFill(Colors.gray()),
                          z=z,
                          transform=Transform2D(
                              pivot=Vec2(
                                  (start.x + end.x) * 0.5,
                                  (end.y + start.y) * 0.5,
                              ),
                              # No circular ref here because it's a new object
                              _parent= None if parent_node is None else parent_node.transform,
                          ),
                          # No circular ref here because it's a new object
                          _parent=parent_node)
    @staticmethod
    def create_simple_line_from_dots(
        start_dot: Dot,
        end_dot: Dot,
        fill: Fill | None = None,
        z: float = 0.0,
        parent_node: Node | None = None
    ) -> SimpleLine:
        """Create a simple line between two dots.

        Args:
            start_dot (Dot): The starting dot of the line.
                Its translate will be stored as a reference as the starting
                point of the line.
            end_dot (Dot): The ending dot of the line.
                Its translate will be stored as a reference as the ending
                point of the line.
            fill (Fill | None): The fill of the line. 
                Defaults to a gray solid fill if not provided.
            z (float): The depth of the line.
            parent_node (Node | None): The optional parent node of the line.
        """
        return ShapeFactory.create_simple_line_from_points(
            start=start_dot.transform.translate,
            end=end_dot.transform.translate,
            fill=fill,
            z=z,
            parent_node=parent_node,
        )
    @staticmethod
    def create_simple_line_with_two_ends(
        start: Vec2, 
        end: Vec2,
        z: float = 0.0,
        parent_node: Node | None = None
    ) -> Node:
        """Create node with a green simple line with two endpoints. 
        The starting point will be colored red 
        and the ending point will be colored blue.

        Args:
            start (Vec2Rela): The starting point of the line. 
                Will be stored as references in the returned object
            end (Vec2Rela): The ending point of the line.
                Will be stored as references in the returned object
            z (float): The depth of the line.
            parent_node (Node | None): The optional parent node of the line.
        """
        start_dot = ShapeFactory.create_dot_with_vec(
            start, 
            fill=SolidFill(Colors.red()),
            z=1.0,
        )
        end_dot = ShapeFactory.create_dot_with_vec(
            end, 
            fill=SolidFill(Colors.blue()),
            z=1.0,
        )
        line = ShapeFactory.create_simple_line_from_dots(
            start_dot=start_dot,
            end_dot=end_dot,
            fill=SolidFill(Colors.green()),
            z=0,
        )
        return Node(
            z=z, 
            transform=Transform2D(pivot=line.transform.pivot,
                                  _parent= None if parent_node is None else parent_node.transform),
            _parent=parent_node,
        ).add_child(start_dot).add_child(end_dot).add_child(line)
    
    @staticmethod
    def create_circle_at(x: AbsoFloat,
                         y: AbsoFloat,
                         radius: AbsoFloat,
                         fill: Fill | None | bool = True,
                         stroke: Stroke | None = None,
                         z: float = 0.0,
                         parent_node: Node | None = None) -> Circle:
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
        return Circle(
            radius=radius,
            fill=fill,
            stroke=stroke,
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


    