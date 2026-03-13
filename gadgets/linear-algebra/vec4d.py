from __future__ import annotations

from dataclasses import dataclass
from random import random

Vector4dTuple = tuple[float, float, float, float]

@dataclass(slots=True, frozen=False)
class Vec4d:
    x: float; y: float; z: float; w: float
    
    @classmethod
    def random(cls) -> Vec4d:
        return cls(random(), random(), random(), random())
    
    def to_string(self, digits: int = 3, precision: int = 3) -> str:
        fmt = f"%{digits}.{precision}f"
        v = self
        return f"{fmt % v.x} {fmt % v.y} {fmt % v.z} {fmt % v.w}"
    
    def to_tuple(self) -> Vector4dTuple:
        return (self.x, self.y, self.z, self.w)
    