

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
    def get_color(self, x: NormFloat, y: NormFloat) -> Color: 
        c = self.color
        return Color(c.r, c.g, c.b, c.a)

@dataclass(slots=True)
class LinearFill(Fill):
    # hidden for maintaing order
    _stops: list[tuple[NormFloat, Color]]

    @property
    def stops(self) -> tuple[tuple[NormFloat, Color]]:
        return tuple(self._stops)
    
    @stops.setter
    def stops(self, values: Iterable[tuple[NormFloat, Color]]):
        if len(values) < 2:
            raise ValueError("LinearFill must have at least two stops.")
        values = sorted(values, key=lambda val: val[0])
        if not values[0][0] == 0.0 or not values[-1][0] == 1.0:
            raise ValueError("The positions of LinearFill stops must "
                             "start at 0.0 and end at 1.0")
        if any(values[i][0] == values[i+1][0] for i in range(len(values)-1)):
            raise ValueError("Two colors must not have the same position.")

    def add_stop(self, position: NormFloat, color: Color):
        if position < 0.0 or position > 1.0:
            raise ValueError("Position must be between 0.0 and 1.0")
        insertion_pos = bisect_left(self._stops, position, 
                                    key=lambda v: v[0])
        if self._stops[insertion_pos][0] == position:
            raise ValueError("Color already exists at the given position.")
        self._stops.insert(insertion_pos, (position, color))
    
    def remove_stop(self, position: NormFloat) -> Color:
        stops = self._stops
        length = len(stops)
        if length <= 2:
            raise ValueError("LinearFill must have at least two stops.")
        index = bisect_left(stops, position, key=lambda v: v[0])
        if stops[index][0] != position:
            raise ValueError("No color stop found at the given position.")
        if index == 0:
            stops[1] = (0.0, stops[1][1])
            return stops.pop(index)[1]
        elif index == length - 1:
            stops[length - 2] = (1.0, stops[length - 2][1])
            return stops.pop(index)[1]

    def get_color(self, u, v) -> Color:
        """Only `u` will be taken into account.
        
        Returns:
            Color: A new Color object
        """
        stops = self._stops
        if u <= 0.0:
            color = stops[0][1]
            return Color(color.r, color.g, color.b, color.a)
        if u >= 1.0:
            color = stops[-1][1]
            return Color(color.r, color.g, color.b, color.a)
        # Perform linear interpolation between the color stops
        # Find the two stops to interpolate between
        upper_index = bisect_left(self._stops, u, key=lambda val: val[0])
        lower_index = upper_index - 1
        lower_stop = self._stops[lower_index]
        upper_stop = self._stops[upper_index]
        # Interpolate between the two stops
        t = (u - lower_stop[0]) / (upper_stop[0] - lower_stop[0])
        t_ = 1 - t
        color_l = lower_stop[1]
        color_r = upper_stop[1]
        return Color(
            color_l.r * t_ + color_r.r * t,
            color_l.g * t_ + color_r.g * t,
            color_l.b * t_ + color_r.b * t,
            color_l.a * t_ + color_r.a * t,
        )