from __future__ import annotations

from dataclasses import dataclass
from random import random

Matrix4dTuple = tuple[float, float, float, float,
                      float, float, float, float,
                      float, float, float, float,
                      float, float, float, float]

@dataclass(slots=True, frozen=False)
class Matrix4d:
    m00: float; m01: float ;m02: float; m03: float
    m10: float; m11: float; m12: float; m13: float
    m20: float; m21: float; m22: float; m23: float
    m30: float; m31: float; m32: float; m33: float
    
    @classmethod
    def identity(cls) -> Matrix4d:
        return cls(
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        )
    @classmethod
    def random(cls) -> Matrix4d:
        return cls(
            random(), random(), random(), random(),
            random(), random(), random(), random(),
            random(), random(), random(), random(),
            random(), random(), random(), random(),
        )
    
    def to_string(self, digits: int = 3, precision: int = 3) -> str:
        fmt = f"%{digits}.{precision}f"
        m = self
        return (
            f"{fmt % m.m00} {fmt % m.m01} {fmt % m.m02} {fmt % m.m03}\n"
            f"{fmt % m.m10} {fmt % m.m11} {fmt % m.m12} {fmt % m.m13}\n"
            f"{fmt % m.m20} {fmt % m.m21} {fmt % m.m22} {fmt % m.m23}\n"
            f"{fmt % m.m30} {fmt % m.m31} {fmt % m.m32} {fmt % m.m33}"
        )
    
    def to_tuple(self) -> Matrix4dTuple:
        return (
            self.m00, self.m01, self.m02, self.m03,
            self.m10, self.m11, self.m12, self.m13,
            self.m20, self.m21, self.m22, self.m23,
            self.m30, self.m31, self.m32, self.m33,
        )
