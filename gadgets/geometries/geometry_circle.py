
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Protocol
from math import pi, cos, sin

from basics import Vertex, Color, RasterizationTriangle, Buffer

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
    
    uv_strategy: CircleUV = CircleUVRadialLinear.zero()
    vertex_num: int = 16
    
    def triangulate(self) -> list[RasterizationTriangle]:
        d = _HALF_PI / self.vertex_num
        dd = 2 * d
        out = []
        for i in range(self.vertex_num):
            t1 = -d + i * dd
            t2 = t1 + dd
            x1, y1 = cos(t1), sin(t1)
            x2, y2 = cos(t2), sin(t2)
            out.append(RasterizationTriangle(
                a=Vertex(x1, y1, *self.uv_strategy.get_uv(self, x1, y1)),
                b=Vertex(x2, y2, *self.uv_strategy.get_uv(self, x2, y2)),
                c=self.center,
                texture=self.texture,
            ))
        return out
    