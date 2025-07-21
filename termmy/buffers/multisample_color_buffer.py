

from __future__ import annotations

from .buffer2d import Buffer2D
from .color_buffer import ColorBuffer
from ..colors import Color, Colors

from typing import override, TYPE_CHECKING, Self
from itertools import islice

if TYPE_CHECKING:
    from ..rendering import MSAA, MSAAx4

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
        self.data = data or tuple(
            Color() for _ in range((width * height) << msaa._level)
        )
        self.format_str = f"{"\033[48;2;%d;%d;%dm  " * width}\033[0m\n"
    
    def resolve_to(self, buffer: ColorBuffer) -> ColorBuffer:
        """Resolve the buffer to the color buffer passed in.

        Returns:
            ColorBuffer: A reference to the buffer passed in.
        
        Raises:
            ValueError: If the dimensions of the buffer passed in do not match
                the dimensions of this buffer.
        """
        if self.width != buffer.width or self.height != buffer.height:
            raise ValueError("Dimensions of the buffer passed in do not "
                             "match. The `MultisampleColorBuffer` has "
                             f"dimensions of {self.width}x{self.height}, and "
                             "the target buffer has dimensions of "
                             f"{buffer.width}x{buffer.height}")
        level = self.msaa._level
        sample_num = 1 << level
        sample_num_inv = 1 / sample_num
        for i, color in enumerate(buffer.data):
            colors = self.data[i << level : (i << level) + sample_num]
            color.r = sum(c.r for c in colors) * sample_num_inv
            color.g = sum(c.g for c in colors) * sample_num_inv
            color.b = sum(c.b for c in colors) * sample_num_inv
            color.a = sum(c.a for c in colors) * sample_num_inv

    @override
    def clear(self) -> Self:
        self.fill(Color(0.0, 0.0, 0.0, 1.0))
        return self

    @override
    def fill(self, color: Color | None = None) -> Self:
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
                  i: int | None = None) -> Self:
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
        sample_num = len(self.msaa.pattern)
        if not (i is None or 0 <= i < sample_num):
            raise IndexError("i out of bounds. "
                             f"Expected i to be None or 0 <= i < {sample_num}, "
                             f"but got {i=}.")
        if i is None:
            sample_num_inv = 1 / sample_num
            start = (y*self.width + x) << self.msaa._level
            samples = self.data[start : start + sample_num]
            return Color(
                sum(color.r for color in samples) * sample_num_inv,
                sum(color.g for color in samples) * sample_num_inv,
                sum(color.b for color in samples) * sample_num_inv,
                sum(color.a for color in samples) * sample_num_inv,
            )
        else:
            return self.data[(y*self.width + x) * sample_num + i]
    
    @override
    def set(self, x: int, y: int, color: Color, i: int | None = None) -> Self:
        """Set the `i`th sample at (`x`, `y`).

        Args:
            x (int): The horizontal coordinate of the pixel.
            y (int): The vertical coordinate of the pixel.
            color (Color): The color to set to.
            i (int | None): The index of the sample to get. 
                If `None`, return the average color of all samples.
        
        Returns:
            MultisampleColorBuffer: The MultisampleColorBuffer object itself.
        
        Raises:
            IndexError: If `x`, `y` or `i` are out of bounds.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got {x=}, {y=}.")
        sample_num = len(self.msaa.pattern)
        if not (i is None or 0 <= i < sample_num):
            raise IndexError("i out of bounds. "
                             f"Expected i to be None or 0 <= i < {sample_num}, "
                             f"but got {i=}.")
        start = (y*self.width + x) << self.msaa._level
        if i is None:
            for old_color in islice(self.data, start, start + sample_num):
                old_color.r = color.r
                old_color.g = color.g
                old_color.b = color.b
                old_color.a = color.a
        else:
            old_color = self.data[start + i]
            old_color.r = color.r
            old_color.g = color.g
            old_color.b = color.b
            old_color.a = color.a
        return self
    
    
