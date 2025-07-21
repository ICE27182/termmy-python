

from __future__ import annotations
from termmy.colors import Color
from .buffer2d import Buffer2D

from typing import override, overload, TYPE_CHECKING, Self
from collections.abc import Iterable
from copy import copy
from itertools import islice
from warnings import deprecated

if TYPE_CHECKING:
    from termmy.display import DisplaySettings
    from .text_tag import TextTag
    from ..rendering import SSAA



class ColorBuffer(Buffer2D):
    __slots__ = ("width", "height", "data", "format_str")
    
    width: int
    height: int
    data: tuple[Color]
    format_str: str

    def __init__(self, width: int, height: int,
                 data: tuple[Color] | None = None):
        """
        Args:
            width (int): The width of the buffer. Must be a positive integer.
            height (int): The height of the buffer. Must be a positive 
                integer.
            data (tuple[Color] | None): The initial data for the buffer. If 
                provided, it must be a tuple of `Color` objects with a length
                equal to `width * height`. If not provided, the buffer will be
                initialized with default `Color` objects.
        Raises:
            ValueError: If `width` or `height` are not positive integers.
            ValueError: If `data` is provided and its length is not equal to
                `width * height`.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers."
                             f"Got {width=}, {height=}")
        if data and len(data) != width * height:
            raise ValueError("Data length must be equal to width * height.")
        self.width = width
        self.height = height
        self.data = data or tuple(Color() for _ in range(width*height))
        self.format_str = f"{"\033[48;2;%d;%d;%dm  " * width}\033[0m\n"

    @classmethod
    def from_display_settings(
        cls, 
        display_settings: DisplaySettings
    ) -> ColorBuffer:
        return cls(width=display_settings.width, 
                   height=display_settings.height)

    def resolve_to(self, buffer: ColorBuffer, ssaa: SSAA) -> Self:
        if (self.width != buffer.width * ssaa.level
            or self.height != buffer.height * ssaa.level):
            raise ValueError("Incompatible buffer dimensions.")
        # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        #  485    1.058    0.002    1.058    0.002 color_buffer.py:62(resolve_to) - 80x48 SSAAx2
        #   16    8.380    0.524    8.380    0.524 color_buffer.py:62(resolve_to) - 1280x720 SSAAx2
        squared_level = ssaa.level * ssaa.level
        l_l = buffer.width * squared_level # I dont know how to name this :(
        weight = 1.0 / squared_level
        for buffer_row_starting in range(0, buffer.height * buffer.width, buffer.width):
            self_col_starting = 0
            for x in range(buffer.width):
                r = g = b = a = 0.0
                self_starting = buffer_row_starting * squared_level
                for self_row_starting in range(self_starting,
                                               self_starting + l_l,
                                               self.width):
                    for dx in range(ssaa.level):
                        sample_color = self.data[self_row_starting + self_col_starting + dx]
                        r += sample_color.r
                        g += sample_color.g
                        b += sample_color.b
                        a += sample_color.a
                color = buffer.data[buffer_row_starting + x]
                color.r = r * weight
                color.g = g * weight
                color.b = b * weight
                color.a = a * weight
                self_col_starting += ssaa.level
        return self
        # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        #  836    2.018    0.002    2.018    0.002 color_buffer.py:62(resolve_to) - 80x48 SSAAx2
        #   16   10.066    0.629   10.066    0.629 color_buffer.py:62(resolve_to) - 1280x720 SSAAx2
        weight = 1.0 / (ssaa.level * ssaa.level)
        for y in range(buffer.height):
            for x in range(buffer.width):
                r = g = b = a = 0.0
                for dy in range(ssaa.level):
                    for dx in range(ssaa.level):
                        sample_color = self.data[(y * ssaa.level + dy) * self.width + (x * ssaa.level + dx)]
                        r += sample_color.r
                        g += sample_color.g
                        b += sample_color.b
                        a += sample_color.a
                color = buffer.data[y * buffer.width + x]
                color.r = r * weight
                color.g = g * weight
                color.b = b * weight
                color.a = a * weight
        return self
                
    @override
    def clear(self) -> None:
        for color in self.data:
            color.r = 0.0
            color.g = 0.0
            color.b = 0.0

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
            pixel_color.a = color.a
        return self
    
    @override
    def get_color(self, x: int, y: int) -> Color:
        """Get the color at (x, y). 

        Args:
            x (int): The horizontal coordinate of the pixel.
            y (int): The vertical coordinate of the pixel.

        Returns:
            Color: A new Color object at (x, y).

        Raises:
            IndexError: If `x` or `y` are out of bounds.
        """
        return self.get(x, y)

    @override
    def set_color(self, x: int, y: int, color: Color) -> ColorBuffer:
        """Set the color at (x, y) to `color`. 

        Args:
            x (int): The horizontal coordinate of the pixel.
            y (int): The vertical coordinate of the pixel.
            color (Color): The new color to be set at (x, y).
        
        Returns:
            ColorBuffer: The ColorBuffer object itself

        Raises:
            IndexError: If `x` or `y` are out of bounds.
        """
        return self.set(x, y, color)

    @override
    def blend_color(self, x: int, y: int, color: Color) -> ColorBuffer:
        """Add the given color to (x, y).

        Args:
            x (int): The horizontal coordinate of the pixel.
            y (int): The vertical coordinate of the pixel.
            color (Color): The color to add to the pixel at (x, y).

        Returns:
            ColorBuffer: The ColorBuffer object itself.

        Raises:
            IndexError: If `x` or `y` are out of bounds.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got x={x}, y={y}.")
        base_color = self.data[y*self.width + x]
        base_color.blend_over(color)
        return self

    @override
    def get(self, x: int, y: int) -> Color:
        """Get the color at (x, y).

        Args:
            x (int): The horizontal coordinate of the pixel.
            y (int): The vertical coordinate of the pixel.

        Returns:
            Color: A new Color object at (x, y).

        Raises:
            IndexError: If `x` or `y` are out of bounds.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got x={x}, y={y}.")
        return copy(self.data[y*self.width + x])

    @override
    def set(self, x: int, y: int, color: Color) -> ColorBuffer:
        """Set the color at (x, y).

        Args:
            x (int): The horizontal coordinate of the pixel.
            y (int): The vertical coordinate of the pixel.
            color (Color): The new color to be set at (x, y).

        Returns:
            ColorBuffer: The ColorBuffer object itself.

        Raises:
            IndexError: If `x` or `y` are out of bounds.
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
    def ansi_24(self) -> str:
        """Return an ANSI 24-bit color string representation of the buffer.

        Returns:
            str: The ANSI string representing the buffer.
        """
    @override
    @deprecated("Use `Scene` instead")
    def ansi_24(self, text_tags: TextTag) -> str: ...

    @override
    def ansi_24(self, text_tags = None) -> str:
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
            return f"{"\033[0m\n".join(str_buf)}\033[0m"
        else:
            return super().ansi_24(text_tags)
    
