raise NotImplementedError(
    "How the program treats the uv wrapping is flawed.\n"
    "Currently `rasterize_triangle` and `rasterize_triangle_with_loop` "
    "use the bitwise AND for the wrapping, which does not work properly "
    "when the texture size is not a power of 2.\n"
    "And `rasterize_triangle_with_func` uses the modulo operator, "
    "which works but is slower than the other two functions\n"
)
"""
If you inline everything, you get at most 1.3% faster, but then the code gets worse

I dont think it's worth it

Use 2 function calls instead.

In the test case where we render 1000 triangles for 500 times, it can rasterize 26k+ triangles per second

3 runs of the test with 1000 triangles and 100 iterations each. 
Average time in seconds per triangle:
# Run 1
3.682624500004749e-05
3.7306149170035494e-05
3.7308583749982064e-05
# Run 2
3.7269405420011024e-05
3.751992541001527e-05
3.742800833002548e-05
# Run 3
3.7312989589991045e-05
3.7421235000001615e-05
3.740109792001022e-05
"""

from timeit import repeat, timeit
from random import random, uniform, seed, randint

from data_structures import *
        
def rasterize_triangle(triangle: Triangle, texture: Buffer, buffer: Buffer) -> None:
    # Localize data
    txtr_w, txtr_h = texture.width, texture.height - 1
    u_mask, v_mask = txtr_w - 1, txtr_h - 1
    buff_w, buff_h = buffer.width, buffer.height
    txtr, buff = texture.data, buffer.data
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
        
        # Edge AB
        t_ab = (ax - bx) / (ay - by)
        du_ab, dv_ab = (au - bu) / (ay - by), (av - bv) / (ay - by) # ay-by!=0
        
        # Assign left & right edges
        if bx <= mx:
            t_left, t_right, du_left = t_ab, t_ac, du_ab
            dv_left, du_right, dv_right = dv_ab, du_ac, dv_ac
        else:
            t_left, t_right, du_left = t_ac, t_ab, du_ac
            dv_left, du_right, dv_right = dv_ac, du_ab, dv_ab
        
        # Y range
        y_start, y_end = int(ay), int(by)
        if y_start < 0: y_start = 0
        if y_end > buff_h: y_end = buff_h
        
        # UV for left and right edges
        u_left = (y_start - ay) * du_left + au
        v_left = (y_start - ay) * dv_left + av
        u_right = (y_start - ay) * du_right + au
        v_right = (y_start - ay) * dv_right + av
        
        for y in range(y_start, y_end):
            buf_row_idx = y * buff_w
            
            # X range
            x_left = int(t_left * (y - ay) + ax)
            x_right = int(t_right * (y - ay) + ax) + 1
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
                u_, v_ = int(u) & u_mask, int(v) & v_mask
                c_end, c_src = buff[buf_row_idx + x], txtr[v_ * txtr_w + u_]
                c_end.r, c_end.g, c_end.b = c_src.r, c_src.g, c_src.b
                u, v = u + du_row, v + dv_row
            
            # Increament UV for the next row
            u_left, v_left = u_left + du_left, v_left + dv_left
            u_right, v_right = u_right + du_right, v_right + dv_right
            
    if by != cy:
        # Non flat bottom
        
        # Edge BC
        t_bc = (bx - cx) / (by - cy)
        du_bc, dv_bc = (bu - cu) / (by - cy), (bv - cv) / (by - cy) # by-cy!=0
        
        # Assign left & right edges
        if mx <= bx:
            t_left, t_right, du_left = t_ac, t_bc, du_ac
            dv_left, du_right, dv_right = dv_ac, du_bc, dv_bc
        else:
            t_left, t_right, du_left = t_bc, t_ac, du_bc
            dv_left, du_right, dv_right = dv_bc, du_ac, dv_ac
        
        # Y range
        y_start, y_end = int(by), int(cy)
        if y_start < 0: y_start = 0
        if y_end > buff_h: y_end = buff_h
        
        # UV for left and right edges
        u_left = (y_start - cy) * du_left + cu
        v_left = (y_start - cy) * dv_left + cv
        u_right = (y_start - cy) * du_right + cu
        v_right = (y_start - cy) * dv_right + cv
        
        for y in range(y_start, y_end):
            buf_row_idx = y * buff_w
            
            # X range
            x_left = int(t_left * (y - cy) + cx)
            x_right = int(t_right * (y - cy) + cx) + 1
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
                u_, v_ = int(u) & u_mask, int(v) & v_mask
                c_end, c_src = buff[buf_row_idx + x], txtr[v_ * txtr_w + u_]
                c_end.r, c_end.g, c_end.b = c_src.r, c_src.g, c_src.b
                u, v = u + du_row, v + dv_row
                
            # Increament UV for the next row
            u_left, v_left = u_left + du_left, v_left + dv_left
            u_right, v_right = u_right + du_right, v_right + dv_right       


def rasterize_flat_triangle(
    bx: float, by: float, bu: float, bv: float,
    vx: float, vy: float, vu: float, vv: float,
    t_m: float, mx: float, du_m: float, dv_m: float,
    buff: list[Color], buff_w: int, buff_h: int,
    txtr: list[Color], txtr_w: int, txtr_h: int,
    u_mask: int, v_mask: int
):
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
            u_, v_ = int(u) & u_mask, int(v) & v_mask
            c_end, c_src = buff[buf_row_idx + x], txtr[v_ * txtr_w + u_]
            c_end.r, c_end.g, c_end.b = c_src.r, c_src.g, c_src.b
            u, v = u + du_row, v + dv_row
        
        # Increament UV for the next row
        u_left, v_left = u_left + du_left, v_left + dv_left
        u_right, v_right = u_right + du_right, v_right + dv_right
    

def rasterize_triangle_with_func(triangle: Triangle, texture: Buffer, buffer: Buffer) -> None:
    # Localize data
    txtr_w, txtr_h = texture.width, texture.height - 1
    u_mask, v_mask = txtr_w - 1, txtr_h - 1
    buff_w, buff_h = buffer.width, buffer.height
    txtr, buff = texture.data, buffer.data
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
            buff, buff_w, buff_h,
            txtr, txtr_w, txtr_h,
            u_mask, v_mask,
        )
            
    if by != cy:
        # Non flat bottom
        rasterize_flat_triangle(
            bx, by, bu, bv,
            cx, cy, cu, cv,
            t_ac, mx, du_ac, dv_ac,
            buff, buff_w, buff_h,
            txtr, txtr_w, txtr_h,
            u_mask, v_mask,
        )      


def rasterize_triangle_with_loop(triangle: Triangle, texture: Buffer, buffer: Buffer) -> None:
    # Localize data
    txtr_w, txtr_h = texture.width, texture.height - 1
    u_mask, v_mask = txtr_w - 1, txtr_h - 1
    buff_w, buff_h = buffer.width, buffer.height
    txtr, buff = texture.data, buffer.data
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
    
    for i in (1, 0):
        if i:
            if ay == by: continue
            # Non flat top
            vx, vy = ax, ay,
            vu, vv = au, av
        else:
            if by == cy: continue
            # Non flat bottom
            vx, vy = cx, cy,
            vu, vv = cu, cv
            
        # Edge BV
        t_bv = (vx - bx) / (vy - by)
        du_bv, dv_bv = (vu - bu) / (vy - by), (vv - bv) / (vy - by)
        # Assign left & right edges
        if bx <= mx:
            t_left, t_right, du_left = t_bv, t_ac, du_bv
            dv_left, du_right, dv_right = dv_bv, du_ac, dv_ac
        else:
            t_left, t_right, du_left = t_ac, t_bv, du_ac
            dv_left, du_right, dv_right = dv_ac, du_bv, dv_bv
        
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
                u_, v_ = int(u) & u_mask, int(v) & v_mask
                c_end, c_src = buff[buf_row_idx + x], txtr[v_ * txtr_w + u_]
                c_end.r, c_end.g, c_end.b = c_src.r, c_src.g, c_src.b
                u, v = u + du_row, v + dv_row
            
            # Increament UV for the next row
            u_left, v_left = u_left + du_left, v_left + dv_left
            u_right, v_right = u_right + du_right, v_right + dv_right

txtr = Buffer.ice(80, 24)
frame = Buffer.empty(80, 24, 30, 30, 30)

triangle = Triangle(
    Vertex(10, 5, 10/80, 5/24), 
    Vertex(50, 15, 50/80, 15/24), 
    Vertex(30, 25, 30/80, 25/24),
)

def get_triangles(w: int, h: int, n: int, sd: int = 0) -> list[Triangle]:
    seed(sd)
    return [Triangle(
        Vertex(uniform(-0.2, 1.2) * w, uniform(-0.2, 1.2) * h, random(), random()), 
        Vertex(uniform(-0.2, 1.2) * w, uniform(-0.2, 1.2) * h, random(), random()), 
        Vertex(uniform(-0.2, 1.2) * w, uniform(-0.2, 1.2) * h, random(), random()),
    ) for _ in range(n)]

if 0:
    N = 100
    M = 1000
    def benchmark(rasterize_triangle, n, m):
        seed(0)
        triangles = get_triangles(80, 24, m)
        def callback():
            for t in triangles:
                rasterize_triangle(t, txtr, frame)
        result = min(repeat(callback, number=n))
        print(
            result / n / m
        )
            
    benchmark(rasterize_triangle, N, M)

    benchmark(rasterize_triangle_with_func, N, M)
    
    benchmark(rasterize_triangle_with_loop, N, M)
elif 1:
    M = 1000
    N = 500
    seed(0)
    triangles = get_triangles(80, 24, M)
    def callback():
        for t in triangles:
            rasterize_triangle_with_func(t, txtr, frame)
    result = timeit(callback, number=N)
    print(
        result / N / M
    )

if 0:
    rasterize_triangle(
    triangle=triangle,
    texture=txtr,
    buffer=frame
)
elif 0:
    rasterize_triangle_with_func(
        triangle=triangle,
        texture=txtr,
        buffer=frame
    )
elif 0:
    rasterize_triangle_with_loop(
        triangle=triangle,
        texture=txtr,
        buffer=frame
    )
    
if 0:
    frame.fill(30, 30, 30)
    N = 10
    triangles = get_triangles(80, 24, N, 1)
    seed(0)
    for t in triangles:
        txtr.fill(randint(0, 255), randint(0, 255), randint(0, 255))
        rasterize_triangle_with_func(
            triangle=t,
            texture=txtr,
            buffer=frame,
        )
        print(frame.to_ansi())
        print(f"{t.a.x:.1f} {t.a.y:.1f}\n{t.b.x:.1f} {t.b.y:.1f}\n{t.c.x:.1f} {t.c.y:.1f}")
        input()
else:
    print(frame.to_ansi())
