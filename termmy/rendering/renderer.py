

from __future__ import annotations

from ..core import Transform2D
from ..colors import Color
from ..buffers import ColorBuffer, MultisampleColorBuffer
from ..graphics import Scene, Node

from .anti_aliasing import MSAA, AAA, SSAA
from .anti_aliasing import MSAAoff, AAAoff, SSAAoff
from .rasterizers import Rasterizer, RASTERIZERS
from .render_context import RenderContext

from dataclasses import dataclass
from typing import ClassVar, Callable

@dataclass(slots=True)
class Renderer:
    rasterizers: ClassVar[
        dict[
            type, 
            Callable[
                [Renderer, Node, RenderContext,
                 Transform2D, Scene],
                None,
            ]
            | Rasterizer,
        ] 
    ] = RASTERIZERS
    msaa: MSAA = MSAAoff
    aaa: AAA = AAAoff
    ssaa: SSAA = SSAAoff

    def render(self, scene: Scene, render_context: RenderContext) -> ColorBuffer:
        """Render the scene to a new color buffer with the same dimensions
        as the scene's base buffer.

        Text tags will be ignored.

        Args:
            scene (Scene): The scene to render. Its base buffer will be 
                streched if its dimensions do not match those of the target
                buffer. Make sure they have the same dimensions to achieve
                lowest overhead.
            render_context (RenderContext): The render context to use for rendering.
        Returns:
            ColorBuffer: A reference to the `render_context.color_buffer`.
        """
        raise NotImplementedError
        
    
    def initiate_buffer(self, scene: Scene, render_context: RenderContext) -> None:
        width = render_context.width
        height = render_context.height
        buffer = render_context.color_buffer
        base = scene.base
        if self.msaa:
            if base.width == width and base.height == height:
                _initiate_matched_ms_buffer(
                    base.data,
                    self.msaa,
                    buffer,
                )
            else:
                _initiate_unmatched_ms_buffer(
                    base,
                    self.msaa,
                    buffer,
                )
        else:
            if base.width == width and base.height == height:
                _initiate_matched_color_buffer(
                    base.data,
                    buffer,
                )
            else:
                _initiate_unmatched_color_buffer(
                    base,
                    buffer,
                )
            
    def render_nodes(self, scene: Scene, render_context: RenderContext) -> None:
        for node in scene._nodes:
            self._render_node(node, render_context, scene=scene)
        if self.msaa:
            render_context.ms_buffer.resolve_to(render_context.color_buffer)
    
    def _render_node(self, 
                     node: Node, 
                     render_context: RenderContext,
                     scene: Scene) -> None:
        rasterizer = Renderer.rasterizers.get(type(node), None)
        if rasterizer:
            rasterizer(self, node, render_context, scene=scene)
        else:
            raise ValueError(f"No rasterizer found for {type(node)}")
        for child in node._children:
            self._render_node(child, render_context, scene=scene)


################################################################
# Internal functions
################################################################
    
def _initiate_matched_color_buffer(base_data: tuple[Color],
                                   out: ColorBuffer) -> ColorBuffer:
    for i, (base_color, out_color) in enumerate(zip(base_data, out.data)):
        out_color.r = base_color.r
        out_color.g = base_color.g
        out_color.b = base_color.b
        out_color.a = base_color.a

def _initiate_unmatched_color_buffer(base: ColorBuffer,
                                     out: ColorBuffer) -> ColorBuffer:
    out_width, out_height = out.width, out.height
    x_scale, y_scale = base.width/out_width, base.height/out_height
    base_data = base.data
    base_width, row_starting_index = base.width, 0
    for y in range(out_height):
        for x in range(out_width):
            i = row_starting_index + x
            color = base_data[int(y_scale*y)*base_width + int(x_scale*x)]
            old_color = out.data[i]
            old_color.r = color.r
            old_color.g = color.g
            old_color.b = color.b
            old_color.a = color.a
        row_starting_index += out_width

def _initiate_matched_ms_buffer(base_data: tuple[Color],
                                msaa: MSAA,
                                out: MultisampleColorBuffer) -> ColorBuffer:
    """
    Assuming msaa is not off, i.e. len(msaa) > 0.
    
    If msaa is off, this function will do nothing. 
    Use `_initiate_matched_color_buffer` instead.
    """
    sample_num = len(msaa)
    for i, base_color in enumerate(base_data):
        start = i * sample_num
        for j in range(sample_num):
            out_color = out.data[start + j]
            out_color.r = base_color.r
            out_color.g = base_color.g
            out_color.b = base_color.b
            out_color.a = base_color.a

def _initiate_unmatched_ms_buffer(base: ColorBuffer,
                                  msaa: MSAA,
                                  out: MultisampleColorBuffer) -> ColorBuffer:
    """
    Assuming msaa is not off, i.e. len(msaa) > 0.
    
    If msaa is off, this function will do nothing. 
    Use `_initiate_matched_color_buffer` instead.
    """
    out_width, out_height = out.width, out.height
    x_scale, y_scale = base.width/out_width, base.height/out_height
    base_data = base.data
    base_width, row_starting_index = base.width, 0
    sample_num = len(msaa)
    for y in range(out_height):
        for x in range(out_width):
            color = base_data[int(y_scale*y)*base_width + int(x_scale*x)]
            start = (row_starting_index + x) * sample_num
            for j in range(sample_num):
                old_color = out.data[start + j]
                old_color.r = color.r
                old_color.g = color.g
                old_color.b = color.b
                old_color.a = color.a
        row_starting_index += out_width
################################################################
