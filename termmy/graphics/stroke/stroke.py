

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..shapes import Shape


class Stroke(ABC):
    @abstractmethod
    def get_stroke(self) -> tuple[Shape]:
        """Gets a tuple of shapes that represent the stroke.
        """
