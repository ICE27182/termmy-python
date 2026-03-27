
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from basics import Vertex, Color, RasterizationTriangle, Buffer
from gadgets.geometries.geometry_rectangle import Rectangle

@dataclass(slots=True, frozen=False)
class Line:
    thickness: float
    # start and end allows variable uv
    _start: Vertex
    _end: Vertex
    _texture: Buffer
    
    @classmethod
    def from_length(cls, length: float, start: Vertex, 
                    end_uv: tuple[float, float], 
                    thickness: float = 1.0) -> Line: ...
    
    def to_rectangle(self) -> Rectangle: ...
    
    def triangulate(self) -> list[RasterizationTriangle]:
        return self.to_rectangle().triangulate()
    
