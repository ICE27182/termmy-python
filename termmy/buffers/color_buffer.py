

from termmy.colors import Color
from .buffer2d import Buffer2D
from .text_tag import TextTag

from typing import override, overload
from collections.abc import Iterable
from copy import copy
from itertools import islice


class ColorBuffer(Buffer2D):
    __slots__ = ("width", "height", "data", "format_str")
    def __init__(self, width: int, height: int,
                 data: tuple[Color, ...]|None = None):
        """
        `width` and `height` should be positive integers.
        """
        self.width = width
        self.height = height
        self.data = data or tuple(Color() for _ in range(width*height))
        self.format_str = ("\033[48;2;%d;%d;%dm  " * width) + "\033[0m\n"

    @override
    def clear(self) -> None:
        for color in self.data:
            color.r = 0
            color.g = 0
            color.b = 0

    @override
    def fill(self, color: Color | None = None) -> Buffer2D:
        """
        Fill the frame buffer with `color`.

        `color` will default to Color(1.0, 1.0, 1.0, 1.0) if not provided.
        """
        color = color or Color(1.0, 1.0, 1.0, 1.0)
        for pixel_color in self.data:
            pixel_color.r = color.r
            pixel_color.g = color.g
            pixel_color.b = color.b
        return self

    @overload
    def ansi_24(self) -> str: ...
    @overload
    def ansi_24(self, text_tags: Iterable[TextTag]) -> str: ...
    
    @override
    def get_color(self, x:int, y:int) -> Color:
        """
        Return a new Color object at (x, y).

        The return value is not a reference to the pixel stored in the buffer.

        Performs bounds checking.
        """
        return self.get(x, y)

    @override
    def set_color(self, x:int, y:int, color: Color) -> Buffer2D:
        """
        Set the given color at (x, y). 
        
        The color will not be a reference to the argument.

        Performs bounds checking.
        """
        return self.set(x, y, color)

    @override
    def add_color(self, x:int, y:int, color: Color) -> Buffer2D:
        """
        Add the given color to (x, y). 
        
        The color will not be a reference to the argument.

        Performs bounds checking.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got x={x}, y={y}.")
        base_color = self.data[y*self.width + x]
        base_color += color
        return self
    
    @override
    def get(self, x:int, y:int) -> Color:
        """
        Get the color at (x, y). 
        
        Performs bounds checking.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got x={x}, y={y}.")
        return copy(self.data[y*self.width + x])
    
    @override
    def set(self, x:int, y:int, color: Color) -> Buffer2D:
        """
        Set the color at (x, y). 
        
        Performs bounds checking.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got x={x}, y={y}.")
        base_color = self.data[y*self.width + x]
        base_color.r = color.r
        base_color.g = color.g
        base_color.b = color.b
        return self

    @override
    def ansi_24(self, text_tags: None | Iterable[TextTag] = None) -> str:
        """
        """
        if not text_tags:
            str_buf = []
            width = self.width
            for y in range(self.height):
                str_buf.append(
                    "".join(
                        "\033[48;2;%d;%d;%dm  " % (round(color.r*255.0), 
                                                   round(color.g*255.0), 
                                                   round(color.b*255.0))
                        for color in islice(self.data, y*width, (y+1)*width)
                    )
                )
            return "\033[0m\n".join(str_buf) + "\033[0m\n"
        else:
            return super().ansi_24(text_tags)
    
