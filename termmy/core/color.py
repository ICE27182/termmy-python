
from __future__ import annotations
from dataclasses import dataclass
from typing import Self

@dataclass(slots=True)
class Color:
    r:int
    g:int
    b:int
    a:int = 255
    
    @classmethod
    def from_bytes(cls, bytes: bytes|bytearray) -> Color:
        return cls(*bytes)

    def to_bytes_32(self) -> bytes:
        return bytes((self.r, self.g, self.b, self.a))
    def to_bytesarray_32(self) -> bytearray:
        return bytearray((self.r, self.g, self.b, self.a))
    def to_bytes_24(self) -> bytes:
        return bytes((self.r, self.g, self.b))
    def to_bytesarray_24(self) -> bytearray:
        return bytearray((self.r, self.g, self.b))
    
    def to_ansi_txt_24(self) -> str:
        return f"\033[38;2;{self.r};{self.g};{self.b}m"
    
    def to_ansi_bgd_24(self) -> str:
        return f"\033[48;2;{self.r};{self.g};{self.b}m"
    
    def __add__(self, other: Self) -> Self:
        a = other.a / 255
        a_ = 1 - a
        return Color(
            int(self.r*a_ + other.r*a),
            int(self.g*a_ + other.g*a),
            int(self.b*a_ + other.b*a),
            255
        )
    def __iadd__(self, other: Self) -> Self:
        a = other.a / 255
        a_ = 1 - a
        self.r = int(self.r*a_ + other.r*a),
        self.g = int(self.g*a_ + other.g*a),
        self.b = int(self.b*a_ + other.b*a),
        self.a = 255
        return self
    
    
