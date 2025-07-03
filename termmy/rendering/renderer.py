

from __future__ import annotations

from ..core import NormFloat
from ..colors import Color
from ..buffers import ColorBuffer, Buffer2D
from ..graphics import Scene, Node

from .anti_aliasing import MSAA, AAA, SSAA
from .anti_aliasing import MSAAoff, AAAoff, SSAAoff
from .rasterizer import Rasterizer

from dataclasses import dataclass
from typing import ClassVar, Callable, overload

@dataclass
class Renderer:
    rasterizers: ClassVar[
        dict[
            type, 
            Callable[
                [Renderer, Node, 
                int, int, 
                NormFloat, NormFloat, 
                list[Color]],
                list[Color],
            ]
            | Rasterizer,
        ] 
    ]
    msaa: MSAA = MSAAoff
    aaa: AAA = AAAoff
    ssaa: SSAA = SSAAoff
    fxaa: bool = False

    @overload
    def render_to(self, scene: Scene,  buffer: Buffer2D) -> Buffer2D:
        """Render the scene to the provided buffer.

        Passing in a `ColorBuffer` is more efficient than passing in a
        general `Buffer2D` as it allows this method to access the color
        directly without using its getters and setters.

        Text tags will be ignored. They are only supported in `display`.

        Args:
            scene (Scene): The scene to render. Its base buffer will be 
                streched if its dimensions do not match those of the target
                buffer. Make sure they have the same dimensions to achieve
                lowest overhead.
            buffer (Buffer2D): The buffer to render to.
        
        Returns:
            Buffer2D: A reference to the color buffer passed in.
        """
    @overload
    def render_to(self, scene: Scene, buffer: ColorBuffer) -> ColorBuffer:
        """Render the scene to the provided color buffer.

        Passing in a `ColorBuffer` is more efficient than passing in a
        general `Buffer2D` as it allows this method to access the color
        directly without using its getters and setters.

        Text tags will be ignored. They are only supported in `display`.

        Args:
            scene (Scene): The scene to render. Its base buffer will be 
                streched if its dimensions do not match those of the target
                buffer. Make sure they have the same dimensions to achieve
                lowest overhead.
            buffer (ColorBuffer): The color buffer to render to.
        
        Returns:
            Buffer2D: A reference to the color buffer passed in.
        """
    def render_to(self, scene: Scene, buffer: ColorBuffer) -> ColorBuffer:
        width = buffer.width
        height = buffer.height
        rendered_nodes = [None] * (width*height)
        for node in scene._nodes:
            self._render_node(node, width, height, 0.0, 0.0, rendered_nodes)
        if isinstance(buffer, ColorBuffer):
            if scene.base.width == width and scene.base.height == height:
                return Renderer._render_to_matched_color_buffer(
                    scene.base.data, 
                    buffer, 
                    rendered_nodes,
                )
            else:
                return Renderer._render_to_unmatched_color_buffer(
                    scene.base, 
                    buffer, 
                    rendered_nodes,
                )
        else: # isinstance(buffer, Buffer2D)
            if scene.base.width == width and scene.base.height == height:
                return Renderer._render_to_matched_buffer2d(
                    scene.base.data, 
                    buffer, 
                    rendered_nodes,
                )
            else:
                return Renderer._render_to_unmatched_buffer2d(
                    scene.base, 
                    buffer, 
                    rendered_nodes,
                )

    @overload
    def render(self, scene: Scene) -> ColorBuffer:
        """Render the scene to a new color buffer with the same dimensions
        as the scene's base buffer.

        Note that a new color buffer will be allocated. Use `render_to` if
        you want to render to an existing buffer to reduce the allocation 
        overhead.

        Text tags will be ignored. They are only supported in `display`.

        Args:
            scene (Scene): The scene to render. Its base buffer will be 
                streched if its dimensions do not match those of the target
                buffer. Make sure they have the same dimensions to achieve
                lowest overhead.

        Returns:
            ColorBuffer: A new color buffer with the same dimensions as the
                base buffer.
        """
    @overload
    def render(self, scene: Scene, width: int, height: int) -> ColorBuffer:
        """Render the scene to a new color buffer with the specified 
        dimensions.

        Note that a new color buffer will be allocated. Use `render_to` if
        you want to render to an existing buffer to reduce the allocation 
        overhead.

        Text tags will be ignored. They are only supported in `display`.

        Args:
            scene (Scene): The scene to render. Its base buffer will be 
                streched if its dimensions do not match those of the target
                buffer. Make sure they have the same dimensions to achieve
                lowest overhead.
            width (int): The width of the new color buffer. Must be a positive
                integer.
            height (int): The height of the new color buffer. 
                Must be a positive integer.
                
        Returns:
            ColorBuffer: A new color buffer of the specified dimensions.

        Raises:
           ValueError: If width or height are not positive integers.
        """
    def render(self, scene: Scene, width: int | None = None, 
               height: int | None = None) -> ColorBuffer | Buffer2D:
        if width is None and height is None:
            # render(self, scene: Scene) -> ColorBuffer
            return self.render_to(ColorBuffer(width=scene.base.width, 
                                              height=scene.base.height))
        elif width is not None and height is not None:
            # render(self, scene: Scene, width: int, height: int) -> ColorBuffer
            return self.render_to(ColorBuffer(width=width, height=height))
        else:
            raise TypeError("Both width and height must be provided or neither. "
                            f"Got {width=}, {height=}")
    
    def _render_node(self, 
                     node: Node, 
                     width: int, 
                     height: int, 
                     x_offset: NormFloat,
                     y_offset: NormFloat,
                     out: list[Color]) -> list[Color]:
        rasterizer = Renderer.rasterizers.get(type(node), None)
        if rasterizer:
            rasterizer(self, node, width, height, x_offset, y_offset, out)
        else:
            raise ValueError(f"No rasterizer found for {type(node)}")

        for child in node._children:
            self._render_node(child, out)
        return out

    @staticmethod
    def _render_to_matched_color_buffer(base_data: tuple[Color], 
                                        rendered_nodes: list[Color], 
                                        out: ColorBuffer) -> ColorBuffer:
        for i, (base_color, out_color) in enumerate(zip(base_data, out.data)):
            color = rendered_nodes[i] or base_color
            out_color.r = color.r
            out_color.g = color.g
            out_color.b = color.b
            out_color.a = color.a
        return out
    
    @staticmethod
    def _render_to_unmatched_color_buffer(base: ColorBuffer,
                                          rendered_nodes: list[Color], 
                                          out: ColorBuffer) -> ColorBuffer:
        out_width = out.width
        out_height = out.height
        x_scale = base.width / out_width
        y_scale = base.height / out_height
        base_data = base.data
        base_width = base.width

        row_starting_index = 0
        for y in range(out_height):
            for x in range(out_width):
                i = row_starting_index + x
                color = (rendered_nodes[i]
                         or base_data[int(y_scale*y*base_width + x_scale*x)])
                old_color = out.data[i]
                old_color.r = color.r
                old_color.g = color.g
                old_color.b = color.b
                old_color.a = color.a
            row_starting_index += out_width
        return out
    
    @staticmethod
    def _render_to_matched_buffer2d(base_data: tuple[Color], 
                                    rendered_nodes: list[Color], 
                                    out: Buffer2D) -> Buffer2D:
        out_width = out.width
        out_height = out.height
        row_starting_index = 0
        for y in range(out_height):
            for x in range(out_width):
                i = row_starting_index + x
                out.set_color(x, y, rendered_nodes[i] or base_data[i])
            row_starting_index += out_width
        return out
    
    @staticmethod
    def _render_to_unmatched_buffer2d(base: ColorBuffer,
                                      rendered_nodes: list[Color], 
                                      out: Buffer2D) -> Buffer2D:
        out_width = out.width
        out_height = out.height
        x_scale = base.width / out_width
        y_scale = base.height / out_height
        base_data = base.data
        base_width = base.width

        row_starting_index = 0
        for y in range(out_height):
            for x in range(out_width):
                i = row_starting_index + x
                color = (rendered_nodes[i]
                         or base_data[int(y_scale*y*base_width + x_scale*x)])
                out.set_color(x, y, color)
            row_starting_index += out_width
        return out
