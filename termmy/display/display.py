

from .display_settings import DisplaySettings, ColorMode, ResizeMode
from termmy.colors import Color, ColorQuantizer
from termmy.buffers import Buffer2D
from termmy.buffers.msaa_patterns import *

from typing import Any, overload, Callable

@overload
def display(frame_buffer: Buffer2D): ...
@overload
def display(frame_buffer: Buffer2D,
            color_settings: DisplaySettings = DisplaySettings.auto_detecting(),
            go_back_to_top: bool = False,
            color_map: Callable[[float], float] | None = None): ...

def display(
    buffer: Buffer2D, 
    display_settings:DisplaySettings = DisplaySettings.auto_detecting(),
    go_back_to_top: bool = False,
    color_map: Callable[[float], float] | None = None,
) -> None:
    """
    `color_map` must be function mapping from [0, 1] -> [0, 1], 
    or IndexError may raise or the displayed image may not look as expected.
    """
    quantizer = display_settings.quantizer
    resize_mode = display_settings.resize_mode
    display_width = display_settings.width
    display_height = display_settings.height
    if not color_map and _ansi_24(buffer, quantizer, resize_mode, 
                                  display_settings.width,
                                  display_settings.height, 
                                  go_back_to_top):
        return
    if resize_mode == ResizeMode.AsIs:
        _color_cropped(buffer=buffer, 
                       quantizer=quantizer, 
                       range_of_x=range(buffer.width), 
                       range_of_y=range(buffer.height), 
                       go_back_to_top=go_back_to_top,
                       color_map=color_map)
    elif resize_mode == ResizeMode.CropRight:
        _color_cropped(buffer=buffer, 
                       quantizer=quantizer, 
                       range_of_x=range(buffer.width 
                                        if buffer.width <= display_width
                                        else display_width), 
                       range_of_y=range(buffer.height), 
                       go_back_to_top=go_back_to_top)
    elif resize_mode == ResizeMode.CropRightBottom:
        _color_cropped(buffer=buffer, 
                       quantizer=quantizer, 
                       range_of_x=range(buffer.width 
                                        if buffer.width <= display_width
                                        else display_width), 
                       range_of_y=range(buffer.height 
                                        if buffer.height <= display_height
                                        else display_height), 
                       go_back_to_top=go_back_to_top,
                       color_map=color_map)
    elif resize_mode == ResizeMode.CropHorizontalCentered:
        half_width_diff = (display_width-buffer.width) / 2
        if half_width_diff >= 0:
            range_of_x = range(buffer.width)
        else:
            range_of_x = range(round(-half_width_diff), 
                            round(buffer.width + half_width_diff))
        _color_cropped(buffer=buffer, 
                       quantizer=quantizer, 
                       range_of_x=range_of_x, 
                       range_of_y=range(buffer.height), 
                       go_back_to_top=go_back_to_top,
                       color_map=color_map)
    elif resize_mode == ResizeMode.CropCentered:
        half_width_diff = (display_width-buffer.width) / 2
        if half_width_diff >= 0:
            range_of_x = range(buffer.width)
        else:
            range_of_x = range(round(-half_width_diff), 
                            round(buffer.width + half_width_diff))
        half_height_diff = (display_height-buffer.height) / 2
        if half_height_diff >= 0:
            range_of_y = range(buffer.height)
        else:
            range_of_y = range(round(-half_height_diff), 
                            round(buffer.height + half_height_diff))
        _color_cropped(buffer=buffer, 
                       quantizer=quantizer, 
                       range_of_x=range_of_x, 
                       range_of_y=range_of_y, 
                       go_back_to_top=go_back_to_top,
                       color_map=color_map)
    elif resize_mode == ResizeMode.Stretch:
        _color_scaled(buffer=buffer,
                      quantizer=quantizer,
                      display_width=display_width,
                      display_height=display_height,
                      horizontal_scalar=buffer.width/display_width,
                      vertical_scalar=buffer.height/display_height,
                      go_back_to_top=go_back_to_top,
                      multi_sampling=display_settings.multisampling,
                      color_map=color_map)
    elif resize_mode == ResizeMode.Fit:
        display_aspect_ratio = display_width / display_height
        buffer_aspect_ratio = buffer.width / buffer.height
        # Change horizontally
        if buffer_aspect_ratio >= display_aspect_ratio:
            horizontal_scalar = buffer.width / display_width
            vertical_scalar = horizontal_scalar
        # Change vertically
        else:
            vertical_scalar = buffer.height / display_height
            horizontal_scalar = vertical_scalar

        _color_scaled(buffer=buffer,
                      quantizer=quantizer,
                      display_width=display_width,
                      display_height=display_height,
                      horizontal_scalar=horizontal_scalar,
                      vertical_scalar=vertical_scalar,
                      go_back_to_top=go_back_to_top,
                      multi_sampling=display_settings.multisampling,
                      color_map=color_map)
    else:
        raise NotImplementedError(f"Resize mode '{resize_mode}' "
                                  "is not supported yet.")



def _ansi_24(buffer: Buffer2D, 
             quantizer: ColorQuantizer | None,
             resize_mode: ResizeMode,
             display_width: int,
             display_height: int,
             go_back_to_top: bool) -> bool:
    """
    A buffer specifc, potentially more efficient method will be used
    under correct circumstances.

    Returns True if this method is used and there is no need to fallback to
    the more general implementations.

    Return False if nothing is done in this function.
    """
    use_ansi_24 = False
    if not quantizer:
        if resize_mode == ResizeMode.AsIs:
            use_ansi_24 = True
        elif buffer.width == display_width:
            if resize_mode in (ResizeMode.CropRight, 
                               ResizeMode.CropRightBottom):
                use_ansi_24 = True
            elif buffer.height == display_height:
                use_ansi_24 = True
    if use_ansi_24:
        print(buffer.ansi_24())
        if go_back_to_top:
            print("\033[F"*(buffer.height + 1), end="")
    return use_ansi_24

def _color_cropped(buffer: Buffer2D, quantizer: ColorQuantizer | None,
                   range_of_x: range, range_of_y: range, 
                   go_back_to_top: bool, 
                   color_map: Callable[[float], float] | None = None) -> None:
    # The step will always be 1, 
    # so there is no need to divide the length by it
    # It also applies to `row_num`
    format_str = "%s" * (range_of_x.stop - range_of_x.start)
    if quantizer:
        print(
            "\033[0m\n".join(
                format_str % tuple(
                    quantizer.pixel_str(buffer.get_color(x, y))
                    for x in range_of_x
                )
                for y in range_of_y
            )
            if not color_map else
            "\033[0m\n".join(
                format_str % tuple(
                    quantizer.pixel_str(buffer.get_color(x, y).map(color_map))
                    for x in range_of_x
                )
                for y in range_of_y
            )
        )
    else:
        print(
            "\033[0m\n".join(
                format_str % tuple(
                    f"{buffer.get_color(x, y).to_ansi_bgd_24()}  "
                    for x in range_of_x
                )
                for y in range_of_y
            )
            if not color_map else
            "\033[0m\n".join(
                format_str % tuple(
                    f"{buffer.get_color(x, y)
                             .map(color_map)
                             .to_ansi_bgd_24()}  "
                    for x in range_of_x
                )
                for y in range_of_y
            )
        )
    if go_back_to_top:
        row_num = range_of_y.stop - range_of_y.start
        print("\033[F" * (row_num + 1), end = "")

def _color_scaled(buffer: Buffer2D, 
                  quantizer: ColorQuantizer | None,
                  display_width: range, 
                  display_height: range, 
                  horizontal_scalar: float, 
                  vertical_scalar: float,
                  go_back_to_top: bool,
                  multi_sampling: MSAAPattern,
                  color_map: Callable[[float], float] | None = None) -> None:
    """
    horizontal_scalar * resultin_x = buffer_x
    """
    # The logic for checking quantizer is moved into the loops for the
    # clarity of the code.
    candidate_display_width = int(buffer.width / horizontal_scalar)
    candidate_display_height = int(buffer.height / vertical_scalar)
    if candidate_display_width < display_width:
        display_width = candidate_display_width
    if candidate_display_height < display_height:
        display_height = candidate_display_height
    format_str = "%s" * display_width
    if (not multi_sampling 
        or buffer.width == display_width and buffer.height == display_height):
        print(
            "\033[0m\n".join(
                format_str % tuple(
                    (
                        quantizer.pixel_str(
                            buffer.get_color(int(vertical_scalar * x), 
                                             int(horizontal_scalar * y))
                        )
                        if quantizer else 
                        f"{buffer.get_color(int(vertical_scalar * x), 
                                            int(horizontal_scalar * y)
                           ).to_ansi_bgd_24()}  "
                    )
                    for x in range(display_width)
                )
                for y in range(display_height)
            )
            if not color_map else
            "\033[0m\n".join(
                format_str % tuple(
                    (
                        quantizer.pixel_str(
                            buffer.get_color(int(vertical_scalar * x), 
                                             int(horizontal_scalar * y))
                                  .map(color_map)
                        )
                        if quantizer else 
                        f"{buffer.get_color(int(vertical_scalar * x), 
                                            int(horizontal_scalar * y)
                           ).to_ansi_bgd_24()}  "
                    )
                    for x in range(display_width)
                )
                for y in range(display_height)
            )
        )
    else:
        str_buf = []
        buffer_width, buffer_height = buffer.width, buffer.height
        for y in range(display_height):
            for x in range(display_width):
                current_color = Color(0, 0, 0)
                sample_num = 0.0
                for dx, dy in multi_sampling:
                    buffer_x = round(horizontal_scalar * (x + dx))
                    buffer_y = round(vertical_scalar * (y + dy))
                    if (0 <= buffer_x < buffer_width 
                        and 0 <= buffer_y < buffer_height):
                        color = buffer.get_color(buffer_x, buffer_y)
                        current_color.r += color.r
                        current_color.g += color.g
                        current_color.b += color.b
                        sample_num += 1.0
                if sample_num:
                    sample_num_reciprocal = 1.0 / sample_num
                    current_color.r *= sample_num_reciprocal
                    current_color.g *= sample_num_reciprocal
                    current_color.b *= sample_num_reciprocal
                else:
                    current_color = buffer.get_color(
                        int(horizontal_scalar * x),
                        int(vertical_scalar * y),
                    )
                if color_map:
                    current_color.r = color_map(current_color.r)
                    current_color.g = color_map(current_color.g)
                    current_color.b = color_map(current_color.b)
                str_buf.append(
                    quantizer.pixel_str(current_color)
                    if quantizer 
                    else f"{current_color.to_ansi_bgd_24()}  "
                )
            str_buf.append("\033[0m\n")
        print("".join(str_buf))

    if go_back_to_top:
        print("\033[F" * (display_height + 1), end = "")
