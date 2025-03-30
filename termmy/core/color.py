
from __future__ import annotations
from dataclasses import dataclass
from typing import Self

@dataclass(slots=True)
class Color:
    r:float = 0.0
    g:float = 0.0
    b:float = 0.0
    a:float = 1.0
    
    @classmethod
    def from_ints(cls, r: int, g: int, b: int, a: int = 255) -> Color:
        return cls(r/255, g/255, b/255, a/255)
    
    def to_ansi_txt_24(self) -> str:
        r = round(self.r*255.0) if self.r >= 0 else 0 if self.r <= 1 else 255
        g = round(self.g*255.0) if self.g >= 0 else 0 if self.g <= 1 else 255
        b = round(self.b*255.0) if self.b >= 0 else 0 if self.b <= 1 else 255
        return f"\033[38;2;{r};{g};{b}m"
    
    def to_ansi_bgd_24(self) -> str:
        r = round(self.r*255.0) if self.r >= 0 else 0 if self.r <= 1 else 255
        g = round(self.g*255.0) if self.g >= 0 else 0 if self.g <= 1 else 255
        b = round(self.b*255.0) if self.b >= 0 else 0 if self.b <= 1 else 255
        return f"\033[48;2;{r};{g};{b}m"
    
    def __add__(self, other: Self) -> Self:
        a = other.a
        a_ = 1.0 - a
        return Color(
            self.r*a_ + other.r*a,
            self.g*a_ + other.g*a,
            self.b*a_ + other.b*a,
            1.0
        )
    def __iadd__(self, other: Self) -> Self:
        a = other.a
        a_ = 1.0 - a
        self.r = self.r*a_ + other.r*a
        self.g = self.g*a_ + other.g*a
        self.b = self.b*a_ + other.b*a
        self.a = 1.0
        return self
