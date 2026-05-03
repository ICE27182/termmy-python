

from __future__ import annotations
from termmy.colors import Color
from .buffer2d import Buffer2D

from typing import Iterable, Final
from copy import copy
from itertools import islice
from warnings import deprecated
from dataclasses import dataclass, field

@dataclass(slots=True)
class ColorBuffer:
    """
    A 2D buffer of RGBA colors, where each color is represented by a `Color` object.
    
    Attributes:
        width (Final[int]): The width of the buffer in pixels. 
        height (Final[int]): The height of the buffer in pixels.
        data (tuple[Color, ...]): 
            A flat tuple containing the color data for each pixel.
            
            A pixel can be accessed at coordinates (x, y) using the formula
            `data[y * width + x]`.
            
            If not provided, it will be initialized with the default Color.
    """
    
    width: Final[int]
    height: Final[int]
    data: tuple[Color, ...] = tuple()
    _format_str: str = field(init=False)

    def __post_init__(self):
        width, height, data = self.width, self.height, self.data
        
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError("Width and height must be integers. "
                            f"Got {type(width).__name__} for width and "
                            f"{type(height).__name__} for height.")
        
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers."
                             f"Got {width=}, {height=}")
            
        if data and len(data) != width * height:
            raise ValueError("Data length must be equal to width * height.")
        
        self.data = data or tuple(Color() for _ in range(width*height))
        self._format_str = f"{"\033[48;2;%d;%d;%dm  " * width}\033[0m\n"

    def fill(self, color: Color | None = None) -> ColorBuffer:
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
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got x={x}, y={y}.")
        return copy(self.data[y*self.width + x])

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
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got x={x}, y={y}.")
        base_color = self.data[y*self.width + x]
        base_color.r = color.r
        base_color.g = color.g
        base_color.b = color.b
        return self
    
    def ansi_24(self) -> str:
        return ansi24(self.width, self.height, self.data)



def ansi24(width: int, height: int, data: tuple[Color, ...]) -> str:
    return (
        f"{"\033[0m\r\n".join(
            "".join(
                    "\033[48;2;%d;%d;%dm  " % (round(color.r*255.0),
                                               round(color.g*255.0),
                                               round(color.b*255.0))
                    for color in islice(data, row_start, row_start + width)
            )
            for row_start in range(0, height * width, width)
        )}\033[0m"
    )


def ansi24_4x(width: int, height: int, data: tuple[Color, ...]) -> str:
    return (
        f"{"\033[0m\r\n".join(
            "".join(
                    "\033[38;2;%d;%d;%dm"
                    "\033[48;2;%d;%d;%dm▀" % (round(ct.r*255.0),
                                                round(ct.g*255.0),
                                                round(ct.b*255.0),
                                                round(cb.r*255.0),
                                                round(cb.g*255.0),
                                                round(cb.b*255.0))
                    for ct, cb in zip(islice(data, row_start, row_start + width), 
                                      islice(data, row_start + width, row_start + (width<<1)))
            )
            for row_start in range(0, height * width, 2 * width)
        )}\033[0m"
    )
