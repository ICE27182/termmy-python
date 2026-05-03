from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Callable

from termmy.core import Transform
from termmy.core.linear_algebra import mat4t_mul_vec4t
from termmy.buffers import ColorBuffer, FrameBuffer
from termmy.rendering.basic_rendering_functions import render

from ..rasterization import RasterizationTriangle, Vertex


@dataclass(slots=True, frozen=False)
class Triangle:
    a: Final[Vertex]
    b: Final[Vertex]
    c: Final[Vertex]
    
    texture: ColorBuffer
    
    transform: Transform = field(default_factory=Transform.identity)
    
    # NOTE _r_* is to optimize out the per-render allocation, 
    # but is not thread-safe.
    
    _r_a: Final[Vertex] = field(default_factory=Vertex.zero)
    _r_b: Final[Vertex] = field(default_factory=Vertex.zero)
    _r_c: Final[Vertex] = field(default_factory=Vertex.zero)
    
    _r_tri: Final[RasterizationTriangle] = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, '_r_tri', 
                           RasterizationTriangle(self._r_a, self._r_b,
                                                 self._r_c, self.texture))
    
    def triangulate(self) -> list[RasterizationTriangle]:
        t_mat = self.transform.get_matrix()
        
        ra, rb, rc = self._r_a, self._r_b, self._r_c
        a, b, c = self.a, self.b, self.c
        ra.x, ra.y, _, _ = mat4t_mul_vec4t(t_mat, (a.x, a.y, 0.0, 1.0))
        rb.x, rb.y, _, _ = mat4t_mul_vec4t(t_mat, (b.x, b.y, 0.0, 1.0))
        rc.x, rc.y, _, _ = mat4t_mul_vec4t(t_mat, (c.x, c.y, 0.0, 1.0))
        ra.u, ra.v = a.u, a.v
        rb.u, rb.v = b.u, b.v
        rc.u, rc.v = c.u, c.v
        return [self._r_tri]
    
    def render(self, frame_buffer: FrameBuffer) -> None:
        render(frame_buffer, self)