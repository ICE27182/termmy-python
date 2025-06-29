
from __future__ import annotations

from termmy.core import Vec2i
from termmy.colors import Color
from .msaa_patterns import MSAAPattern, MSAAoff, MSAAx2, MSAAx4, MSAAx8, MSAAx16
from typing import overload, TYPE_CHECKING
from warnings import deprecated
from collections.abc import Iterable, Iterator
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .text_tag import TextTag

class Buffer2D(ABC):

    def __init__(self, width: int, height: int):
        if not isinstance(width, int):
            raise TypeError(f"`width` must be an int. Got {type(width)}.")
        if not isinstance(height, int): 
            raise TypeError(f"`height` must be an int. Got {type(height)}.")
        if width <= 0:
            raise ValueError(f"`width` must be greater than 0. Got {width}.")
        if height <= 0:
            raise ValueError(f"`height` must be greater than 0. Got {height}.")
        self.width:int
        self.height:int

    def clear(self) -> Buffer2D:
        """
        Clear the frame buffer.
        """
        for y in range(self.height):
            for x in range(self.width):
                self.set_color(x, y, Color(0, 0, 0, 0))
        return self
    
    def fill(self, color: Color | None = None) -> Buffer2D:
        """
        Fill the frame buffer with `color`.

        `color` will default to Color(255, 255, 255, 255) if not provided.
        """
        color = color or Color(255, 255, 255, 255)
        for y in range(self.height):
            for x in range(self.width):
                self.set_color(x, y, color)
        return self

    @abstractmethod
    def get_color(self, x:int, y:int) -> Color:
        """
        Return a new Color object at (x, y).

        The return value is not a reference to the pixel stored in the buffer.

        Non-color derived classes should return a Color based on class 
        specific rules.
        """
    
    @abstractmethod
    def set_color(self, x:int, y:int, color: Color) -> Buffer2D:
        """
        Set the given color at (x, y). 
        
        The color will not be a reference to the argument.

        Non-color derived classes should should set its value(s) based on
        class specific rules.
        """
    
    @abstractmethod
    def add_color(self, x:int, y:int, color: Color) -> Buffer2D:
        """
        Add the given color to the color at (x, y) with transparency.

        Non-color derived classes should should set its value(s) based on
        class specific rules.
        """
    
    @abstractmethod
    def get(self, x: int, y: int) -> object:
        """
        Return a new object at (x, y).

        The returned value is not a reference to the pixel stored in the 
        buffer.
        """
    
    @abstractmethod
    def set(self, x: int, y: int, value: object) -> Buffer2D:
        """
        Set the given value at (x, y). 
        
        The value at (x, y) will not be a reference to the argument.
        """

    @overload
    def ansi_24(self) -> str: ...
    @overload
    @deprecated("Use `Scene` instead")
    def ansi_24(self, text_tags: Iterable[TextTag]) -> str: ...
    def ansi_24(self, text_tags: None | Iterable[TextTag] = None) -> str:
        width, height = self.width, self.height
        str_buff = []
        if text_tags:
            text_tags = {tag.starting_position(): tag for tag in text_tags}
            line_wrap = None
            text_tag_iter: Iterator | None = None
            for y in range(height):
                for x in range(width):
                    str_buff.append(self.get_color(x, y).to_ansi_bgd_24())
                    if Vec2i(x, y) in text_tags:
                        text_tag = text_tags[Vec2i(x, y)]
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
        else:
            for y in range(height):
                for x in range(width):
                    str_buff.append(self.get_color(x, y).to_ansi_bgd_24())
                    str_buff.append("  ")
                str_buff.append("\033[0m\n")
        return "".join(str_buff)
    
    def draw(self, shape: "Shape"):
        raise NotImplementedError
    
    def __iadd__(self, other: Buffer2D) -> Buffer2D:
        """
        Add the color of each pixel of another buffer to the current buffer.
        The two buffers must have the same dimensions.
        """
        if self.width != other.width or self.height != other.height:
            raise ValueError("Frame buffer dimensions do not match.")
        width, height = self.width, self.height
        for y in range(height):
            for x in range(width):
                self.add_color(x, y, other.get_color(x, y))
        return self
    
    @deprecated("Use `draw` instead.")
    def draw_line(
            self, a: Vec2i, b: Vec2i, 
            color: Color | None = None,
            msaa: MSAAPattern = MSAAx4
        ) -> None:
        """
        Line color will be default to 
        Color(0.5, 0.5, 0.5, 1.0) if not provided.

        A simple method to add a line to the frame buffer.

        addColor will be used so it is less suitable for performance critical
        application.
        """
        color = color or Color(0.5, 0.5, 0.5, 1.0)
        msaa_weight = 1 / len(msaa) if msaa else None
        width, height = self.width, self.height
        dx = a.x - b.x
        if dx == 0:
            t = 0
        else:
            k = (a.y - b.y) / dx
            if k <= 1.0:
                if a.x < b.x:
                    x_min = a.x if a.x >= 0 else 0
                    x_max = b.x if b.x < width else width - 1
                else:
                    x_min = b.x if b.x >= 0 else 0
                    x_max = a.x if a.x < width else width - 1
                bias = a.y - k * a.x
                for x in range(x_min, x_max + 1):
                    y = round(k * x + bias)
                    if 0 <= y < height:
                        composed_color = self.get_color(x, y) + color
                        alpha = 0.0 if msaa else 1.0
                        for dx, dy in msaa:
                            diff = abs(y + dy - k * (x + dx) - bias)
                            alpha += msaa_weight * (1.0 - diff) if diff < 1.0 else 0.0
                        composed_color.a = alpha
                        self.add_color(x, y, composed_color)
                return
            else:
                t = 1 / k
        if a.y < b.y:
            y_min = a.y if a.y >= 0 else 0
            y_max = b.y if b.y < height else height - 1
        else:
            y_min = b.y if b.y >= 0 else 0
            y_max = a.y if a.y < height else height - 1
        bias = a.x - t * a.y
        for y in range(y_min, y_max + 1):
            x = round(t * y + bias)
            if 0 <= x < width:
                composed_color = self.get_color(x, y) + color
                alpha = 0.0 if msaa else 1.0
                for dx, dy in msaa:
                    diff = abs(x + dx - t*(y + dy) - bias)
                    alpha += msaa_weight * (1.0 - diff) if diff < 1.0 else 0.0
                composed_color.a = alpha
                self.add_color(x, y, composed_color)

    @deprecated("Use `draw` instead.")
    def draw_rect(self, a: Vec2i, b: Vec2i, 
                  fillcolor: Color | bool = False,
                  linecolor: Color | bool = True) -> None:
        """
        Draw a rectangle with the given color.

        If color is False, the rectangle will not be filled.

        If color is True, `fillcolor` will default to Color(0.75, 0.75, 0.0, 0.5)
        and `linecolor` will be default to Color(0.75, 0.75, 0.0, 1.0).

        setColor will be used so it is less suitable for performance critical
        application.
        """
        if fillcolor and isinstance(fillcolor, bool):
            fillcolor = Color(0.75, 0.75, 0.0, 0.5)
        if linecolor and isinstance(linecolor, bool):
            linecolor = Color(0.75, 0.75, 0.0, 1.0)

        width, height = self.width, self.height
        x_min = a.x if a.x < b.x else b.x
        x_max = a.x if a.x > b.x else b.x
        y_min = a.y if a.y < b.y else b.y
        y_max = a.y if a.y > b.y else b.y
        if linecolor:
            for x in range(x_min, x_max + 1):
                if 0 <= x < width:
                    self.add_color(x, y_min, linecolor)
                    self.add_color(x, y_max, linecolor)
            for y in range(y_min, y_max): # not need to + 1
                if 0 <= y < height:
                    self.add_color(x_min, y, linecolor)
                    self.add_color(x_max, y, linecolor)
        if fillcolor:
            for y in range(y_min + 1, y_max):
                for x in range(x_min + 1, x_max):
                    self.add_color(x, y, fillcolor)

    @deprecated("Use `draw` instead.")
    def draw_triangle(self, a: Vec2i, b: Vec2i, c: Vec2i, 
                      fillcolor: Color | bool = False,
                      linecolor: Color | bool = True,
                      msaa: MSAAPattern = MSAAx4) -> None:
        """
        Draw a triangle with the given color.

        If color is False, the triangle will not be filled.

        If color is True, `fillcolor` will default to Color(0.25, 0.75, 0.25, 0.5)
        and `linecolor` will be default to Color(0.25, 0.75, 0.25, 1.0).

        setColor will be used so it is less suitable for performance critical
        application.
        """
        if fillcolor and isinstance(fillcolor, bool):
            fillcolor = Color(0.25, 0.75, 0.25, 0.5)
        if linecolor and isinstance(linecolor, bool):
            linecolor = Color(0.25, 0.75, 0.25, 1.0)

        if fillcolor:
            a, b, c = sorted((a, b, c), key=lambda v: v.y)
            if b.y == c.y:
                b, c = (b, c) if b.x < c.x else (c, b)
                self._fill_triangle_flat(a, b, c, fillcolor, msaa)
            elif a.y == b.y:
                a, b = (a, b) if a.x < b.x else (b, a)
                self._fill_triangle_flat(c, a, b, fillcolor, msaa)
            else:
                x = a.x - (a.y - b.y) * (a.x - c.x) // (a.y - c.y)
                d = Vec2i(x, b.y)
                if b.x < d.x:
                    self._fill_triangle_flat(a, b, d, fillcolor, 
                                             tuple() if linecolor else msaa)
                    self._fill_triangle_flat(c, b, d, fillcolor, 
                                             tuple() if linecolor else msaa)
                else:
                    self._fill_triangle_flat(a, d, b, fillcolor, 
                                             tuple() if linecolor else msaa)
                    self._fill_triangle_flat(c, d, b, fillcolor, 
                                             tuple() if linecolor else msaa)

        if linecolor:
            self.draw_line(a, b, linecolor, msaa)
            self.draw_line(b, c, linecolor, msaa)
            self.draw_line(c, a, linecolor, msaa)
    
    @deprecated("Use `draw` instead.")
    def _fill_triangle_flat(self, a: Vec2i, b: Vec2i,
                            c: Vec2i, fillcolor: Color,
                            msaa: MSAAPattern) -> None:
        """
        Fill a triangle with a flat top or bottom with `fillcolor`.

        `b.y` is expected to be equal to `c.y` and `b.x` is expected to be
        less than or equal to `c.x`. 
        """
        width, height = self.width, self.height
        msaa_weight = 1 / len(msaa) if msaa else None
        if a.y < b.y:
            y_min = a.y if a.y >= 0 else 0
            y_max = b.y if b.y < height else height - 1
        else:
            y_min = b.y if b.y >= 0 else 0
            y_max = a.y if a.y < height else height - 1
        t_left = (a.x - b.x) / (a.y - b.y)
        t_right = (a.x - c.x) / (a.y - c.y)
        b_left = a.x - t_left * a.y
        b_right = a.x - t_right * a.y
        # Going from top to bottom
        for y in range(y_min, y_max):
            x_left = round(t_left * y + b_left)
            x_right = round(t_right * y + b_right)
            x_left = x_left if x_left >= 0 else 0
            x_right = x_right if x_right < width else width - 1
            # Going from the left edge of the triangle to the right edge
            for x in range(x_left + 1, x_right):
                self.add_color(x, y, fillcolor)
            
            composed_color_left = self.get_color(x_left, y) + fillcolor
            composed_color_right = self.get_color(x_right, y) + fillcolor
            alpha_left = 0.0 if msaa else 1.0
            alpha_right = 0.0 if msaa else 1.0
            for dx, dy in msaa:
                diff_left = abs(x_left + dx - t_left*(y + dy) - b_left)
                alpha_left += (msaa_weight * (1.0 - diff_left)
                               if diff_left < 1.0 else 0.0)
                diff_right = abs(x_right + dx - t_right*(y + dy) - b_right)
                alpha_right += (msaa_weight * (1.0 - diff_right)
                               if diff_right < 1.0 else 0.0)
            composed_color_left.a = alpha_left
            composed_color_right.a = alpha_right
            self.add_color(x_left, y, composed_color_left)
            self.add_color(x_right, y, composed_color_right)
