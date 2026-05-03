from dataclasses import dataclass
from typing import Final

from termmy.buffers import ColorBuffer

@dataclass(slots=True, frozen=False)
class Vertex:
    x: float
    y: float
    u: float
    v: float
    
    @classmethod
    def zero(cls) -> Vertex:
        return cls(0.0, 0.0, 0.0, 0.0)
    
    def __repr__(self) -> str:
        return "Vertex(x=%.3f, y=%.3f, u=%.3f, v=%.3f)" % (
            self.x, self.y, self.u, self.v
        )

@dataclass(slots=True, frozen=False)
class RasterizationTriangle:
    a: Final[Vertex]
    b: Final[Vertex]
    c: Final[Vertex]
    texture: ColorBuffer
