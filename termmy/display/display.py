

from .display_settings import DisplaySettings, ColorMode, ResizeMode
from termmy.colors import Color, ColorQuantizer
from termmy.buffers import Buffer2D
from termmy.buffers.msaa_patterns import *
from termmy.termiohub import TermIOHub

from typing import Any, overload, Callable

@overload
def display(frame_buffer: Buffer2D) -> None: ...
@overload
def display(
    frame_buffer: Buffer2D,
    color_settings: DisplaySettings = DisplaySettings.auto_detecting(),
    go_back_to_top: bool = False,
    tone_mapping: Callable[[float], float] | None = None
) -> None: ...

def display(
    buffer: Buffer2D, 
    display_settings:DisplaySettings = DisplaySettings.auto_detecting(),
    go_back_to_top: bool = False,
    tone_mapping: Callable[[float], float] | None = None,
) -> None:
    """
    `tone_mapping` must be function mapping from [0, 1] -> [0, 1], 
    or IndexError or TypeError may raise
    or the displayed image may not look as expected.
    """
    resize_mode = display_settings.resize_mode
    multisampling = MSAAoff
    horizontal_scalar, vertical_scalar = 1.0, 1.0
    display_width = display_settings.width
    display_height = display_settings.height
    inverse = display_settings.inverse
    gamma_reciprocal = display_settings.gamma_reciprocal
    quantizer = display_settings.quantizer
    buffer_width, buffer_height = buffer.width, buffer.height
    if resize_mode == ResizeMode.CropRight:
        range_of_x = range(display_width if display_width < buffer_width 
                           else buffer_width)
        range_of_y = range(buffer_height)
    elif resize_mode == ResizeMode.CropRightBottom:
        range_of_x = range(display_width if display_width < buffer_width 
                           else buffer_width)
        range_of_y = range(display_height if display_height < buffer_height
                           else buffer_height)
    elif resize_mode == ResizeMode.CropHorizontalCentered:
        half_width_diff = (display_width-buffer_width) / 2
        if half_width_diff >= 0:
            range_of_x = range(buffer_width)
        else:
            range_of_x = range(round(-half_width_diff), 
                               round(buffer_width + half_width_diff))
        range_of_y = range(buffer_height)
    elif resize_mode == ResizeMode.CropCentered:
        half_width_diff = (display_width-buffer_width) / 2
        if half_width_diff >= 0:
            range_of_x = range(buffer_width)
        else:
            range_of_x = range(round(-half_width_diff), 
                               round(buffer_width + half_width_diff))
        half_height_diff = (display_height-buffer_height) / 2
        if half_height_diff >= 0:
            range_of_y = range(buffer_height)
        else:
            range_of_y = range(round(-half_height_diff), 
                               round(buffer_height + half_height_diff))
    elif resize_mode == ResizeMode.Stretch:
        range_of_x = range(display_width)
        range_of_y = range(display_height)
        horizontal_scalar=buffer_width/display_width
        vertical_scalar=buffer_height/display_height
        multisampling = display_settings.multisampling
    elif resize_mode == ResizeMode.Fit:
        display_aspect_ratio = display_width / display_height
        buffer_aspect_ratio = buffer_width / buffer_height
        # Change horizontally
        if buffer_aspect_ratio >= display_aspect_ratio:
            horizontal_scalar = buffer_width / display_width
            vertical_scalar = horizontal_scalar
        # Change vertically
        else:
            vertical_scalar = buffer_height / display_height
            horizontal_scalar = vertical_scalar
        multisampling = display_settings.multisampling
        candidate_display_width = int(buffer.width / horizontal_scalar)
        candidate_display_height = int(buffer.height / vertical_scalar)
        if candidate_display_width < display_width:
            display_width = candidate_display_width
        if candidate_display_height < display_height:
            display_height = candidate_display_height
        range_of_x = range(display_width)
        range_of_y = range(display_height)
    elif resize_mode == ResizeMode.AsIs:
        range_of_x = range(buffer_width)
        range_of_y = range(buffer_height)
    else:
        raise NotImplementedError(f"Resize mode `{resize_mode}` is not supported yet.")
    format_str = "%s" * (range_of_x.stop - range_of_x.start) + ""
    # go_back_to_top is 0 when it is false
    row_num_going_back = go_back_to_top * (range_of_y.stop-range_of_y.start)
    if TermIOHub._active_instance:
        TermIOHub._active_instance.safe_print(
            "\033[?25l" +
            "\033[0m\n".join(
                format_str % tuple(
                    _pixel_color(buffer=buffer,
                                x_display=x_display,
                                y_display=y_display,
                                buffer_width=buffer_width,
                                buffer_height=buffer_height,
                                gamma_reciprocal=gamma_reciprocal,
                                inverse=inverse,
                                quantizer=quantizer,
                                multisampling=multisampling,
                                horizontal_scalar=horizontal_scalar,
                                vertical_scalar=vertical_scalar,
                                tone_mapping=tone_mapping,
                                display_settings=display_settings)
                    for x_display in range_of_x
                )
                for y_display in range_of_y
            ),
            end=f"\033[0m\n{row_num_going_back * "\033[F"}\033[?25h"
        )
    else:
        print(
            "\033[?25l" +
            "\033[0m\n".join(
                format_str % tuple(
                    _pixel_color(buffer=buffer,
                                x_display=x_display,
                                y_display=y_display,
                                buffer_width=buffer_width,
                                buffer_height=buffer_height,
                                gamma_reciprocal=gamma_reciprocal,
                                inverse=inverse,
                                quantizer=quantizer,
                                multisampling=multisampling,
                                horizontal_scalar=horizontal_scalar,
                                vertical_scalar=vertical_scalar,
                                tone_mapping=tone_mapping,
                                display_settings=display_settings)
                    for x_display in range_of_x
                )
                for y_display in range_of_y
            ),
            end=f"\033[0m\n{row_num_going_back * "\033[F"}\033[?25h"
        )

def _pixel_color(
    buffer: Buffer2D,
    x_display: int, 
    y_display: int,
    buffer_width: int,
    buffer_height: int,
    gamma_reciprocal: float,
    inverse: bool,
    quantizer: ColorQuantizer,
    multisampling: MSAAPattern,
    horizontal_scalar: float,
    vertical_scalar: float,
    tone_mapping: Callable[[float], float] | None = None,
    display_settings: DisplaySettings | None = None,
) -> str:
    num_samples = 0
    r, g, b = 0, 0, 0
    for dx, dy in multisampling:
        x_buffer_offset = round((x_display + dx) * horizontal_scalar)
        y_buffer_offset = round((y_display + dy) * vertical_scalar)
        if (0 <= x_buffer_offset < buffer_width
            and 0 <= y_buffer_offset < buffer_height):
            current_color = buffer.get_color(x_buffer_offset, y_buffer_offset)
            r += current_color.r
            g += current_color.g
            b += current_color.b
            num_samples += 1
    if num_samples:
        num_samples_reciprocal = 1 / num_samples
        current_color = Color(r * num_samples_reciprocal,
                              g * num_samples_reciprocal,
                              b * num_samples_reciprocal)
    # No multisampling or no eligible samples
    else:
        current_color: Color = buffer.get_color(
            int(x_display * horizontal_scalar),
            int(y_display * vertical_scalar),
        )
    if tone_mapping:
        current_color.r = tone_mapping(current_color.r)
        current_color.g = tone_mapping(current_color.g)
        current_color.b = tone_mapping(current_color.b)
    if gamma_reciprocal != 1.0:
        current_color.r **= gamma_reciprocal
        current_color.g **= gamma_reciprocal
        current_color.b **= gamma_reciprocal
    if inverse:
        current_color.r = 1 - current_color.r
        current_color.g = 1 - current_color.g
        current_color.b = 1 - current_color.b
    if quantizer:
        return quantizer.pixel_str(current_color)
    else:
        return "\033[48;2;%d;%d;%dm  " % (current_color.to24bit())
