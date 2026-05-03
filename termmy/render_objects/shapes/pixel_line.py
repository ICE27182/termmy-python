
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from termmy.core import Transform
from termmy.core.linear_algebra import mat4t_mul_vec4t
from termmy.colors import Color
from termmy.buffers import ColorBuffer, FrameBuffer
from termmy.rendering.basic_rendering_functions import rasterize_pixel_line

from ..rasterization import RasterizationTriangle, Vertex

@dataclass(slots=True, frozen=True)
class PixelLine:
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    color: Color
    
    def render(self, frame_buffer: FrameBuffer) -> None:
        rasterize_pixel_line(
            self.start_x, self.start_y,
            self.end_x, self.end_y,
            self.color,
            frame_buffer.color_buffer,
        )
