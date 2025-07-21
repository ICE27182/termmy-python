

from __future__ import annotations

from .render_context import RenderContext
from .anti_aliasing import MSAA, AAA, SSAA
from ..core import NormFloat, Vec2
from ..colors import Color
from ..graphics import Scene, Node, Dot, SimpleLine, Line

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
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
        aa = renderer.anti_aliasing
        use_aaa = isinstance(aa, AAA)
        uses_msaa = isinstance(aa, MSAA)
        use_ssaa = isinstance(aa, SSAA)
        if use_ssaa:
            width = render_context.ss_buffer.width
            height = render_context.ss_buffer.height
            data = render_context.ss_buffer.data
        else:
            width = render_context.width
            height = render_context.height
            data = (render_context.ms_buffer.data if uses_msaa
                    else render_context.color_buffer.data)
        
        vec = dot.transform.apply(_VEC2_0_0)
        screen_x = vec.x * render_context._abso_coord_scalar
        screen_y = vec.y * render_context._abso_coord_scalar

        if 0.0 <= screen_x < width and 0.0 <= screen_y < height:
            fill_color = dot.fill.color
            if uses_msaa:
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
        # Localize variables
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
        local_start = line.start
        local_end = line.end
        # Transformation to screen coordinates
        screen_start = transform.apply(local_start)
        screen_end = transform.apply(local_end)
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
        local_diff = local_end - local_start
        iter_num = ((screen_end.x - screen_start.x) / dir.x if dir.x
                    else (screen_end.y - screen_start.y) / dir.y)
        iter_num_inv = 1.0 / iter_num
        # Starting
        pos = Vec2(screen_start.x, screen_start.y)
        for i in range(round(iter_num)):
            dis_x = round(pos.x)
            dis_y = round(pos.y)
            if 0 <= dis_x < width and 0 <= dis_y < height:
                interpolation_pos = i * iter_num_inv
                fill_color = fill.get_color(
                    round(interpolation_pos * local_diff.x + local_start.x),
                    round(interpolation_pos * local_diff.y + local_start.y),
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

RASTERIZERS = {
    Node: rasterize_node,
    Dot: rasterize_dot,
    SimpleLine: rasterize_simple_line
}
