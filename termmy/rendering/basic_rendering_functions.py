from typing import Callable
from math import ceil

from termmy.colors.color import alpha_blended, Color
from termmy.buffers.framebuffer import hasColorBuffer
from termmy.buffers.color_buffer import ColorBuffer
from termmy.render_objects.triangulatable import Triangulatable
from termmy.render_objects.rasterization import RasterizationTriangle


def render(frame_buffer: hasColorBuffer, render_object: Triangulatable) -> None:
    for triangle in render_object.triangulate():
        rasterize_triangle(frame_buffer.color_buffer, triangle, triangle.texture, pixel_shader)
        # rasterize_pixel_line(triangle.a.x, triangle.a.y, triangle.b.x, triangle.b.y, Color(0.0, 0.0, 0.0), frame_buffer.color_buffer)
        # rasterize_pixel_line(triangle.b.x, triangle.b.y, triangle.c.x, triangle.c.y, Color(0.0, 0.0, 0.0), frame_buffer.color_buffer)
        # rasterize_pixel_line(triangle.c.x, triangle.c.y, triangle.a.x, triangle.a.y, Color(0.0, 0.0, 0.0), frame_buffer.color_buffer)
        
        
def rasterize_triangle(color_buffer: ColorBuffer, 
                       triangle: RasterizationTriangle,
                       texture: ColorBuffer,
                       pixel_shader: Callable) -> None:
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
            color_buffer, texture,
            pixel_shader,
        )
            
    if by != cy:
        # Non flat bottom
        _rasterize_flat_triangle(
            bx, by, bu, bv,
            cx, cy, cu, cv,
            t_ac, mx, du_ac, dv_ac,
            color_buffer, texture,
            pixel_shader,
        )      


def _rasterize_flat_triangle(
    bx: float, by: float, bu: float, bv: float,
    vx: float, vy: float, vu: float, vv: float,
    t_m: float, mx: float, du_m: float, dv_m: float,
    buffer: ColorBuffer, texture: ColorBuffer,
    pixel_shader: Callable,
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
        clrbuf_row_idx = y * buff_w
        
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
            
            for x in range(x_left, x_right):
                u_, v_ = (int(u) % txtr_w, 
                          (int(v) % txtr_h_ if txtr_h_ > 0 else 0))
                
                pixel_shader(x, clrbuf_row_idx, buff, u_, v_, txtr_w, txtr)

                # print(buffer.ansi_24(), end="")
                # print(buffer.rollback_str(), end="")
                
                u, v = u + du_row, v + dv_row
                
        
        # Increament UV for the next row
        u_left, v_left = u_left + du_left, v_left + dv_left
        u_right, v_right = u_right + du_right, v_right + dv_right
        
        
def pixel_shader(x: int, clrbuf_row_idx: int, clrbuf_data: tuple[Color],
                 u: float, v: float, 
                 txtr_width: int, txtr_data: tuple[Color]) -> None:
    c_old, c_new = (clrbuf_data[clrbuf_row_idx + x], 
                    txtr_data[int(v) * txtr_width + int(u)])
    c_old.r, c_old.g, c_old.b = alpha_blended(c_new, c_old)


def rasterize_pixel_line(
    x1: float, y1: float, x2: float, y2: float,
    color: Color, buffer: ColorBuffer,
) -> None:
    
    # TODO This is inefficient for lines with a large portion 
    # outside the buffer
    
    x_diff = x1 - x2
    y_diff = y1 - y2
    
    if abs(x_diff) > abs(y_diff):
        k = y_diff / x_diff
        b = y1 - k * x1
        if x1 > x2:
            x1, y1, x2, y2 = x2, y2, x1, y1
            
        for x in range(int(x1), int(x2)):
            y = int(k * x + b)
            rasterize_pixel_point(x, y, color, buffer)
    else:
        t = x_diff / y_diff
        b = x1 - t * y1
        if y1 > y2:
            x1, y1, x2, y2 = x2, y2, x1, y1
            
        for y in range(int(y1), int(y2)):
            x = int(t * y + b)
            rasterize_pixel_point(x, y, color, buffer)


def rasterize_pixel_point(
    x: float, y: float, color: Color, buffer: ColorBuffer,
) -> None:
    x, y = int(x), int(y)
    if 0 <= x < buffer.width and 0 <= y < buffer.height:
        c = buffer.data[y * buffer.width + x]
        c.r, c.g, c.b = alpha_blended(color, c)
