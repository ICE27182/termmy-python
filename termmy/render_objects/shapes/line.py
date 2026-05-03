
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final


from termmy.core import Transform
from termmy.core.linear_algebra import mat4t_mul_vec4t
from termmy.buffers import ColorBuffer, FrameBuffer
from termmy.rendering.basic_rendering_functions import render

from ..rasterization import RasterizationTriangle, Vertex
from .rectangle import Rectangle


@dataclass(slots=True, frozen=False)
class Line:
    thickness: float
    length: float
    
    texture: ColorBuffer
    
    lu: float
    lv: float
    ru: float
    rv: float
    
    transform: Transform = field(default_factory=Transform.identity)
    
    def to_rectangle(self) -> Rectangle:
        hl, ht = self.length * 0.5, self.thickness * 0.5
        lu, lv, ru, rv = self.lu, self.lv, self.ru, self.rv
        return Rectangle(
            tl=Vertex(-hl, -ht, lu, lv),
            tr=Vertex(hl, -ht, ru, rv),
            bl=Vertex(-hl, ht, lu, lv),
            br=Vertex(hl, ht, ru, rv),
            texture=self.texture,
            transform=self.transform.copy(),
        )
    
    def triangulate(self) -> list[RasterizationTriangle]:
        # TODO currently a new rectangle is created every time, and
        # all the 4 vertices and the 2 triangles will also have to be 
        # re-created
        return self.to_rectangle().triangulate()
    
    def render(self, frame_buffer: FrameBuffer) -> None:
        render(frame_buffer, self)    
