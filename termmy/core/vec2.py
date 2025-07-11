

from __future__ import annotations

from .type_aliases import NormFloat

from dataclasses import dataclass
from typing import overload
from abc import ABC
from numbers import Number

class _Vec2Mixin(ABC):
    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self
    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)
    def __imul__(self, scalar):
        self.x *= scalar
        self.y *= scalar
        return self
    def dot_prod(self, other):
        return self.x * other.x + self.y * other.y
    def cross_prod(self, other):
        return self.x * other.y - self.y * other.x
    def length(self):
        return (self.x * self.x + self.y * self.y)**0.5
    def __hash__(self):
        return hash((self.x, self.y))

@dataclass(slots=True)
class Vec2i(_Vec2Mixin):
    x: int
    y: int
    def __eq__(self, other):
        return (isinstance(other, Vec2i) 
                and self.x == other.x and self.y == other.y)

@dataclass(slots=True)
class Vec2(_Vec2Mixin):
    x: float
    y: float
    def __eq__(self, other):
        return (isinstance(other, Vec2) 
                and self.x == other.x and self.y == other.y)
@dataclass(slots=True)
class Vec2Rela(_Vec2Mixin):
    x: NormFloat
    y: NormFloat
    def __eq__(self, other):
        return (isinstance(other, Vec2) 
                and self.x == other.x and self.y == other.y)

@dataclass(slots=True)
class UV:
    u: NormFloat
    v: NormFloat
    def __hash__(self):
        return hash((self.u, self.v))
    def __eq__(self, other):
        return (isinstance(other, UV) 
                and self.u == other.u and self.v == other.v)

if __name__ == "__main__":
    d = {Vec2i(1, 2): 0, Vec2i(4, 3): 1}
    print((1, 2) in d)
    print(hash((1, 2)) == hash(Vec2i(1, 2)))
