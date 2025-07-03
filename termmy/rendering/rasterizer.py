

from ..core import NormFloat
from ..colors import Color
from ..buffers import MultisampleColorBuffer
from ..graphics import Dot, Line

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from .renderer import Renderer



class Rasterizer(ABC):
    @abstractmethod
    def __call__(self, 
                 renderer: Renderer,
                 dot: Dot,
                 width: int, 
                 height: int, 
                 x_offset: NormFloat,
                 y_offset: NormFloat,
                 out: list[Color],
                 ms_buffer: MultisampleColorBuffer 
                            | None = None) -> list[Color]: ...



def rasterize_dot(renderer: Renderer,
                  dot: Dot,
                  width: int, 
                  height: int, 
                  x_offset: NormFloat,
                  y_offset: NormFloat,
                  out: list[Color],
                  ms_buffer: MultisampleColorBuffer 
                             | None = None) -> list[Color]:
    raise NotImplementedError

def rasterize_line(renderer: Renderer,
                   dot: Line,
                   width: int, 
                   height: int, 
                   x_offset: NormFloat,
                   y_offset: NormFloat,
                   out: list[Color],
                   ms_buffer: MultisampleColorBuffer 
                              | None = None) -> list[Color]:
    raise NotImplementedError