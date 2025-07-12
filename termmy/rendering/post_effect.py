

from .render_context import RenderContext
from ..colors import Color
from ..buffers import ColorBuffer
from ..graphics import Scene, Node, Dithering

from dataclasses import dataclass
from typing import Callable

class PostEffect:
    fxaa: bool = True
    fxaa_threshold: float = 0.15
    
    dithering: Dithering | None = None
    
    invert: bool = False
    gamma: float = 1.0
    exposure: float = 1.0
    grayscale: bool = False

    color_filter: Callable[[Color], Color] | None = None

    def apply(self, render_context: RenderContext) -> ColorBuffer:
        """
        
        The alpha channel after applying this method should be discarded.

        A new scratch buffer will be created in `render_context` if it is
        None and FXAA is used.

        Returns:
            ColorBuffer: A reference to the color buffer in `render_context`.
        
        Raises:
            ValueError: If the `scratch_buffer` is provided but its demension
                does not match the target dimension.
        """
        width, height = render_context.width, render_context.height
        if self.fxaa:
            scratch_buffer = render_context.scratch_buffer
            if scratch_buffer is None:
                scratch_buffer = ColorBuffer(width, height)
                render_context.scratch_buffer = scratch_buffer
            elif scratch_buffer.width != width or scratch_buffer.height != height:
                raise ValueError("`scratch_buffer` is provided but its demension "
                                f"{scratch_buffer.width}x{scratch_buffer.height} "
                                "does not match the target dimension "
                                f"{width}x{height}.")
            scratch_buffer = render_context.scratch_buffer
            _with_fxaa(render_context, self.dithering, 
                       self.invert, self.gamma, self.exposure, 
                       self.grayscale, self.color_filter, 
                       self.fxaa_threshold)
        else:
            _without_fxaa(render_context, self.dithering, 
                          self.invert, self.gamma, self.exposure, 
                          self.grayscale, self.color_filter)


def _without_fxaa(
    render_context: RenderContext,
    dithering: Dithering | None,
    invert: bool,
    gamma: float,
    exposure: float,
    grayscale: bool,
    color_filter: Callable[[Color], Color] | None,
) -> ColorBuffer:
    buffer = render_context.color_buffer
    width, height = render_context.width, render_context.height
    data = buffer.data
    for y, row_starting in zip(range(height), range(0, height*width, width)):
        for x in range(width):
            color = data[row_starting + x]
            if color_filter:
                new_color = color_filter(color)
                color.r = new_color.r
                color.g = new_color.g
                color.b = new_color.b
            if gamma != 1.0:
                color.r = pow(color.r, 1 / gamma)
                color.g = pow(color.g, 1 / gamma)
                color.b = pow(color.b, 1 / gamma)
            if exposure != 1.0:
                color.r *= exposure
                color.g *= exposure
                color.b *= exposure
            if invert:
                color.r = 1.0 - color.r
                color.g = 1.0 - color.g
                color.b = 1.0 - color.b
            if grayscale:
                luminance = 0.3 * color.r + 0.59 * color.g + 0.11 * color.b
                color.r = color.g = color.b = luminance
            if dithering:
                new_color = dithering.dithered_color(buffer, x, y)
                color.r = new_color.r
                color.g = new_color.g
                color.b = new_color.b
    return buffer


def _with_fxaa(
    render_context: RenderContext,
    dithering: Dithering | None,
    invert: bool,
    gamma: float,
    exposure: float,
    grayscale: bool,
    color_filter: Callable[[Color], Color] | None,
    threshold: float,
) -> ColorBuffer:
    buffer = render_context.color_buffer
    scratch_buffer = render_context.scratch_buffer
    width, height = render_context.width, render_context.height
    data = buffer.data
    scratch_data = scratch_buffer.data
    luminance_map = [0.299 * c.r + 0.587 * c.g + 0.114 * c.b for c in data]
    
    for y, row_starting in zip(range(height), 
                               range(width, width * (height - 1), width)):
        last_row_starting = row_starting - width
        next_row_starting = row_starting + width
        for x in range(1, width - 1):
            # Calculate the indices for buffer.data and luminance_map
            current = row_starting + x
            north = last_row_starting + x
            south = next_row_starting + x
            west = current - 1
            east = current + 1
            nw = north - 1
            ne = north + 1
            sw = south - 1
            se = south + 1
            # Edge & direction detection
            to_be_blended: list[Color] = [data[current]]
            if abs(luminance_map[north] - luminance_map[south]) > threshold:
                to_be_blended.extend((data[north], data[south]))
            if abs(luminance_map[west] - luminance_map[east]) > threshold:
                to_be_blended.extend((data[west], data[east]))
            if abs(luminance_map[nw] - luminance_map[se]) > threshold:
                to_be_blended.extend((data[nw], data[se]))
            if abs(luminance_map[ne] - luminance_map[sw]) > threshold:
                to_be_blended.extend((data[ne], data[sw]))
            # Blending
            coef = 1 / len(to_be_blended)
            color = scratch_data[current]
            color.r = sum(color.r for color in to_be_blended) * coef
            color.g = sum(color.g for color in to_be_blended) * coef
            color.b = sum(color.b for color in to_be_blended) * coef
            # Other passes
            if color_filter:
                new_color = color_filter(color)
                color.r = new_color.r
                color.g = new_color.g
                color.b = new_color.b
            if gamma != 1.0:
                color.r = pow(color.r, 1 / gamma)
                color.g = pow(color.g, 1 / gamma)
                color.b = pow(color.b, 1 / gamma)
            if exposure != 1.0:
                color.r *= exposure
                color.g *= exposure
                color.b *= exposure
            if invert:
                color.r = 1.0 - color.r
                color.g = 1.0 - color.g
                color.b = 1.0 - color.b
            if grayscale:
                luminance = 0.3 * color.r + 0.59 * color.g + 0.11 * color.b
                color.r = color.g = color.b = luminance
            if dithering:
                new_color = dithering.dithered_color(buffer, x, y)
                color.r = new_color.r
                color.g = new_color.g
                color.b = new_color.b
    # The first and last rows
    last_y = height - 1
    last_row_starting = width * (height - 1)
    for x in range(width):
        # Top
        color_t = scratch_data[x]
        original_color_top = data[x]
        color_t.r = original_color_top.r
        color_t.g = original_color_top.g
        color_t.b = original_color_top.b
        # Bottom
        color_b = scratch_data[x + last_row_starting]
        original_color_bottom = data[x + last_row_starting]
        color_b.r = original_color_bottom.r
        color_b.g = original_color_bottom.g
        color_b.b = original_color_bottom.b
        # Other passes
        if color_filter:
            new_color_t = color_filter(color_t)
            color_t.r = new_color_t.r
            color_t.g = new_color_t.g
            color_t.b = new_color_t.b
            new_color_b = color_filter(color_b)
            color_b.r = new_color_b.r
            color_b.g = new_color_b.g
            color_b.b = new_color_b.b
        if gamma != 1.0:
            color_t.r = pow(color_t.r, 1 / gamma)
            color_t.g = pow(color_t.g, 1 / gamma)
            color_t.b = pow(color_t.b, 1 / gamma)
            color_b.r = pow(color_b.r, 1 / gamma)
            color_b.g = pow(color_b.g, 1 / gamma)
            color_b.b = pow(color_b.b, 1 / gamma)
        if exposure != 1.0:
            color_t.r *= exposure
            color_t.g *= exposure
            color_t.b *= exposure
            color_b.r *= exposure
            color_b.g *= exposure
            color_b.b *= exposure
        if invert:
            color_t.r = 1.0 - color_t.r
            color_t.g = 1.0 - color_t.g
            color_t.b = 1.0 - color_t.b
            color_b.r = 1.0 - color_b.r
            color_b.g = 1.0 - color_b.g
            color_b.b = 1.0 - color_b.b
        if grayscale:
            luminance_t = 0.3 * color_t.r + 0.59 * color_t.g + 0.11 * color_t.b
            color_t.r = color_t.g = color_t.b = luminance_t
            luminance_b = 0.3 * color_b.r + 0.59 * color_b.g + 0.11 * color_b.b
            color_b.r = color_b.g = color_b.b = luminance_b
        if dithering:
            new_color_t = dithering.dithered_color(buffer, x, 0)
            color_t.r = new_color_t.r
            color_t.g = new_color_t.g
            color_t.b = new_color_t.b
            new_color_b = dithering.dithered_color(buffer, x, last_y)
            color_b.r = new_color_b.r
            color_b.g = new_color_b.g
            color_b.b = new_color_b.b
    # The first and last columns
    last_x = width - 1
    for y, row_starting in zip(range(height), 
                               range(0, width * height, width)):
        # Left
        color_l = scratch_data[row_starting]
        original_color_left = data[row_starting]
        color_l.r = original_color_left.r
        color_l.g = original_color_left.g
        color_l.b = original_color_left.b
        # Right
        color_r = scratch_data[row_starting + last_x]
        original_color_right = data[row_starting + last_x]
        color_r.r = original_color_right.r
        color_r.g = original_color_right.g
        color_r.b = original_color_right.b
        # Other passes
        if color_filter:
            new_color_l = color_filter(color_l)
            color_l.r = new_color_l.r
            color_l.g = new_color_l.g
            color_l.b = new_color_l.b
            new_color_r = color_filter(color_r)
            color_r.r = new_color_r.r
            color_r.g = new_color_r.g
            color_r.b = new_color_r.b
        if gamma != 1.0:
            color_l.r = pow(color_l.r, 1 / gamma)
            color_l.g = pow(color_l.g, 1 / gamma)
            color_l.b = pow(color_l.b, 1 / gamma)
            color_r.r = pow(color_r.r, 1 / gamma)
            color_r.g = pow(color_r.g, 1 / gamma)
            color_r.b = pow(color_r.b, 1 / gamma)
        if exposure != 1.0:
            color_l.r *= exposure
            color_l.g *= exposure
            color_l.b *= exposure
            color_r.r *= exposure
            color_r.g *= exposure
            color_r.b *= exposure
        if invert:
            color_l.r = 1.0 - color_l.r
            color_l.g = 1.0 - color_l.g
            color_l.b = 1.0 - color_l.b
            color_r.r = 1.0 - color_r.r
            color_r.g = 1.0 - color_r.g
            color_r.b = 1.0 - color_r.b
        if grayscale:
            luminance_l = 0.3 * color_l.r + 0.59 * color_l.g + 0.11 * color_l.b
            color_l.r = color_l.g = color_l.b = luminance_l
            luminance_r = 0.3 * color_r.r + 0.59 * color_r.g + 0.11 * color_r.b
            color_r.r = color_r.g = color_r.b = luminance_r
        if dithering:
            new_color_l = dithering.dithered_color(buffer, 0, y)
            color_l.r = new_color_l.r
            color_l.g = new_color_l.g
            color_l.b = new_color_l.b
            new_color_r = dithering.dithered_color(buffer, last_x, y)
            color_r.r = new_color_r.r
            color_r.g = new_color_r.g
            color_r.b = new_color_r.b
    # Swap the data in `scratch_buffer` and `buffer`
    scratch_buffer.data, buffer.data = buffer.data, scratch_buffer.data
    return buffer
