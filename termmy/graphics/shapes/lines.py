

from __future__ import annotations

from .shape import Shape
from .dot import Dot
from .rectangle import Rectangle
from ..fills import Fill, SolidFill
from ..stroke import Stroke
from ..stroke import Stroke
from ..node import Node
from ...colors import Colors
from ...core import AbsoFloat, Vertex2, Transform2D, Vec2

from dataclasses import dataclass
from math import atan2
from copy import copy

@dataclass(slots=True)
class SimpleLine(Shape):
    """A straight line with a start and end point.
    It has no customizable weight and is always one pixel wide.
    It draws faster but is less versatile comparing to `Line`, which
    supports weight and stroke.
    """
    start: Vertex2 = None
    end: Vertex2 = None
    fill: Fill | None = None

    @staticmethod
    def create_with(
        start: Vertex2 | Dot, 
        end: Vertex2 | Dot,
        fill: Fill | None = None,
        z: float = 0.0,
        parent_node: Node | None = None
    ) -> SimpleLine:
        """Create a simple line from two points/dots.
        
        Args:
            start (Vertex2 | Dot): The starting point of the line. 
                Will be stored as a reference in the returned object.
            end (Vertex2 | Dot): The ending point of the line.
                Will be stored as a reference in the returned object.
            fill (Fill | None): The fill of the line. 
                Defaults to a gray solid fill if not provided.
            z (float): The depth of the line.
            parent_node (Node | None): The optional parent node of the line.
        """
        if isinstance(start, Dot):
            start = start.transform.translate
        if isinstance(end, Dot):
            end = end.transform.translate
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

    def length(self) -> float:
        return (self.end - self.start).length()
    
    def inclinantion(self) -> float:
        """Returns the angle of inclination in radians"""
        return atan2(self.end.y - self.start.y, self.end.x - self.start.x)

    def slope(self) -> float:
        return ((self.end.y - self.start.y) / (self.end.x - self.start.x) 
                if self.end.x != self.start.x else float('inf'))
    def slope_inv(self) -> float:
        return 1 / self.slope() if self.slope() != 0 else float('inf')
    
    def y_intercept(self) -> float:
        if self.end.x == self.start.x:
            raise ValueError("Vertical line has no y-intercept.")
        return self.start.y - (self.slope() * self.start.x)
    def x_intercept(self) -> float:
        if self.end.y == self.start.y:
            raise ValueError("Horizontal line has no x-intercept.")
        return (self.start.x - (self.start.y / self.slope()))


@dataclass(slots=True)
class Line(SimpleLine):
    stroke: Stroke | None = None
    weight: AbsoFloat = 2.0

    def rectangulate(self) -> Rectangle:
        lt = self.transform
        # A manual deepcopy
        transform = Transform2D(copy(lt.translate), copy(lt.pivot), 
                                lt.inheritance, lt.scale, 
                                lt._rotation_radians, copy(lt._rot_mat), 
                                # A reference to the same parent
                                lt._parent)
        transform.rotation_radians += self.inclinantion()
        transform.translate += self.start
        rectangle = Rectangle(self.length(), 
                              self.weight, 
                              self.fill,
                              self.stroke,
                              z=self.z,
                              transform=transform)
        return rectangle