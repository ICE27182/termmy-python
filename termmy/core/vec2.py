

from dataclasses import dataclass
from .type_aliases import AbsoFloat, NormFloat

@dataclass(slots=True)
class Vec2i:
    x: int
    y: int
    def __hash__(self):
        return hash((self.x, self.y))
    def __eq__(self, other):
        return (isinstance(other, Vec2i) 
                and self.x == other.x and self.y == other.y)

@dataclass(slots=True)
class Vec2:
    x: float
    y: float
    def __hash__(self):
        return hash((self.x, self.y))
    def __eq__(self, other):
        return (isinstance(other, Vec2) 
                and self.x == other.x and self.y == other.y)
@dataclass(slots=True)
class Vec2Rela:
    x: NormFloat
    y: NormFloat
    def __hash__(self):
        return hash((self.x, self.y))
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
