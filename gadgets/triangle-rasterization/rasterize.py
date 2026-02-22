from data_structures import *

from enum import StrEnum, auto
from dataclasses import dataclass

class TranslucencySettings(StrEnum):
    OPAQUE = auto()
    TRANSPARENT = auto()
    TRANSLUCENT = auto()

class AntialiasingSettings(StrEnum):
    NONE = auto()
    MSAA = auto()
    AAA = auto()

@dataclass(slots=True)
class RasterizationSettings:
    translucency: TranslucencySettings
    antialiasing: AntialiasingSettings
    
def rasterize_triangle_with_func(
    triangle: Triangle, 
    texture: Buffer, 
    buffer: Buffer | MSAABuffer, 
    settings: RasterizationSettings
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
        rasterize_flat_triangle(
            bx, by, bu, bv,
            ax, ay, au, av,
            t_ac, mx, du_ac, dv_ac,
            buffer, texture, settings,
        )
            
    if by != cy:
        # Non flat bottom
        rasterize_flat_triangle(
            bx, by, bu, bv,
            cx, cy, cu, cv,
            t_ac, mx, du_ac, dv_ac,
            buffer, texture, settings,
        )      


def rasterize_flat_triangle(
    bx: float, by: float, bu: float, bv: float,
    vx: float, vy: float, vu: float, vv: float,
    t_m: float, mx: float, du_m: float, dv_m: float,
    buffer: Buffer | MSAABuffer, texture: Buffer,
    settings: RasterizationSettings
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
    y_start, y_end = int(vy), int(by)
    if y_start > y_end: y_start, y_end = y_end, y_start
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
        x_right = int(t_right * (y - vy) + vx) + 1
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
        
        for x in range(x_left, x_right):
            u_, v_ = int(u), int(v)
            if u_ < 0: u_ = 0
            elif u_ >= txtr_w: u_ = txtr_w - 1
            if v_ < 0: v_ = 0
            elif v_ > txtr_h_: v_ = txtr_h_
            
            c_end, c_src = buff[buf_row_idx + x], txtr[v_ * txtr_w + u_]
            c_end.r, c_end.g, c_end.b = c_src.r, c_src.g, c_src.b
            
            u, v = u + du_row, v + dv_row
        
        # Increament UV for the next row
        u_left, v_left = u_left + du_left, v_left + dv_left
        u_right, v_right = u_right + du_right, v_right + dv_right
