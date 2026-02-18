
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from basics import Vertex, Color, Triangle, Buffer

@dataclass(slots=True, frozen=False)
class Rectangle:
    # Just having the top left and bottom right vertices is not enough
    # unless we dont use UV mapping
    tl: Final[Vertex]
    tr: Final[Vertex]
    bl: Final[Vertex]
    br: Final[Vertex]
    
    texture: Buffer
    
    @classmethod
    def create_from_size(
        cls, tl_x: float, tl_y: float, width: float, height: float,
        tl_uv: tuple[float, float], tr_uv: tuple[float, float], 
        bl_uv: tuple[float, float], br_uv: tuple[float, float],
        texture: Buffer,
    ) -> Rectangle:
        return cls(
            tl=Vertex(tl_x, tl_y, *tl_uv),
            tr=Vertex(tl_x + width, tl_y, *tr_uv),
            bl=Vertex(tl_x, tl_y + height, *bl_uv),
            br=Vertex(tl_x + width, tl_y + height, *br_uv),
            texture=texture,
        )
    
    def triangulate(self) -> list[Triangle]:
        return [
            Triangle(self.tl, self.bl, self.br, self.texture),
            Triangle(self.tl, self.br, self.tr, self.texture),
        ]
    