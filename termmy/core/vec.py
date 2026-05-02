from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from abc import ABC
from numbers import Number

from .type_aliases import NormFloat


class Vec2(Protocol):
    x: Number
    y: Number

@dataclass(slots=True)
class Vec2i:
    x: int
    y: int

@dataclass(slots=True)
class Vec2f:
    x: float
    y: float
    
@dataclass(slots=True)
class Vec2fNorm:
    x: NormFloat
    y: NormFloat

@dataclass(slots=True)
class UV:
    u: NormFloat
    v: NormFloat



class Vec3(Protocol):
    x: Number
    y: Number
    z: Number
    

@dataclass(slots=True)
class Vec3f:
    x: float
    y: float
    z: float
    
    @classmethod
    def zero(cls) -> Vec3f: return cls(0.0, 0.0, 0.0)
    
    @classmethod
    def one(cls) -> Vec3f: return cls(1.0, 1.0, 1.0)


@dataclass(slots=True)
class Vec3fNorm:
    x: NormFloat
    y: NormFloat
    z: NormFloat
    
    @classmethod
    def zero(cls) -> Vec3fNorm: return cls(0.0, 0.0, 0.0)

    @classmethod
    def one(cls) -> Vec3fNorm: return cls(1.0, 1.0, 1.0)
