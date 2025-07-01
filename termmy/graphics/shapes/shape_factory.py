

from typing import overload

from .shape import Shape
from .line import Line
from ..fills import Fill, SolidFill
from ...core import Vec2Rela
from ...colors import Color

class ShapeFactory:
    @staticmethod
    def create_line_from_points(start: Vec2Rela, end: Vec2Rela, 
                                weight: float = 0.02, 
                                fill: Fill | None = None) -> Line:
        """Create a line from two points.
        
        Args:
            start (Vec2Rela): The starting point of the line.
            end (Vec2Rela): The ending point of the line.
            weight (float): The thickness of the line.
            fill (Fill | None): The fill of the line. Defaults to a gray solid fill if None.

        Returns:
            Line: The created line.
        """
        fill = SolidFill(Color(0.5, 0.5, 0.5, 1.0)) if fill is None else fill
        return Line(stroke=None,
                    start=start,
                    end=end,
                    weight=weight,
                    fill=fill,
                    width=abs(end.x - start.x),
                    height=abs(end.y - start.y))
    