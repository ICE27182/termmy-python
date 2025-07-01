

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Iterator
from itertools import islice
from typing import overload

from .node import Node
from ..buffers import ColorBuffer, Buffer2D
from ..buffers.text_tag import TextTag
from ..colors import Color
from ..core import Vec2i

@dataclass(slots=True)
class Scene:
    # In the rendering output, base may be streched to the size of the output.
    base: ColorBuffer
    # Hidden to maintain its order.
    _nodes: list[Node] = field(default_factory=list)
    text_tags: list[TextTag] = field(default_factory=list)

    def add_node(self, node: Node) -> Scene:
        """Add a new node. Returns itself for chaining."""
        self._nodes.append(node)
        self._nodes.sort(key=lambda node: node.z)
        return self
    
    def remove_node(self, node: Node) -> Scene:
        """Remove a node from this node.

        Returns:
            Scene: Returns itself for chaining.

        Raises:
            ValueError: If `node` is not a node of this scene.
        """
        self._nodes.remove(node)
        return self
    
    def nodes(self) -> Iterator[Node]:
        """Return an iterator over the nodes in the scene."""
        return iter(self._nodes)
    
    @overload
    def render_to(self, buffer: Buffer2D) -> Buffer2D:
        """Render the scene to the provided buffer.

        Passing in a `ColorBuffer` is more efficient than passing in a
        general `Buffer2D` as it allows this method to access the color
        directly without using its getters and setters.

        Text tags will be ignored. They are only supported in `display`.

        Args:
            buffer (Buffer2D): The buffer to render to.
        
        Returns:
            Buffer2D: A reference to the color buffer passed in.
        """
    @overload
    def render_to(self, buffer: ColorBuffer) -> ColorBuffer:
        """Render the scene to the provided color buffer.

        Passing in a `ColorBuffer` is more efficient than passing in a
        general `Buffer2D` as it allows this method to access the color
        directly without using its getters and setters.

        Text tags will be ignored. They are only supported in `display`.

        Args:
            buffer (ColorBuffer): The color buffer to render to.
        
        Returns:
            Buffer2D: A reference to the color buffer passed in.
        """
    def render_to(
        self, 
        buffer: Buffer2D | ColorBuffer,
    ) -> Buffer2D | ColorBuffer:
        width = buffer.width
        height = buffer.height
        rendered_nodes: dict[int, Color] = {}
        for node in self._nodes:
            node._render(width, height, 0.0, 0.0, rendered_nodes)
        x_scale = self.base.width / width
        y_scale = self.base.height / height
        base_data = self.base.data
        base_width = self.base.width
        if isinstance(buffer, ColorBuffer):
            for y in range(height):
                for x in range(width):
                    i = y * width + x
                    color = rendered_nodes.get(
                        i, 
                        base_data[int(y_scale*y*base_width + x_scale*x)],
                    )
                    old_color = buffer.data[i]
                    old_color.r = color.r
                    old_color.g = color.g
                    old_color.b = color.b
                    old_color.a = color.a
        else:
            for y in range(height):
                for x in range(width):
                    i = y * width + x
                    color = rendered_nodes.get(
                        i, 
                        base_data[int(y_scale*y*base_width + x_scale*x)],
                    )
                    buffer.set_color(x, y, color)
        return buffer
    
    @overload
    def render(self) -> ColorBuffer:
        """Render the scene to a new color buffer with the same dimensions
        as the base buffer.

        Note that a new color buffer will be allocated. Use `render_to` if
        you want to render to an existing buffer to reduce the allocation 
        overhead.

        Text tags will be ignored. They are only supported in `display`.
        
        Returns:
            ColorBuffer: A new color buffer with the same dimensions as the
                base buffer.
        """
    @overload
    def render(self, width: int, height: int) -> ColorBuffer:
        """Render the scene to a new color buffer with the specified 
        dimensions.

        Note that a new color buffer will be allocated. Use `render_to` if
        you want to render to an existing buffer to reduce the allocation 
        overhead.

        Text tags will be ignored. They are only supported in `display`.
        
        Returns:
            ColorBuffer: A new color buffer of the specified dimensions.
        """
    def render(self, width: int | None = None, 
               height: int | None = None) -> ColorBuffer | Buffer2D:
        if width is None and height is None:
            # render(self) -> ColorBuffer
            return self.render_to(ColorBuffer(width=self.base.width, 
                                              height=self.base.height))
        elif width is not None and height is not None:
            # render(self, width: int, height: int) -> ColorBuffer
            return self.render_to(ColorBuffer(width=width, height=height))
        else:
            raise TypeError("Both width and height must be provided or neither. "
                            f"Got {width=}, {height=}")
    
    @overload
    def ansi24(self) -> str:
        """Render the scene to a string of ANSI 24-bit color codes. The dimensions
        are determined by the base buffer.
        
        Text tags will be rendered as well.

        Returns:
            str: A string containing ANSI 24-bit color codes representing the
                scene.
        """
    @overload
    def ansi24(self, width: int, height: int) -> str:
        """Render the scene to a string of ANSI 24-bit color codes.

        Text tags will be rendered as well.

        Args:
            width (int): The width of the output. Must be a positive integer.
            height (int): The height of the output. Must be a positive integer.
        Returns:
            str: A string containing ANSI 24-bit color codes representing the 
                scene.
        """
    def ansi24(self, width = None, height = None) -> str:
        if width is None and height is None:
            width, height = self.base.width, self.base.height
        elif not (width is not None and width > 0 
                  and height is not None and height > 0):
            raise ValueError("`width` and `height` must be positive integers."
                             f"Got {width=} and {height=}.")
        # Render Nodes
        rendered_nodes: dict[tuple[int, int], Color] = {}
        for node in self._nodes:
            node._render(width, height, 0.0, 0.0, rendered_nodes)
        # Output to string
        base_data = self.base.data
        str_buff = []
        text_tags = {(pos.x, pos.y): tag 
                     for tag in self.text_tags
                     if (pos:=tag.starting_position())}
        line_wrap = None
        text_tag_iter: Iterator | None = None
        x_scale = self.base.width / width
        y_scale = self.base.height / height
        for y in range(height):
            row_starting_index = y * width * y_scale
            for x in range(width):
                i = y * width + x
                color = rendered_nodes.get(
                    i, 
                    base_data[round(row_starting_index + x*x_scale)]
                )
                str_buff.append(color.to_ansi_bgd_24())
                if (x, y) in text_tags:
                    text_tag = text_tags[(x, y)]
                    text_tag_iter = iter(text_tag)
                    line_wrap = text_tag.line_wrap
                if text_tag_iter:
                    text = next(text_tag_iter, None)
                    if text:
                        str_buff.append(text)
                    else:
                        text_tag_iter = None
                        line_wrap = None
                        str_buff.append("\033[0m")
                else:
                    str_buff.append("  ")
            str_buff.append("\033[0m\n")
            if text_tag_iter and not line_wrap:
                text_tag_iter = None
                line_wrap = None
        str_buff.pop() # Remove the last newline character
        return "".join(str_buff)

