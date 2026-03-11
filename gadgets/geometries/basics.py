from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
from typing import Final

from linear_algebra import *

@dataclass(slots=True)
class Transform:
    mat4: Matrix4dTuple
    
    @classmethod
    def identity(cls) -> Transform:
        return cls((
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ))
    @classmethod
    def translation(cls, x: float, y: float, z: float) -> Transform:
        return cls((
            1.0, 0.0, 0.0, x,
            0.0, 1.0, 0.0, y,
            0.0, 0.0, 1.0, z,
            0.0, 0.0, 0.0, 1.0,
        ))
    @classmethod
    def scaling(cls, x: float, y: float, z: float) -> Transform:
        return cls((
            x, 0.0, 0.0, 0.0,
            0.0, y, 0.0, 0.0,
            0.0, 0.0, z, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ))
    @classmethod
    def rotation_z(cls, radians: float) -> Transform:
        return cls(rot_mat_z(radians))
    @classmethod
    def rotation_y(cls, radians: float) -> Transform:
        return cls(rot_mat_y(radians))
    @classmethod
    def rotation_x(cls, radians: float) -> Transform:
        return cls(rot_mat_x(radians))
    
    def translate(self, x: float, y: float, z: float) -> Transform:
        return Transform(mat4t_mul(self.mat4,
                         Transform.translation(x, y, z).mat4))
    def scale(self, x: float, y: float, z: float) -> Transform:
        return Transform(mat4t_mul(self.mat4,
                         Transform.scaling(x, y, z).mat4))
    def rotate_z(self, radians: float) -> Transform:
        return Transform(mat4t_mul(self.mat4, rot_mat_z(radians)))
    def rotate_y(self, radians: float) -> Transform:
        return Transform(mat4t_mul(self.mat4, rot_mat_y(radians)))
    def rotate_x(self, radians: float) -> Transform:
        return Transform(mat4t_mul(self.mat4, rot_mat_x(radians)))


@dataclass(slots=True, frozen=False)
class Vertex:
    x: float
    y: float
    u: float
    v: float


@dataclass(slots=True, frozen=False)
class Color:
    r: int
    g: int
    b: int
    a: int = 255


@dataclass(slots=True, frozen=False)
class RasterizationTriangle:
    a: Final[Vertex]
    b: Final[Vertex]
    c: Final[Vertex]
    texture: Buffer


@dataclass(slots=True, frozen=True)
class Buffer:
    width: int
    height: int
    data: list[Color]
    
    @classmethod
    def empty(cls, width: int, height: int, 
              r: int = 0, g: int = 0, b: int = 0) -> Buffer:
        return cls(width, height, [Color(r, g, b) 
                                   for _ in range(width * height)])
    
    @classmethod
    def ice(cls, width: int, height: int) -> Buffer:
        data = [Color(0, 0, 0) for _ in range(width * height)]
        cell = width // 16
        for y in range(height):
            for x in range(width):
                c = data[y * width + x]
                xc = x // cell
                yc = y // cell
                if (xc + yc) & 1:
                    c.r = 156
                    c.g = 220
                    c.b = 255
                else:
                    c.r = 255
                    c.g = 255
                    c.b = 255
        return cls(width, height, data)
    
    def fill(self, r: int = 0, g: int = 0, b: int = 0) -> None:
        for c in self.data: c.r, c.g, c.b = r, g, b
                
    
    def to_ansi(self) -> str:
        ansi_builder = "\033[48;2;%d;%d;%dm  \033[0m"
        data = self.data
        width = self.width
        return "\r\n".join(
            "".join(
                ansi_builder % (c.r, c.g, c.b) 
                for c in islice(data, i, i + width)
            )
            for i in range(0, self.height * width, width)
        )
