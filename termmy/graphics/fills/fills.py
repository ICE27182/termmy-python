

from .fill import Fill
from ...colors import Color
from ...core import Vec2, NormFloat, UV

from typing import override
from dataclasses import dataclass
from collections.abc import Iterable
from bisect import bisect_left

@dataclass(slots=True)
class SolidFill(Fill):
    color: Color
    @override
    def get_color(self, x: int, y: int) -> Color: 
        c = self.color
        return Color(c.r, c.g, c.b, c.a)

@dataclass(slots=True)
class LinearFill(Fill):
    start: UV
    end: UV
    direction: Vec2
    # hidden for maintaing order
    _stops: list[tuple[NormFloat, Color]]

    @property
    def stops(self) -> tuple[tuple[NormFloat, Color]]:
        return tuple(self._stops)
    
    @stops.setter
    def stops(self, values: Iterable[tuple[NormFloat, Color]]):
        if len(values) < 2:
            raise ValueError("LinearFill must have at least two stops.")
        values = sorted(values, key=lambda v: v[0])
        if not values[0][0] == 0.0 or not values[-1][0] == 1.0:
            raise ValueError("The positions of LinearFill stops must "
                             "start at 0.0 and end at 1.0")
        if any(values[i][0] == values[i+1][0] for i in range(len(values)-1)):
            raise ValueError("Two colors must not have the same position.")
    

    def get_color(self, x, y):
        return super().get_color(x, y)