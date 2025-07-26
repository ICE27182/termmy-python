

from __future__ import annotations

from .render_context import RenderContext
from .anti_aliasing import MSAA, AAA, SSAA
from ..core import NormFloat, Vec2
from ..colors import Color
from ..graphics import Scene, Node
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
                    round(interpolation_pos * u_diff + start_u),
                    round(interpolation_pos * v_diff + start_v),
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
    transform = circle.transform
    # Transformation to screen coordinates
    vec = transform.apply(_VEC2_0_0)
    screen_x = vec.x * scalar
    screen_y = vec.y * scalar
    radius = circle.radius * circle.transform.get_scale_factor()
    screen_radius = radius * scalar
    screen_radius_squared = screen_radius * screen_radius
    # Local coordinates interpolation for fill
    # Let the uv of the center of a circle be (0.5, 0.5)
    # Unlike triangles or lines, circles do not have vertices
    # that undergo transformations
    increament = 0.5 * circle.radius / screen_radius
    uv_increaments = transform.apply_rotation(Vec2(increament, increament))
    u_increament = uv_increaments.x
    v_increament = uv_increaments.y
    fill = circle.fill
    # Rasterization
    abso_v = 0.0
    y_first_row = round(screen_y - screen_radius)
    row_starting = y_first_row * width
    for y in range(y_first_row, 
                   round(screen_y + screen_radius) + 1):
        if 0 <= y < height:
            abso_u = 0.0
            for x in range(round(screen_x - screen_radius), 
                           round(screen_x + screen_radius) + 1):
                if 0 <= x < width:
                    fill_color = fill.get_color(abso_u, abso_v)
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
                    abso_u += u_increament
        abso_v += v_increament
        row_starting += width



def rasterize_triangle(renderer: Renderer,
                       triangle: Triangle,
                       render_context: RenderContext,
                       scene: Scene | None = None) -> None:
    transform = triangle.transform
    a = transform.apply(triangle.a)
    b = transform.apply(triangle.b)
    c = transform.apply(triangle.c)
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
        t_left = (b.x - a.x) / (b.y - a.y)
        t_right = (c.x - a.x) / (c.y - a.y)
        mid = Vec2(a.x + (b.y - a.y) * t_left, b.y)
        _rasterize_flat_top_triangle(renderer, t_left, t_right, a, b, mid, triangle, render_context, scene)
        _rasterize_flat_bottom_triangle(renderer, t_left, t_right, b, mid, c, triangle, render_context, scene)


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

def _rasterize_flat_top_triangle(renderer: Renderer,
                                 t_left: float,
                                 t_right: float,
                                 left: Vec2,
                                 right: Vec2,
                                 bottom: Vec2,
                                 triangle: Triangle,
                                 render_context: RenderContext,
                                 scene: Scene | None = None) -> None:
    # Localize variables
    width = render_context.width
    height = render_context.height
    # Rasterization
    for y in range(round(left.y), round(bottom.y) + 1):
        if 0 <= y < height:
            # Calculate the x-coordinates of the left and right edges
            x_left = bottom.x + (y - bottom.y) * t_left
            x_right = bottom.x + (y - bottom.y) * t_right
            # Apply AA on the edges

            # Rasterize the pixels between the left and right edges
            for x in range(ceil(x_left), ceil(x_right) + 1):
                if 0 <= x < width:
                    color = triangle.fill.get_color(x, y)
                    render_context.color_buffer.data[y * width + x] = color

def _rasterize_flat_bottom_triangle(renderer: Renderer,
                            t_left: float,
                            t_right: float,
                               top: Vec2,
                                 left: Vec2,
                                 right: Vec2,
                                triangle: Triangle,
                                render_context: RenderContext,
                                scene: Scene | None = None) -> None:
    raise NotImplementedError

RASTERIZERS = {
    Node: rasterize_node,
    Dot: rasterize_dot,
    SimpleLine: rasterize_simple_line,
    Circle: rasterize_circle,
    Triangle: rasterize_triangle,
    Rectangle: rasterize_rectangle,
    Line: rasterize_line,
}
