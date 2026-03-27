from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from basics import Vertex, Color, RasterizationTriangle, Buffer, Transform

@dataclass(slots=True, frozen=False)
class Triangle:
    a: Final[Vertex]
    b: Final[Vertex]
    c: Final[Vertex]
    
    texture: Buffer
    
    transform: Transform = Transform.identity()
    
    def triangulate(self) -> RasterizationTriangle:
        return RasterizationTriangle(self.a, self.b, self.c, self.texture)
    