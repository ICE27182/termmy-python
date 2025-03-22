

from dataclasses import dataclass
@dataclass(slots=True)
class Vec2i:
    x:int
    y:int
    def __hash__(self):
        return hash((self.x, self.y))
    def __eq__(self, other):
        return (isinstance(other, Vec2i) 
                and self.x == other.x and self.y == other.y)

@dataclass(slots=True)
class UV:
    u:float
    v:float
