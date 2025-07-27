

from __future__ import annotations

from .render_context import RenderContext
from .anti_aliasing import MSAA, AAA, SSAA
from ..core import NormFloat, Vec2, Vertex2
from ..colors import Color
from ..graphics import Scene, Node, Fill
from ..graphics import Dot, SimpleLine, Circle
from ..graphics import Triangle, Rectangle, Line

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from math import ceil, floor
if TYPE_CHECKING:
    from .renderer import Renderer

# Used internally. Supposed to be read-only
_VEC2_0_0 = Vec2(0.0, 0.0)

class Rasterizer(ABC):
    @abstractmethod
    def __call__(self, 
                 renderer: Renderer,
                 node: Node,
                 render_context: RenderContext,
                 scene: Scene | None = None) -> None: ...

def rasterize_node(renderer: Renderer,
                   node: Node,
                   render_context: RenderContext,
                   scene: Scene | None = None):
    """Rasterize a node.
    This function has no effect as nodes are only used for grouping nodes.
    """
    pass

def rasterize_dot(renderer: Renderer,
                  dot: Dot,
                  render_context: RenderContext,
                  scene: Scene | None = None) -> None:
    """Rasterize a dot.
    """
    if dot.fill:
        # Localize variables & AA
        aa = renderer.anti_aliasing
        use_aaa = isinstance(aa, AAA)
        use_msaa = isinstance(aa, MSAA)
        use_ssaa = isinstance(aa, SSAA)
        if use_ssaa:
            width = render_context.ss_buffer.width
            height = render_context.ss_buffer.height
            data = render_context.ss_buffer.data
        else:
            width = render_context.width
            height = render_context.height
            data = (render_context.ms_buffer.data if use_msaa
                    else render_context.color_buffer.data)
        # Transformation to screen coordinates
        vec = dot.transform.apply(_VEC2_0_0)
        screen_x = vec.x * render_context._abso_coord_scalar
        screen_y = vec.y * render_context._abso_coord_scalar
        # Rasterization
        if 0.0 <= screen_x < width and 0.0 <= screen_y < height:
            fill_color = dot.fill.color
            if use_msaa:
                level = aa._level
                sample_num = 1 << level
                threshold = 1 / level
                samples = (-threshold <= dx+dy < threshold 
                           for (dx, dy) in aa.pattern)
                start = (int(screen_y) * width + int(screen_x)) << level
                for i, sampled in enumerate(samples, start):
                    if sampled:
                        old_color = data[i]
                        old_color.r = fill_color.r
                        old_color.g = fill_color.g
                        old_color.b = fill_color.b
                        old_color.a = fill_color.a
            elif use_aaa:
                level = aa._level
                sample_num = 1 << level
                alpha = 1 / sample_num
                alpha_ = 1 - alpha
                old_color = data[int(screen_y) * width + int(screen_x)]
                old_color.r = fill_color.r * alpha + old_color.r * alpha_
                old_color.g = fill_color.g * alpha + old_color.g * alpha_
                old_color.b = fill_color.b * alpha + old_color.b * alpha_
                old_color.a = fill_color.a * alpha + old_color.a * alpha_
            else:
                old_color = data[int(screen_y) * width + int(screen_x)]
                old_color.r = fill_color.r
                old_color.g = fill_color.g
                old_color.b = fill_color.b
                old_color.a = fill_color.a

def rasterize_simple_line(renderer: Renderer,
                          line: SimpleLine,
                          render_context: RenderContext,
                          scene: Scene | None = None) -> None:
    fill = line.fill
    if fill:
        # Localize variables & AA
        aa = renderer.anti_aliasing
        use_ssaa = isinstance(aa, SSAA)
        use_msaa = isinstance(aa, MSAA)
        use_aaa = isinstance(aa, AAA)
        if use_ssaa:
            width = render_context.ss_buffer.width
            height = render_context.ss_buffer.height
            data = render_context.ss_buffer.data
        else:
            width = render_context.width
            height = render_context.height
            data = (render_context.ms_buffer.data if use_msaa 
                    else render_context.color_buffer.data)
        transform = line.transform
        coord_scalar = render_context._abso_coord_scalar
        # Transformation to screen coordinates
        screen_start = transform.apply(line.start)
        screen_end = transform.apply(line.end)
        screen_start *= coord_scalar
        screen_end *= coord_scalar
        # Normalized direction vec
        dir: Vec2 = screen_end - screen_start
        if 0.0 == dir.x == dir.y:
            return
        dir *= (dir.x*dir.x + dir.y*dir.y)**-0.5
        # AA settings
        if use_aaa or use_msaa:
            level = aa._level
            threshold = 1 / level
            norm = Vec2(dir.y, -dir.x)
            norm *= 1 / norm.length()
            samples = tuple(-threshold <= dx*norm.x + dy*norm.y < threshold 
                            for (dx, dy) in aa.pattern)
        if use_aaa:
            alpha = sum(samples) / len(samples)
            alpha_ = 1.0 - alpha
        # Local coordinates interpolation for fill
        start_u = line.start.u
        start_v = line.start.v
        u_diff = line.end.u - start_u
        v_diff = line.end.v - start_v
        # Rasterization
        iter_num = ((screen_end.x - screen_start.x) / dir.x if dir.x
                    else (screen_end.y - screen_start.y) / dir.y)
        iter_num_inv = 1.0 / iter_num
        pos = Vec2(screen_start.x, screen_start.y)
        for i in range(round(iter_num)):
            dis_x = round(pos.x)
            dis_y = round(pos.y)
            if 0 <= dis_x < width and 0 <= dis_y < height:
                interpolation_pos = i * iter_num_inv
                fill_color = fill.get_color(
                    interpolation_pos * u_diff + start_u,
                    interpolation_pos * v_diff + start_v,
                )
                if use_msaa:
                    for j, sampled in enumerate(samples):
                        if sampled:
                            color = data[((dis_y * width + dis_x) << level) + j]
                            color.r = fill_color.r
                            color.g = fill_color.g
                            color.b = fill_color.b
                            color.a = fill_color.a
                elif use_aaa:
                    color: Color = data[dis_y * width + dis_x]
                    color.r = alpha * fill_color.r + alpha_ * color.r
                    color.g = alpha * fill_color.g + alpha_ * color.g
                    color.b = alpha * fill_color.b + alpha_ * color.b
                    color.a = fill_color.a
                else:
                    color = data[dis_y * width + dis_x]
                    color.r = fill_color.r
                    color.g = fill_color.g
                    color.b = fill_color.b
                    color.a = fill_color.a
            pos += dir

def rasterize_circle(renderer: Renderer,
                     circle: Circle,
                     render_context: RenderContext,
                     scene: Scene | None = None) -> None:
    # Localize variables & AA
    aa = renderer.anti_aliasing
    use_aaa = isinstance(aa, AAA)
    use_msaa = isinstance(aa, MSAA)
    use_ssaa = isinstance(aa, SSAA)
    if use_ssaa:
        width = render_context.ss_buffer.width
        height = render_context.ss_buffer.height
        data = render_context.ss_buffer.data
    else:
        width = render_context.width
        height = render_context.height
        data = (render_context.ms_buffer.data if use_msaa
                else render_context.color_buffer.data)
    if use_aaa or use_msaa:
        level = aa._level
        pattern = aa.pattern
        sample_num = 1 << level
    scalar = render_context._abso_coord_scalar
    scalar_inv = 1 / scalar
    half_local_radius = 0.5 / circle.radius
    transform = circle.transform
    fill = circle.fill
    # Transformation to screen coordinates
    vec = transform.apply(_VEC2_0_0)
    screen_x = vec.x * scalar
    screen_y = vec.y * scalar
    radius = circle.radius * circle.transform.get_scale_factor()
    screen_radius = radius * scalar
    screen_radius_squared = screen_radius * screen_radius
    # Rasterization
    y_first_row = round(screen_y - screen_radius)
    row_starting = y_first_row * width
    for y in range(y_first_row, 
                   round(screen_y + screen_radius) + 1):
        if 0 <= y < height:
            for x in range(round(screen_x - screen_radius), 
                           round(screen_x + screen_radius) + 1):
                if 0 <= x < width:
                    local = transform.unapply(Vec2(x * scalar_inv, y * scalar_inv))
                    fill_color = fill.get_color(local.x * half_local_radius + 0.5,
                                                local.y * half_local_radius + 0.5)

                    # fill_color = fill.get_color(abso_u, abso_v)
                    diff_x = x - screen_x
                    diff_y = y - screen_y
                    if use_msaa:
                        samples = ((diff_x+dx)*(diff_x+dx) 
                                   + (diff_y+dy)*(diff_y+dy) 
                                   <= screen_radius_squared 
                                   for dx, dy in pattern)
                        for i, sampled in enumerate(samples, (row_starting + x) << level):
                            if sampled:
                                old_color = data[i]
                                old_color.r = fill_color.r
                                old_color.g = fill_color.g
                                old_color.b = fill_color.b
                                old_color.a = fill_color.a
                    elif use_aaa:
                        samples = ((diff_x+dx)*(diff_x+dx) 
                                   + (diff_y+dy)*(diff_y+dy) 
                                   <= screen_radius_squared 
                                   for dx, dy in pattern)
                        alpha = sum(samples) / sample_num
                        alpha_ = 1.0 - alpha
                        old_color = data[row_starting + x]
                        old_color.r = alpha * fill_color.r + alpha_ * old_color.r
                        old_color.g = alpha * fill_color.g + alpha_ * old_color.g
                        old_color.b = alpha * fill_color.b + alpha_ * old_color.b
                        old_color.a = fill_color.a
                    else:
                       
                        if diff_x*diff_x + diff_y*diff_y <= screen_radius_squared:
                            old_color = data[row_starting + x]
                            old_color.r = fill_color.r
                            old_color.g = fill_color.g
                            old_color.b = fill_color.b
                            old_color.a = fill_color.a
        row_starting += width



def rasterize_triangle(renderer: Renderer,
                       triangle: Triangle,
                       render_context: RenderContext,
                       scene: Scene | None = None) -> None:
    transform = triangle.transform
    a = transform.apply(triangle.a) * render_context._abso_coord_scalar
    b = transform.apply(triangle.b) * render_context._abso_coord_scalar
    c = transform.apply(triangle.c) * render_context._abso_coord_scalar
    # Manually sort vertices by y-coordinate
    if a.y > b.y:
        a, b = b, a
    if a.y > c.y:
        a, c = c, a
    if b.y > c.y:
        b, c = c, b
    # We calculate the left and right t-slopes of the triangle
    # before entering the flat top or flat bottom triangle functions,
    # so we can reuse the slope calculated to split a regular triangle
    # into
    #
    # Flat top triangles
    if a.y == b.y:
        if a.x > b.x:
            a, b = b, a
        t_left = (c.x - a.x) / (c.y - a.y)
        t_right = (c.x - b.x) / (c.y - b.y)
        _rasterize_flat_top_triangle(renderer, t_left, t_right, a, b, c, triangle, render_context, scene)
    # Flat bottom triangles
    elif b.y == c.y:
        if b.x > c.x:
            b, c = c, b
        t_left = (b.x - a.x) / (b.y - a.y)
        t_right = (c.x - a.x) / (c.y - a.y)
        _rasterize_flat_bottom_triangle(renderer, t_left, t_right, a, b, c, triangle, render_context, scene)
    # Regular triangles
    else:
        # Split the triangle into two triangles
        t_ab = (b.x - a.x) / (b.y - a.y)
        t_ac = (c.x - a.x) / (c.y - a.y)
        t_bc = (b.x - c.x) / (b.y - c.y)
        mid_x = a.x + (b.y - a.y) * t_ac
        t_uv = (b.y - a.y) / (c.y - a.y)
        t_uv_ = 1.0 - t_uv
        mid = Vertex2(mid_x, b.y, 
                      a.u * t_uv_ + c.u * t_uv, 
                      a.v * t_uv_ + c.v * t_uv)
        if mid_x < b.x:
            _rasterize_flat_bottom_triangle(renderer, t_ac, t_ab, a, mid, b, triangle, render_context, scene)
            _rasterize_flat_top_triangle(renderer, t_ac, t_bc, mid, b, c, triangle, render_context, scene)
        else:
            _rasterize_flat_bottom_triangle(renderer, t_ab, t_ac, a, b, mid, triangle, render_context, scene)
            _rasterize_flat_top_triangle(renderer, t_bc, t_ac, b, mid, c, triangle, render_context, scene)


def rasterize_rectangle(renderer: Renderer,
                        rectangle: Rectangle,
                        render_context: RenderContext,
                        scene: Scene | None = None) -> None:
    raise NotImplementedError

def rasterize_line(renderer: Renderer,
                   line: Line,
                   render_context: RenderContext,
                   scene: Scene | None = None) -> None:
    raise NotImplementedError

def _rasterize_row(
                   x_left: float,
                   x_right: float,
                   y: float,
                   width: int,
                   u_left: float,
                   v_left: float,
                   u_right: float,
                   v_right: float,
                   fill: Fill,
                   data: tuple[Color],
                   use_msaa: bool, 
                   use_aaa: bool,
                   sample_num: int = 0,
                   level: int = 0,
                   pattern: tuple[tuple[float, float, float]] = tuple(),
                   alpha_increament: float = 0.0) -> None:
    # one pixel should be rendered when  x_right equals x_left
    x_diff = 1 + x_right - x_left
    # Apply AA on the edges and rasterize
    if use_aaa:
        alpha_left = alpha_right = 0.0
        for dx, left_edge_dx, right_edge_dx in pattern:
            if left_edge_dx + x_left <= round(x_left) + dx:
                alpha_left += alpha_increament
            if round(x_right) + dx <= right_edge_dx + x_right:
                alpha_right += alpha_increament
        # Left edge
        alpha_left_ = 1 - alpha_left
        new_color_left = fill.get_color(u_left, v_left)
        old_color_left = data[round(y * width) + round(x_left)]
        old_color_left.r = new_color_left.r * alpha_left + old_color_left.r * alpha_left_
        old_color_left.g = new_color_left.g * alpha_left + old_color_left.g * alpha_left_
        old_color_left.b = new_color_left.b * alpha_left + old_color_left.b * alpha_left_
        old_color_left.a = new_color_left.a
        # Right edge
        alpha_right_ = 1 - alpha_right
        new_color_right = fill.get_color(u_right, v_right)
        old_color_right = data[round(y * width) + round(x_right)]
        old_color_right.r = new_color_right.r * alpha_right + old_color_right.r * alpha_right_
        old_color_right.g = new_color_right.g * alpha_right + old_color_right.g * alpha_right_
        old_color_right.b = new_color_right.b * alpha_right + old_color_right.b * alpha_right_
        old_color_right.a = new_color_right.a
        # Rasterize the pixels between the left and right edges
        for x in range(ceil(x_left), floor(x_right) + 1):
            if 0 <= x < width:
                # UV
                tx = (x - x_left) / x_diff
                tx_ = 1.0 - tx
                u = u_left * tx_ + u_right * tx
                v = v_left * tx_ + v_right * tx
                new_color = fill.get_color(u, v)
                old_color = data[round(y * width) + x]
                old_color.r = new_color.r
                old_color.g = new_color.g
                old_color.b = new_color.b
                old_color.a = new_color.a
    elif use_msaa:
        new_color_left = fill.get_color(u_left, v_left)
        new_color_right = fill.get_color(u_right, v_right)
        left_index_start = (round(y * width) + round(x_left)) << level
        right_index_start = (round(y * width) + round(x_right)) << level
        for i, (dx, left_edge_dx, right_edge_dx) in enumerate(pattern):
            if left_edge_dx + x_left <= round(x_left) + dx:
                old_color_left = data[left_index_start + i]
                old_color_left.r = new_color_left.r
                old_color_left.g = new_color_left.g
                old_color_left.b = new_color_left.b
                old_color_left.a = new_color_left.a
            if round(x_right) + dx <= right_edge_dx + x_right:
                old_color_right = data[right_index_start + i]
                old_color_right.r = new_color_right.r
                old_color_right.g = new_color_right.g
                old_color_right.b = new_color_right.b
                old_color_right.a = new_color_right.a
        # Rasterize the pixels between the left and right edges
        for x in range(ceil(x_left), floor(x_right) + 1):
            if 0 <= x < width:
                # UV
                tx = (x - x_left) / x_diff
                tx_ = 1.0 - tx
                u = u_left * tx_ + u_right * tx
                v = v_left * tx_ + v_right * tx
                new_color = fill.get_color(u, v)
                start = (round(y * width) + x) << level
                for old_color in data[start : start + sample_num]:
                    old_color.r = new_color.r
                    old_color.g = new_color.g
                    old_color.b = new_color.b
                    old_color.a = new_color.a
    else:
        # Rasterize the pixels between the left and right edges
        for x in range(round(x_left), round(x_right) + 1):
            if 0 <= x < width:
                # UV
                tx = (x - x_left) / x_diff
                tx_ = 1.0 - tx
                u = u_left * tx_ + u_right * tx
                v = v_left * tx_ + v_right * tx
                new_color = fill.get_color(u, v)
                old_color = data[round(y * width) + x]
                old_color.r = new_color.r
                old_color.g = new_color.g
                old_color.b = new_color.b
                old_color.a = new_color.a

def _rasterize_flat_top_triangle(renderer: Renderer,
                                 t_left: float,
                                 t_right: float,
                                 left: Vertex2,
                                 right: Vertex2,
                                 bottom: Vertex2,
                                 triangle: Triangle,
                                 render_context: RenderContext,
                                 scene: Scene | None = None) -> None:
    # Localize variables & AA
    aa = renderer.anti_aliasing
    use_ssaa = isinstance(aa, SSAA)
    use_msaa = isinstance(aa, MSAA)
    use_aaa = isinstance(aa, AAA)
    if use_ssaa:
        width = render_context.ss_buffer.width
        height = render_context.ss_buffer.height
        data = render_context.ss_buffer.data
    else:
        width = render_context.width
        height = render_context.height
        data = (render_context.ms_buffer.data if use_msaa 
                else render_context.color_buffer.data)
    pattern = level = sample_num = alpha_increament = None
    if use_msaa or use_aaa:
        pattern = tuple((dx, dy * t_left, dy * t_right) for dx, dy in aa.pattern)
        level = aa._level
        sample_num = 1 << level
        alpha_increament = 1 / len(pattern)
    fill = triangle.fill
    # Preparation for uv interpolation
    y_diff = bottom.y - left.y
    # Rasterization
    for y in range(round(left.y), round(bottom.y) + 1):
        if 0 <= y < height:
            # Calculate the x-coordinates of the left and right edges
            x_left = bottom.x + (y - bottom.y) * t_left
            x_right = bottom.x + (y - bottom.y) * t_right
            # Preparation for uv interpolation
            ty = (y - left.y) / y_diff
            ty_ = 1.0 - ty
            u_left = left.u * ty_ + bottom.u * ty
            u_right = right.u * ty_ + bottom.u * ty
            v_left = left.v * ty_ + bottom.v * ty
            v_right = right.v * ty_ + bottom.v * ty
            _rasterize_row(x_left, x_right, 
                           y, 
                           width, 
                           u_left, v_left, 
                           u_right, v_right, 
                           fill, 
                           data, 
                           use_msaa, use_aaa,
                           sample_num, level, pattern, alpha_increament)
            

def _rasterize_flat_bottom_triangle(renderer: Renderer,
                            t_left: float,
                            t_right: float,
                               top: Vertex2,
                                 left: Vertex2,
                                 right: Vertex2,
                                triangle: Triangle,
                                render_context: RenderContext,
                                scene: Scene | None = None) -> None:
    # Localize variables & AA
    aa = renderer.anti_aliasing
    use_ssaa = isinstance(aa, SSAA)
    use_msaa = isinstance(aa, MSAA)
    use_aaa = isinstance(aa, AAA)
    if use_ssaa:
        width = render_context.ss_buffer.width
        height = render_context.ss_buffer.height
        data = render_context.ss_buffer.data
    else:
        width = render_context.width
        height = render_context.height
        data = (render_context.ms_buffer.data if use_msaa 
                else render_context.color_buffer.data)
    pattern = level = sample_num = alpha_increament = None
    if use_msaa or use_aaa:
        pattern = tuple((dx, dy * t_left, dy * t_right) for dx, dy in aa.pattern)
        level = aa._level
        sample_num = 1 << level
        alpha_increament = 1 / len(pattern)
    fill = triangle.fill
    # Preparation for uv interpolation
    y_diff = left.y - top.y
    # Rasterization
    for y in range(round(top.y), round(left.y) + 1):
        if 0 <= y < height:
            # Calculate the x-coordinates of the left and right edges
            x_left = top.x + (y - top.y) * t_left
            x_right = top.x + (y - top.y) * t_right
            # UV of the left and right edges
            ty = (y - top.y) / y_diff
            ty_ = 1.0 - ty
            u_left = left.u * ty + top.u * ty_
            u_right = right.u * ty + top.u * ty_
            v_left = left.v * ty + top.v * ty_
            v_right = right.v * ty + top.v * ty_
            _rasterize_row(x_left, x_right, 
                           y, 
                           width, 
                           u_left, v_left, 
                           u_right, v_right, 
                           fill, 
                           data, 
                           use_msaa, use_aaa,
                           sample_num, level, pattern, alpha_increament)

RASTERIZERS = {
    Node: rasterize_node,
    Dot: rasterize_dot,
    SimpleLine: rasterize_simple_line,
    Circle: rasterize_circle,
    Triangle: rasterize_triangle,
    Rectangle: rasterize_rectangle,
    Line: rasterize_line,
}
