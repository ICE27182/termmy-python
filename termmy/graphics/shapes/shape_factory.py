

from ..node import Node
from ..fills import Fill, SolidFill
from ..stroke import Stroke
from ...core import Vec2, Vertex2, AbsoFloat, Transform2D
from ...colors import Colors
from .dot import Dot
from .lines import SimpleLine
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
    def create_simple_line_from_vertices(
        start: Vertex2, 
        end: Vertex2,
        fill: Fill | None = None,
        z: float = 0.0,
        parent_node: Node | None = None
    ) -> SimpleLine:
        """Create a simple line from two points.
        
        Args:
            start (Vertex2): The starting point of the line. 
                Will be stored as a reference in the returned object
            end (Vertex2): The ending point of the line.
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
    def create_simple_line_between_dots(
        start_dot: Dot,
        end_dot: Dot,
        fill: Fill | None = None,
        z: float = 0.0,
        parent_node: Node | None = None
    ) -> SimpleLine:
        """Create a simple line between two dots.
        The uv coordinates of the line will be set to (0.0, 0.0)
        for the starting point and (1.0, 1.0) for the ending point.

        Args:
            start_dot (Dot): The starting dot of the line. 
                The dot's translate will not be stored as a reference, so
                the starting point of the line will not move as the dot moves
                and vice versa.
            end_dot (Dot): The ending dot of the line.
                The dot's translate will not be stored as a reference, so
                the ending point of the line will not move as the dot moves
                and vice versa.
            fill (Fill | None): The fill of the line. 
                Defaults to a gray solid fill if not provided.
            z (float): The depth of the line.
            parent_node (Node | None): The optional parent node of the line.
        """
        start_vec = start_dot.transform.translate
        end_vec = end_dot.transform.translate
        return ShapeFactory.create_simple_line_from_vertices(
            start=Vertex2(start_vec.x, start_vec.y, 0.0, 0.0),
            end=Vertex2(end_vec.x, end_vec.y, 1.0, 1.0),
            fill=fill,
            z=z,
            parent_node=parent_node,
        )
    
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
                pivot=Vec2(0, 0),
                # No circular ref here because it's a new object
                _parent= None if parent_node is None else parent_node.transform,
            ),
            # No circular ref here because it's a new object
            _parent=parent_node,
        )


    