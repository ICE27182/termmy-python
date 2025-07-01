

from __future__ import annotations

from dataclasses import dataclass
from abc import ABC

from ..node import Node
from ..fills.fill import Fill
from ..stroke.stroke import Stroke
from ...colors import Color
from ...core import NormFloat

@dataclass(slots=True, kw_only=True)
class Shape(Node, ABC):
    fill: Fill | None
    stroke: Stroke | None
    width: NormFloat
    height: NormFloat
    
    def move_center_to(self, center_x: NormFloat, center_y: NormFloat) -> Shape:
        """Move the center of the shape to the given coordinates. 
        The center of the shape is the center of its bounding box, which
        is of `width` and `height`.

        Returns:
            Shape: It returns itself for method chaining.
        """
        self.x = center_x - self.width / 2.0
        self.y = center_y - self.height / 2.0
        return self
