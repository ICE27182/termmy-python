from __future__ import annotations

from dataclasses import dataclass, field
from itertools import islice
from typing import Final, Iterable, Protocol
from time import sleep
from math import ceil

from linear_algebra import *

@dataclass(slots=True, frozen=False)
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
    
    @classmethod
    def zero(cls) -> Vertex:
        return cls(0.0, 0.0, 0.0, 0.0)
    
    def __repr__(self) -> str:
        return "Vertex(x=%.3f, y=%.3f, u=%.3f, v=%.3f)" % (
            self.x, self.y, self.u, self.v
        )


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
    width: Final[int]
    height: Final[int]
    data: list[Color]
    roll_back_str: Final[str] = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "roll_back_str", "\033[%dA" % self.height)
    
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
    
    def fill(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255) -> None:
        for c in self.data: c.r, c.g, c.b, c.a = r, g, b, a
                
    
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
    
    def show(self) -> None:
        print(self.roll_back_str, self.to_ansi(), sep='\033[A', end='\n')
        


class Triangulatable(Protocol):
    def triangulate(self) -> list[RasterizationTriangle]: ...        

pixel_by_pixel = False
triangle_by_triangle = False

def render(geometries: Iterable[Triangulatable], buffer: Buffer) -> None:
    # rasterize_line(47.5, 0, 47.5, 60, Color(0,0,0,0xff), buffer)
    # for geom in geometries:
    #     for tri in geom.triangulate():
    #         rasterize_line(tri.a.x, tri.a.y, tri.b.x, tri.b.y, Color(127, 127, 127, 0x80), buffer)
    #         rasterize_line(tri.b.x, tri.b.y, tri.c.x, tri.c.y, Color(127, 127, 127, 0x80), buffer)
    #         rasterize_line(tri.c.x, tri.c.y, tri.a.x, tri.a.y, Color(127, 127, 127, 0x80), buffer)
    # for geom in geometries:
    #     for tri in geom.triangulate():
    #         rasterize_point(tri.a.x, tri.a.y, Color(0, 255, 0, 0x80), buffer)
    #         rasterize_point(tri.b.x, tri.b.y, Color(0, 255, 0, 0x80), buffer)
    #         rasterize_point(tri.c.x, tri.c.y, Color(0, 255, 0, 0x80), buffer)
    for geom in geometries:
        for i, tri in enumerate(geom.triangulate()):
            c = (255, 0, 0, 0x80) if i & 1 else (0, 0, 0, 0x80)
            tri.texture.fill(*c)
            
            rasterize_point(tri.a.x, tri.a.y, Color(0, 255, 0, 0x80), buffer)
            rasterize_point(tri.b.x, tri.b.y, Color(0, 255, 0, 0x80), buffer)
            rasterize_point(tri.c.x, tri.c.y, Color(0, 255, 0, 0x80), buffer)
            
            # global pixel_by_pixel
            # pixel_by_pixel = i == 3
            rasterize_triangle(tri, tri.texture, buffer)
            
            if triangle_by_triangle:
                buffer.show()
                print('\n', tri.a, tri.b, tri.c, end='\r\033[A')
                # input()


def rasterize_triangle(
    triangle: RasterizationTriangle, 
    texture: Buffer, 
    buffer: Buffer,
) -> None:
    # Localize data
    txtr_w, txtr_h = texture.width, texture.height - 1
    a, b, c = triangle.a, triangle.b, triangle.c
    
    # Sorting by y such that a.y <= b.y <= c.y
    if a.y > b.y: a, b = b, a
    if b.y > c.y: b, c = c, b
    if a.y > b.y: a, b = b, a
    
    # Localize data
    ax, ay = a.x, a.y
    bx, by = b.x, b.y
    cx, cy = c.x, c.y
    au, av = a.u * txtr_w, a.v * txtr_h
    bu, bv = b.u * txtr_w, b.v * txtr_h
    cu, cv = c.u * txtr_w, c.v * txtr_h
    
    if ay == cy: return # The triangle is a line
    
    # Edge AC
    t_ac = (ax - cx) / (ay - cy)
    du_ac, dv_ac = (au - cu) / (ay - cy), (av - cv) / (ay - cy) # ay-cy!=0
    
    # Middle point
    mx = int(t_ac * (by - cy) + cx)
    
    if ay != by:
        # Non flat top
        _rasterize_flat_triangle(
            bx, by, bu, bv,
            ax, ay, au, av,
            t_ac, mx, du_ac, dv_ac,
            buffer, texture,
        )
            
    if by != cy:
        # Non flat bottom
        _rasterize_flat_triangle(
            bx, by, bu, bv,
            cx, cy, cu, cv,
            t_ac, mx, du_ac, dv_ac,
            buffer, texture,
        )      


def _rasterize_flat_triangle(
    bx: float, by: float, bu: float, bv: float,
    vx: float, vy: float, vu: float, vv: float,
    t_m: float, mx: float, du_m: float, dv_m: float,
    buffer: Buffer, texture: Buffer,
):
    txtr_w, txtr_h_ = texture.width, texture.height - 1
    buff_w, buff_h = buffer.width, buffer.height
    txtr, buff = texture.data, buffer.data
    
    # Edge BV
    t_bv = (vx - bx) / (vy - by)
    du_bv, dv_bv = (vu - bu) / (vy - by), (vv - bv) / (vy - by)
    
    # Assign left & right edges
    if bx <= mx:
        t_left, t_right, du_left = t_bv, t_m, du_bv
        dv_left, du_right, dv_right = dv_bv, du_m, dv_m
    else:
        t_left, t_right, du_left = t_m, t_bv, du_m
        dv_left, du_right, dv_right = dv_m, du_bv, dv_bv
    
    # Y range
    if vy > by: y_start, y_end = ceil(by), ceil(vy)
    else: y_start, y_end = ceil(vy), ceil(by)
    
    if y_start < 0: y_start = 0
    if y_end > buff_h: y_end = buff_h
    
    # UV for left and right edges
    u_left = (y_start - vy) * du_left + vu
    v_left = (y_start - vy) * dv_left + vv
    u_right = (y_start - vy) * du_right + vu
    v_right = (y_start - vy) * dv_right + vv
    
    for y in range(y_start, y_end):
        buf_row_idx = y * buff_w
        
        # X range
        x_left = int(t_left * (y - vy) + vx)
        x_right = int(t_right * (y - vy) + vx)
        if x_left < 0: x_left = 0
        if x_right > buff_w: x_right = buff_w
        
        x_diff = x_right - x_left
        if x_diff != 0:
            # This does not result in an unbound error because
            # if x_right == x_left, then the loop will not be entered
            du_row = (u_right - u_left) / x_diff
            dv_row = (v_right - v_left) / x_diff
            u, v = u_left, v_left
        else: du_row = dv_row = u = v = 0.0 # Will never be used
                
        # Middle pixels
        for x in range(x_left, x_right):
            u_, v_ = int(u) % txtr_w, (int(v) % txtr_h_ if txtr_h_ > 0 else 0)
            c_old, c_new = buff[buf_row_idx + x], txtr[v_ * txtr_w + u_]
            c_old.r, c_old.g, c_old.b = alpha_blended(c_new, c_old)
            
            if pixel_by_pixel:
                buffer.show()
                sleep(0.02)
            
            u, v = u + du_row, v + dv_row
        
        # Increament UV for the next row
        u_left, v_left = u_left + du_left, v_left + dv_left
        u_right, v_right = u_right + du_right, v_right + dv_right


def rasterize_line(
    x1: float, y1: float, x2: float, y2: float,
    color: Color, buffer: Buffer,
) -> None:
    x_diff = x1 - x2
    y_diff = y1 - y2
    if abs(x_diff) > abs(y_diff):
        k = y_diff / x_diff
        b = y1 - k * x1
        if x1 > x2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        for x in range(int(x1), int(x2)):
            y = int(k * x + b)
            rasterize_point(x, y, color, buffer)
    else:
        t = x_diff / y_diff
        b = x1 - t * y1
        if y1 > y2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        for y in range(int(y1), int(y2)):
            x = int(t * y + b)
            rasterize_point(x, y, color, buffer)

def rasterize_point(
    x: float, y: float, color: Color, buffer: Buffer,
) -> None:
    x, y = int(x), int(y)
    if 0 <= x < buffer.width and 0 <= y < buffer.height:
        c = buffer.data[y * buffer.width + x]
        c.r, c.g, c.b = alpha_blended(color, c)

def alpha_blended(
    new: Color, old: Color,
) -> tuple[int, int, int]:
    a = new.a / 255.0
    a_ = 1 - a
    r = int(new.r * a + old.r * a_)
    g = int(new.g * a + old.g * a_)
    b = int(new.b * a + old.b * a_)
    return r, g, b
