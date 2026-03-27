from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from basics import Vertex, Color, RasterizationTriangle, Buffer, Transform
from linear_algebra import mat4t_mul_vec4t

@dataclass(slots=True, frozen=False)
class Triangle:
    a: Final[Vertex]
    b: Final[Vertex]
    c: Final[Vertex]
    
    texture: Buffer
    
    transform: Transform = Transform.identity()
    
    _r_a: Final[Vertex] = field(default_factory=lambda: Vertex(0.0, 0.0, 0.0, 0.0))
    _r_b: Final[Vertex] = field(default_factory=lambda: Vertex(0.0, 0.0, 0.0, 0.0))
    _r_c: Final[Vertex] = field(default_factory=lambda: Vertex(0.0, 0.0, 0.0, 0.0))
    
    _r_tri: Final[RasterizationTriangle] = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, '_r_tri', 
                           RasterizationTriangle(self._r_a, self._r_b,
                                                 self._r_c, self.texture))
    
    def triangulate(self) -> list[RasterizationTriangle]:
        t_mat = self.transform.mat4
        
        ra, rb, rc = self._r_a, self._r_b, self._r_c
        a, b, c = self.a, self.b, self.c
        ra.x, ra.y, _, _ = mat4t_mul_vec4t(t_mat, (a.x, a.y, 0.0, 1.0))
        rb.x, rb.y, _, _ = mat4t_mul_vec4t(t_mat, (b.x, b.y, 0.0, 1.0))
        rc.x, rc.y, _, _ = mat4t_mul_vec4t(t_mat, (c.x, c.y, 0.0, 1.0))
        ra.u, ra.v = a.u, a.v
        rb.u, rb.v = b.u, b.v
        rc.u, rc.v = c.u, c.v
        return [self._r_tri]
    