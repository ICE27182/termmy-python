

from __future__ import annotations

from ..shapes import Shape
from ...colors import Color
from ...core import NormFloat

from abc import ABC, abstractmethod

class Stroke(ABC):
    @abstractmethod
    def get_stroke(self) -> tuple[Shape]:
        """Gets a tuple of shapes that represent the stroke.
        """
