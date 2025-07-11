

from __future__ import annotations

from typing import Self
from dataclasses import dataclass

@dataclass(slots=True)
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, other: Self) -> Vec3:
        return Vec3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __neg__(self) -> Vec3:
        return Vec3(
            -self.x,
            -self.y,
            -self.z,
        )
        
    def __sub__(self, other: Self) -> Vec3:
        return Vec3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
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
    
    def __iadd__(self, other: Self) -> Self:
        self.x += other.x
        self.y += other.y
        self.z += other.z        
        return self

    def __isub__(self, other: Self) -> Self:
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __imul__(self, scalar: int | float) -> Self:
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        return self

    def dot_prod(self, other: Self) -> float:
        """
        Dot (Inner) product
        """
        return self.x*other.x + self.y*other.y + self.z*other.z
    
    def cross_prod(self, other: Self) -> Vec3:
        """
        Cross product
        """
        return Vec3(
            self.y*other.z - self.z*other.y,
            self.z*other.x - self.x*other.z,
            self.x*other.y - self.y*other.x,
        )
    
    def icross_prod(self, other: Self) -> Self:
        """
        In-place cross product. Return itself.
        """
        x = self.x
        y = self.y
        z = self.z
        self.x = y*other.z - z*other.y
        self.y = z*other.x - x*other.z
        self.z = x*other.y - y*other.x
        return self
    
    def length(self) -> float:
        return (self.x * self.x + self.y * self.y + self.z * self.z)**0.5

