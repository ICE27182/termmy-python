

from __future__ import annotations
from dataclasses import dataclass
from typing import Self, Callable

@dataclass(slots=True)
class Color:
    r:float = 0.0
    g:float = 0.0
    b:float = 0.0
    a:float = 1.0
    
    @classmethod
    def from_ints(cls, r: int, g: int, b: int, a: int = 255) -> Color:
        return cls(r/255, g/255, b/255, a/255)
    
    @classmethod
    def from_hex(cls, hex: str) -> Color:
        if len(hex) == 0:
            raise ValueError(f"Invalid hex color. Got {hex=}")
        if hex[0] == "#":
            hex = hex[1:]
        if len(hex) in (3, 4):
            hex = "".join("%sF" % h for h in hex)
        elif len(hex) not in (6, 8):
            raise ValueError(f"Invalid hex color. Got {hex=}")
        return cls.from_ints(int(hex[0:2], base=16),
                                 int(hex[2:4], base=16),
                                 int(hex[4:6], base=16),
                                 int(hex[6:8], base=16) if len(hex) == 8 
                                 else 255)
    
    @classmethod
    def from_illuminance(cls, illum: float, alpha: float = 1.0) -> Color:
        return cls(illum, illum, illum, alpha)
    
    @classmethod
    def blended(cls, original: Self, over: Self)  -> Color:
        a = over.a
        a_ = 1.0 - a
        return cls(
            original.r*a_ + over.r*a,
            original.g*a_ + over.g*a,
            original.b*a_ + over.b*a,
            a,
        )
    
    def blend_over(self, over: Self)  -> Self:
        a = over.a
        a_ = 1.0 - a
        self.r = self.r*a_ + over.r*a
        self.g = self.g*a_ + over.g*a
        self.b = self.b*a_ + over.b*a
        self.a = a
        return self
    
    def illuminance(self) -> float:
        return self.r*0.299 + self.g*0.587 + self.b*0.114
    
    def to24bit(self) -> tuple[int, int, int]:
        """
        Return a tuple of 3 integers in [0, 255] with clamping, in the order
        of red, green and blue.

        If the value of a channel is less than 0, the value will be returned
        as 0.

        If the value of a channel is larger than 1, the value will be returned
        as 255.
        """
        return (
            (round(self.r*255.0) if self.r >= 0.0 else 0)
            if self.r <= 1.0 else 255,
            (round(self.g*255.0) if self.g >= 0.0 else 0)
            if self.g <= 1.0 else 255,
            (round(self.b*255.0) if self.b >= 0.0 else 0)
            if self.b <= 1.0 else 255,
        )
    
    def to32bit(self) -> tuple[int, int, int, int]:
        """
        Return a tuple of 4 integers in [0, 255] with clamping, in the order
         of red, green, blue and alpha.

        If the value of a channel is less than 0, the value will be returned
        as 0.
        
        If the value of a channel is larger than 1, the value will be returned
        as 255.
        """
        return (
            (round(self.r*255.0) if self.r >= 0.0 else 0)
            if self.r <= 1.0 else 255,
            (round(self.g*255.0) if self.g >= 0.0 else 0)
            if self.g <= 1.0 else 255,
            (round(self.b*255.0) if self.b >= 0.0 else 0)
            if self.b <= 1.0 else 255,
            (round(self.a*255.0) if self.a >= 0.0 else 0)
            if self.a <= 1.0 else 255,
        )
    
    def to_ansi_txt_24(self) -> str:
        r, g, b = self.to24bit()
        return f"\033[38;2;{r};{g};{b}m"
    
    def to_ansi_bgd_24(self) -> str:
        r, g, b = self.to24bit()
        return f"\033[48;2;{r};{g};{b}m"
    
    def to_ansi_txt_color_lookup(self, lookup: bytes | bytearray) -> str:
        r, g, b = self.to24bit()
        return f"\033[38;5;{lookup[(r<<16) + (g<<8) + b]}m"
    
    def to_ansi_bgd_color_lookup(self, lookup: bytes | bytearray) -> str:
        r, g, b = self.to24bit()
        return f"\033[48;5;{lookup[(r<<16) + (g<<8) + b]}m"
    
    def to_ascii(self, lookup: str) -> str:
        return lookup[int(len(lookup) * self.illuminance())]
    
    def map(self, func: Callable[[float], float]) -> Color:
        self.r = func(self.r)
        self.g = func(self.g)
        self.b = func(self.b)
        return self
    
