
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from basics import Vertex, Color, RasterizationTriangle, Buffer, Transform
from gadgets.geometries.geometry_rectangle import Rectangle

@dataclass(slots=True, frozen=False)
class Line:
    thickness: float
    length: float
    
    texture: Buffer
    
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
            transform=Transform(self.transform.mat4),
        )
    
    def triangulate(self) -> list[RasterizationTriangle]:
        # TODO currently a new rectangle is created every time, and
        # all the 4 vertices and the 2 triangles will also have to be 
        # re-created
        return self.to_rectangle().triangulate()
    
