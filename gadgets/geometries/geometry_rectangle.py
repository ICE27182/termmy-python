
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from basics import Vertex, Color, RasterizationTriangle, Buffer, Transform
from linear_algebra import mat4t_mul_vec4t

@dataclass(slots=True, frozen=False)
class Rectangle:
    # Just having the top left and bottom right vertices is not enough
    # unless we dont use UV mapping
    tl: Final[Vertex]
    tr: Final[Vertex]
    bl: Final[Vertex]
    br: Final[Vertex]
    
    texture: Buffer
    
    transform: Transform = field(default_factory=Transform.identity)
    
    _r_tl: Final[Vertex] = field(default_factory=Vertex.zero)
    _r_tr: Final[Vertex] = field(default_factory=Vertex.zero)
    _r_bl: Final[Vertex] = field(default_factory=Vertex.zero)
    _r_br: Final[Vertex] = field(default_factory=Vertex.zero)
    _r_tri_tl: Final[RasterizationTriangle] = field(init=False)
    _r_tri_bl: Final[RasterizationTriangle] = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, '_r_tri_tl', 
                           RasterizationTriangle(self._r_tl, self._r_bl,
                                                 self._r_br, self.texture))
        object.__setattr__(self, '_r_tri_bl', 
                           RasterizationTriangle(self._r_tl, self._r_br,
                                                 self._r_tr, self.texture))
    
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
    
    def triangulate(self) -> list[RasterizationTriangle]:
        t_mat = self.transform.mat4
        
        r_tl, r_tr, r_bl, r_br = self._r_tl, self._r_tr, self._r_bl, self._r_br
        
        tl, tr, bl, br = self.tl, self.tr, self.bl, self.br
        r_tl.x, r_tl.y, _, _ = mat4t_mul_vec4t(t_mat, (tl.x, tl.y, 0.0, 1.0))
        r_tr.x, r_tr.y, _, _ = mat4t_mul_vec4t(t_mat, (tr.x, tr.y, 0.0, 1.0))
        r_bl.x, r_bl.y, _, _ = mat4t_mul_vec4t(t_mat, (bl.x, bl.y, 0.0, 1.0))
        r_br.x, r_br.y, _, _ = mat4t_mul_vec4t(t_mat, (br.x, br.y, 0.0, 1.0))
        r_tl.u, r_tl.v, r_tr.u, r_tr.v = tl.u, tl.v, tr.u, tr.v
        r_bl.u, r_bl.v, r_br.u, r_br.v = bl.u, bl.v, br.u, br.v

        return [self._r_tri_tl, self._r_tri_bl]
    