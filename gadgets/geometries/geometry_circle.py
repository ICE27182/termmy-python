
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Protocol
from math import pi, cos, sin

from basics import Vertex, Color, RasterizationTriangle, Buffer,  Transform
from linear_algebra import mat4t_mul_vec4t

_DOUBLE_PI = 2 * pi

class CircleUV(Protocol):
    def get_uv(self, x: float, y: float) -> tuple[float, float]: ...


@dataclass(slots=True, frozen=True)
class CircleUVRadialLinear:
    center_u: float
    center_v: float
    diff_u: float
    diff_v: float
    
    @classmethod
    def zero(cls) -> CircleUVRadialLinear:
        return cls(0.0, 0.0, 0.0, 0.0)
    
    @classmethod
    def create(cls, center_uv: tuple[float, float], 
              perimeter_uv: tuple[float, float], 
              radius: float) -> CircleUVRadialLinear:
        radius_reciprocal = 1.0 / radius
        return cls(
            center_u=center_uv[0],
            center_v=center_uv[1],
            diff_u=((perimeter_uv[0] - center_uv[0]) * radius_reciprocal),
            diff_v=((perimeter_uv[1] - center_uv[1]) * radius_reciprocal),
        )
    
    def get_uv(self, x: float, y: float) -> tuple[float, float]:
        t = (x*x + y*y) ** 0.5
        return (self.center_u + self.diff_u * t, 
                self.center_v + self.diff_v * t)


@dataclass(slots=True, frozen=False)
class Circle:
    radius: float
    
    texture: Buffer
    
    transform: Transform = field(default_factory=Transform.identity)
    
    uv_strategy: CircleUV = field(default_factory=CircleUVRadialLinear.zero)
    
    _vertex_num_reciprocal: float = 1/16
    _r_circ_vertex_coords: Final[list[tuple[float, float]]] = field(
        default_factory=list,
    )
    _r_center: Final[Vertex] = field(default_factory=Vertex.zero)
    _r_vertices: Final[list[Vertex]] = field(default_factory=list)
    _r_tris: Final[list[RasterizationTriangle]] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        self._reset_preallocation()
    
    @classmethod
    def create(cls, pos_x: float, pos_y: float, radius: float, color: Color) -> Circle:
        return cls(
            radius=radius,
            transform=Transform.translation(pos_x, pos_y, 0.0),
            texture=Buffer(1, 1, [Color(color.r, color.g, color.b, color.a)]),
            uv_strategy=CircleUVRadialLinear.zero(),
        )
    
    def set_vertex_num(self, vertex_num: int) -> None:
        if vertex_num < 3: raise ValueError('vertex_num must be at least 3')
        self._vertex_num_reciprocal = 1.0 / vertex_num
        self._reset_preallocation()
        
    def triangulate(self) -> list[RasterizationTriangle]:
        t_mat, txtr, radius = self.transform.mat4, self.texture, self.radius
        vs, ts, rc = self._r_vertices, self._r_tris, self._r_center
        cvs = self._r_circ_vertex_coords
        
        rc.x, rc.y, _, _ = mat4t_mul_vec4t(t_mat, (0.0, 0.0, 0.0, 1.0))
        
        for v, (x, y) in zip(vs, cvs):
            v.x, v.y, _, _ = mat4t_mul_vec4t(
                t_mat, 
                (radius * x, radius * y, 0.0, 1.0),
            )
        
        for t in ts: t.texture = txtr
            
        return self._r_tris
    
    def _reset_preallocation(self) -> None:
        n = round(1 / self._vertex_num_reciprocal)
        d = _DOUBLE_PI * self._vertex_num_reciprocal
        
        vs, ts = self._r_vertices, self._r_tris
        cvs = self._r_circ_vertex_coords
        
        vs.clear()
        ts.clear()
        cvs.clear()
        
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
        cvs.extend( (cos(t), sin(t)) for t in (i * d for i in range(n)) )
    