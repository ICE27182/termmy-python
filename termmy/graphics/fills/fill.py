from __future__ import annotations

from abc import ABC, abstractmethod

from ...colors import Color
from ...core import AbsoFloat

class Fill(ABC):
    @abstractmethod
    def get_color(self, u: AbsoFloat, v: AbsoFloat) -> Color:
        """
        Get a new color object at the given coordinates.
        """

