

from termmy.core import Color
from .frame_buffer_base import FrameBufferBase
from .text_tag import TextTag

from typing import override, overload
from collections.abc import Iterable
from itertools import islice


class FrameBuffer(FrameBufferBase):
    __slots__ = ("width", "height", "data", "format_str")
    channel_num = 3
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
    def fill(self, color: Color | None = None) -> FrameBufferBase:
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
        """
        return self.data[y*self.width + x]

    @override
    def set_color(self, x:int, y:int, color: Color) -> FrameBufferBase:
        """
        Set the given color at (x, y). 
        
        The color will not be a reference to the argument.
        """
        old_color = self.data[y*self.width + x]
        old_color.r = color.r
        old_color.g = color.g
        old_color.b = color.b
        old_color.a = color.a
        return self

    @override
    def add_color(self, x:int, y:int, color: Color) -> FrameBufferBase:
        """
        Set the given color at (x, y). 
        
        The color will not be a reference to the argument.
        """
        base_color = self.data[y*self.width + x]
        base_color += color
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
    
