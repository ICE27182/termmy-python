

from __future__ import annotations

from .render_context import RenderContext
from ..core import NormFloat, Vec2Rela
from ..colors import Color
from ..graphics import Scene, Node, Dot, SimpleLine, Line

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from .renderer import Renderer

# Used internally. Supposed to be read-only
_VEC2_1_1 = Vec2Rela(1.0, 1.0)
_VEC2_0_0 = Vec2Rela(0.0, 0.0)

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
    """Node is only used for grouping nodes."""
    pass

def rasterize_dot(renderer: Renderer,
                  dot: Dot,
                  render_context: RenderContext,
                  scene: Scene | None = None) -> None:
    """MSAA, SSAA and AAA do not have sepcial effects on
    the rendering of a dot.
    """
    if dot.fill:
        width = render_context.width
        height = render_context.height
        transform = dot.transform
        sample_num = len(renderer.msaa)
        data = (render_context.ms_buffer.data if sample_num
                else render_context.color_buffer.data)
        fill_color = dot.fill.color
        vec = transform.apply(_VEC2_0_0)
        x = round(vec.x * width)
        y = round(vec.y * height)
        if 0 <= x < width and 0 <= y < height:
            if sample_num:
                start = (y * width + x) * sample_num
                for i in range(start, start + sample_num):
                    old_color = data[i]
                    old_color.r = fill_color.r
                    old_color.g = fill_color.g
                    old_color.b = fill_color.b
                    old_color.a = fill_color.a
            else:
                old_color = data[y * width + x]
                old_color.r = fill_color.r
                old_color.g = fill_color.g
                old_color.b = fill_color.b
                old_color.a = fill_color.a



def rasterize_simple_line(renderer: Renderer,
                          line: SimpleLine,
                          render_context: RenderContext,
                          scene: Scene | None = None):
    fill = line.fill
    if fill:
        width = render_context.width
        width_inv = 1 / width
        height = render_context.height
        height_inv = 1 / height

        transform = line.transform
        translate_x = transform.translate.x
        translate_y = transform.translate.y

        start = transform.apply(line.start)
        end = transform.apply(line.end)

        dir_x = end.x - start.x
        dir_y = end.y - start.y
        len_inv = (dir_x*dir_x + dir_y*dir_y) ** -0.5
        dir_x *= len_inv * width_inv
        # It is width_inv here below, not height_inv
        dir_y *= len_inv * width_inv

        x = start.x
        y = start.y

        sample_num = len(renderer.msaa)
        data = (render_context.ms_buffer.data if sample_num
                else render_context.color_buffer.data)
        
        for _ in range(round(width * height_inv * ((line.width * width)**2 + (line.height * height)**2)**0.5)):
            dis_x = round(x * width)
            dis_y = round(y * height)
            if 0 <= dis_x < width and 0 <= dis_y < height:
                # TODO Add AAs
                old_color = data[dis_y * width + dis_x]
                fill_color = fill.get_color(
                    x - translate_x, 
                    y - translate_y,
                )
                old_color.r = fill_color.r
                old_color.g = fill_color.g
                old_color.b = fill_color.b
                old_color.a = fill_color.a
            x += dir_x
            y += dir_y

RASTERIZERS = {
    Node: rasterize_node,
    Dot: rasterize_dot,
    SimpleLine: rasterize_simple_line
}
