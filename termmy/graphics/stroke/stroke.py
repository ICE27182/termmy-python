

from __future__ import annotations

from ...colors import Color
from ...core import NormFloat

from abc import ABC, abstractmethod

class Stroke(ABC):
    @abstractmethod
    def get_color(self, t: int, y: int) -> Color:
        """
        Get a new color object at the given coordinates.

        x and y are relative to the shape's origin.
        """

