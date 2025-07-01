from __future__ import annotations

from abc import ABC, abstractmethod

from ...colors import Color
from ...core import NormFloat

class Fill(ABC):
    @abstractmethod
    def get_color(self, x: NormFloat, y: NormFloat) -> Color:
        """
        Get a new color object at the given coordinates.

        x and y are relative to the shape's origin.
        """

