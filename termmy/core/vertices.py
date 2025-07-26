

from __future__ import annotations

from .type_aliases import NormFloat
from .vec2 import Vec2, UV

from typing import Self
from dataclasses import dataclass

@dataclass(slots=True)
class Vertex2:
    """
    A vertex in 2D space with additional UV coordinates.
    This has the same attributes as `Vertex2(Vec2, UV)` but with 
    lower overhead without MRO.

    Note that while it has `u` and `v` attributes, its methods
    focus on 2D vector operations rather than mapping.

    Attributes:
        x (float): The x-coordinate of the vertex.
        y (float): The y-coordinate of the vertex.
        u (NormFloat): The u-coordinate for mapping.
        v (NormFloat): The v-coordinate for mapping.
    """
    x: float
    y: float
    u: NormFloat
    v: NormFloat

    def __add__(self, other) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)
    def __iadd__(self, other) -> Self:
        self.x += other.x
        self.y += other.y
        return self
    def __sub__(self, other) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)
    def __isub__(self, other) -> Self:
        self.x -= other.x
        self.y -= other.y
        return self
    def __mul__(self, scalar) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)
    def __imul__(self, scalar) -> Self:
        self.x *= scalar
        self.y *= scalar
        return self
    def dot_prod(self, other: Vertex2 | Vec2) -> float:
        return self.x * other.x + self.y * other.y
    def cross_prod(self, other) -> float:
        return self.x * other.y - self.y * other.x
    def length(self) -> float:
        return (self.x * self.x + self.y * self.y)**0.5
    