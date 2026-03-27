
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Protocol
from math import pi, cos, sin

from basics import Vertex, Color, RasterizationTriangle, Buffer,  Transform
from linear_algebra import mat4t_mul_vec4t

_HALF_PI = pi / 2

class CircleUV(Protocol):
    def get_uv(self, circle: Circle, x: float, y: float) -> tuple[float, float]: ...


@dataclass(slots=True, frozen=True)
class CircleUVRadialLinear:
    diff_u: float
    diff_v: float
    
    @classmethod
    def zero(cls) -> CircleUVRadialLinear:
        return cls(0.0, 0.0)
    
    @classmethod
    def from_(cls, center_uv: tuple[float, float], 
              perimeter_uv: tuple[float, float], 
              radius: float) -> CircleUVRadialLinear:
        radius_reciprocal = 1.0 / radius
        return cls(
            diff_u=((perimeter_uv[0] - center_uv[0]) * radius_reciprocal),
            diff_v=((perimeter_uv[1] - center_uv[1]) * radius_reciprocal),
        )
    
    def get_uv(self, circle: Circle, x: float, y: float) -> tuple[float, float]:
        t = (x*x + y*y) ** 0.5
        c = circle.center
        return (c.u + self.diff_u * t, 
                c.v + self.diff_v * t)


@dataclass(slots=True, frozen=False)
class Circle:
    # Just having the top left and bottom right vertices is not enough
    # unless we dont use UV mapping
    center: Final[Vertex]
    radius: float
    
    texture: Buffer
    
    transform: Transform = field(default_factory=Transform.identity)
    
    uv_strategy: CircleUV = field(default_factory=CircleUVRadialLinear.zero)
    vertex_num: int = 16
    
    _r_center: Final[Vertex] = field(default_factory=Vertex.zero)
    _r_vertices: Final[list[Vertex]] = field(default_factory=list)
    _r_tris: Final[list[RasterizationTriangle]] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        self.reset_preallocation()
    
    def reset_preallocation(self) -> None:
        vs, ts, n = self._r_vertices, self._r_tris, self.vertex_num
        vs.clear()
        ts.clear()
        vs.extend(Vertex.zero() for _ in range(n))
        ts.extend(
            RasterizationTriangle(
                a=vs[i],
                b=vs[i + 1],
                c=self._r_center,
                texture=self.texture,
            )
            for i in range(-1, n - 1)
        )
    
    def triangulate(self) -> list[RasterizationTriangle]:
        t_mat, txtr = self.transform.mat4, self.texture
        c, rc  = self.center, self._r_center
        vs, ts = self._r_vertices, self._r_tris
        
        d = _HALF_PI / self.vertex_num
        dd = 2 * d
        
        rc.x, rc.y, _, _ = mat4t_mul_vec4t(t_mat, (c.x, c.y, 0.0, 1.0))
        
        for i, v in enumerate(vs):
            t = -d + i * dd
            v.x, v.y, _, _ = mat4t_mul_vec4t(t_mat, (cos(t), sin(t), 0.0, 1.0))
        
        for t in ts: t.texture = txtr
            
        return self._r_tris
    