

from __future__ import annotations

from .buffer2d import Buffer2D
from .color_buffer import ColorBuffer
from ..rendering.anti_aliasing import MSAA, MSAAx4
from ..colors import Color, Colors

from typing import override, overload, TYPE_CHECKING


class MultisampleColorBuffer(Buffer2D):
    __slots__ = ("width", "height", "msaa", "data", "format_str")

    width: int
    height: int
    msaa: MSAA
    data: tuple[Color]
    format_str: str

    def __init__(self, width: int, height: int, msaa: MSAA,
                 data: tuple[Color] | None = None):
        """
        Args:
            width (int): The width of the buffer. Must be a positive integer.
            height (int): The height of the buffer. Must be a positive 
                integer.
            msaa (MSAA): The multisample anti-aliasing pattern to use.
            data (tuple[Color] | None): The flat initial data for the buffer. If 
                provided, it must be a tuple of `Color` objects with a length
                equal to `width * height * len(msaa)`. 
                If not provided, the buffer will be initialized with 
                default `Color` objects.
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
        self.msaa = msaa
        self.data = data or tuple(Color() for _ in range(width*height*len(msaa)))
        self.format_str = f"{"\033[48;2;%d;%d;%dm  " * width}\033[0m\n"
    
    def resolve(self) -> ColorBuffer:
        raise NotImplementedError

    @override
    def clear(self) -> MultisampleColorBuffer:
        self.fill(Color(0.0, 0.0, 0.0, 1.0))
        return self

    @override
    def fill(self, color: Color | None = None) -> MultisampleColorBuffer:
        for color in self.data:
            color.r = 0.0
            color.g = 0.0
            color.b = 0.0
            color.a = 0.0
        return self
    
    @override
    def get_color(self, x: int, y: int, i: int | None = None) -> Color:
        """Get the `i`th sample at (`x`, `y`). 

        Args:
            x (int): The horizontal coordinate of the pixel.
            y (int): The vertical coordinate of the pixel.
            i (int): The index of the sample to get. 
                If None, the average color is returned.

        Returns:
            Color: A new Color object.

        Raises:
            IndexError: If `x`, `y`, or `i` are out of bounds.
        """
        return self.get(x, y)
    
    @override
    def set_color(self, x: int, y: int, color: Color, 
                  i: int | None = None) -> MultisampleColorBuffer:
        """Set the `i`th sample at (`x`, `y`).

        Args:
            x (int): The horizontal coordinate of the pixel.
            y (int): The vertical coordinate of the pixel.
            color (Color): The new color to be set at (x, y).
            i (int): The index of the sample to set. 
        
        Returns:
            MultisampleColorBuffer: The MultisampleColorBuffer object itself

        Raises:
            IndexError: If `x`, `y` or `i` are out of bounds.
        """
        return self.set(x, y, color, i)

    @override
    def blend_color(self, x: int, y: int, color: Color, i: int | None = None) -> MultisampleColorBuffer:
        raise NotImplementedError
    
    @override
    def get(self, x: int, y: int, i: int | None = None) -> Color:
        """Get the `i`th sample at (`x`, `y`).

        Args:
            x (int): The horizontal coordinate of the pixel.
            y (int): The vertical coordinate of the pixel.
            i (int | None): The index of the sample to get. 
                If `None`, return the average color of all samples.
        
        Returns:
            Color: The color of the `i'th sample or 
                the average color at (`x`, `y`).
        
        Raises:
            IndexError: If `x`, `y` or `i` are out of bounds.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got {x=}, {y=}.")
        sample_num = len(self.msaa)
        if not (i is None or 0 <= i < sample_num):
            raise IndexError("i out of bounds. "
                             f"Expected i to be None or 0 <= i < {sample_num}, "
                             f"but got {i=}.")
        if i is None:
            sample_num_inv = 1 / sample_num
            start = (y*self.width + x) * sample_num
            samples = self.data[start : start + sample_num]
            return Color(
                sum(color.r for color in samples) * sample_num_inv,
                sum(color.g for color in samples) * sample_num_inv,
                sum(color.b for color in samples) * sample_num_inv,
                sum(color.a for color in samples) * sample_num_inv,
            )
        else:
            return self.data[(y*self.width + x) * sample_num + i]
    
    
