

from __future__ import annotations

from typing import Self
from dataclasses import dataclass

@dataclass(slots=True)
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, other: Self | int | float) -> Vec3:
        if isinstance(other, Vec3):
            return Vec3(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z,
            )
        else:
            return Vec3(
                self.x + other,
                self.y + other,
                self.z + other,
            )
    __radd__ = __add__

    def __neg__(self) -> Vec3:
        return Vec3(
            -self.x,
            -self.y,
            -self.z,
        )
        
    def __sub__(self, other: Self | int | float) -> Vec3:
        if isinstance(other, Vec3):
            return Vec3(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z,
            )
        else:
            return Vec3(
                self.x - other,
                self.y - other,
                self.z - other,
            )
    def __rsub__(self, other: int | float) -> Vec3:
        return Vec3(
            other - self.x,
            other - self.y,
            other - self.z,
        )
    
    def __mul__(self, other: int | float) -> Vec3:
        return Vec3(
            self.x * other,
            self.y * other,
            self.z * other,
        )
    __rmul__ = __mul__

    def __truediv__(self, other: int | float) -> Vec3:
        inverse = 1 / other
        return Vec3(
            self.x * inverse,
            self.y * inverse,
            self.z * inverse,
        )
    
    def __iadd__(self, other: Self | int | float) -> Self:
        if isinstance(other, Vec3):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        else:
            self.x += other
            self.y += other
            self.z += other
        return self

    def __isub__(self, other: Self | int | float) -> Self:
        if isinstance(other, Vec3):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        else:
            self.x -= other
            self.y -= other
            self.z -= other
        return self

    def __imul__(self, other: int | float) -> Self:
        self.x *= other
        self.y *= other
        self.z *= other
        return self
    
    def __idiv__(self, other: int | float) -> Self:
        inverse = 1 / other
        self.x *= inverse
        self.y *= inverse
        self.z *= inverse
        return self

    def dot(self, other: Self) -> float:
        """
        Dot (Inner) product
        """
        return self.x*other.x + self.y*other.y + self.z*other.z
    
    def cross(self, other: Self) -> Vec3:
        """
        Cross product
        """
        return Vec3(
            self.y*other.z - self.z*other.y,
            self.z*other.x - self.x*other.z,
            self.x*other.y - self.y*other.x,
        )
    
    def icross(self, other: Self) -> Self:
        """
        In-place cross product. Return itself.
        """
        self.x = self.y*other.z - self.z*other.y
        self.y = self.z*other.x - self.x*other.z
        self.z = self.x*other.y - self.y*other.x
        return self

