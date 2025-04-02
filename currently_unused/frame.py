 

from .type_aliases import RGB, RGBA, Pos, Pixel
from .argument_checking import validate_width, validate_height
from .color_constants import *
from .text_tag import TextTag
from .color import compose_alpha
from .settings import Settings, DisplaySetting


from collections.abc import Iterable
from abc import ABC, abstractmethod

def _validate_str_tagged_args(display_setting:DisplaySetting, color_quantization_table:str|bytes|None) -> None:
    if (
        display_setting == DisplaySetting.AsciiGrayscale 
        and 
        not isinstance(color_quantization_table, str)
    ):
        raise TypeError(
            "`color_quantization_table` must be a `str` object "
            "when `display_setting` is `DisplaySetting.AsciiGrayscale`"
        )
    elif (
        display_setting == DisplaySetting.ANSI4bit
        or
        display_setting == DisplaySetting.ANSI8bit
    ):
        if not isinstance(color_quantization_table, bytes):
            raise TypeError(
                "`color_quantization_table` must be a `bytes` object "
                "when `display_setting` is `DisplaySetting.ANSI4bit` or "
                "`DisplaySetting.ANSI8bit`"
            )
        elif len(color_quantization_table) != 1 << 24:
            raise ValueError(
                "`color_quantization_table` must be of size 1 << 24"
                "when `display_setting` is `DisplaySetting.ANSI4bit` or "
                "`DisplaySetting.ANSI8bit`"
            )




class Frame(ABC):
    def __init__(self,
                 width:int, 
                 height:int) -> None:
        super().__init__()
        validate_width(width)
        validate_height(height)
        self.width = width
        self.height = height
        self.data:list[Pixel]
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}" +
            f"(width = {self.width}, height {self.height})"
        )
    
    @abstractmethod
    def __getitem__(self, pos:Pos) -> Pixel: pass
    @abstractmethod
    def __setitem__(self, pos:Pos, value: Pixel) -> None: pass

    def _valid_pos(self, pos:Pos) -> bool:
        return (
            len(pos) == 2 and 
            0 <= pos[0] < self.width and 
            0 <= pos[1] < self.height
        )

    def str_tagged(
            self,   
            text_tags:Iterable[TextTag],
            prevent_identical_lines:bool = False,
            display_setting:DisplaySetting = DisplaySetting.ANSI24bit,
            color_quantization_table:str|bytes|None = None
        ) -> str:
        """
        This function is not optimized for performance.

        If two text tags have the same starting position, only one of them 
        will be shown, depending on which one occurs last.

        If two text tags overlaps, the latter one will take dominance after
        it starts.
        """
        def format_pixel_string(
            pixel_color:RGB, 
            text:str, 
            text_color:RGB|None) -> str:
            """
            Used in `set_pixel`

            Form the str object to be added to `line` from
            the arguments. 

            How the string is formed depends on `display_setting`
            """
            # Grayscale, no text color composition
            if display_setting == DisplaySetting.AsciiGrayscale:
                return (
                    text if text != "  " 
                    else int(
                        grayscale_mapping_coef * (
                                0.299 * pixel_color[0] + 
                                0.587 * pixel_color[1] + 
                                0.114 * pixel_color[2]
                        )
                    )
                )
            # Text color composition
            if text_color:
                text_color = compose_alpha(pixel_color, text_color)
            # 24-bit
            if display_setting == DisplaySetting.ANSI24bit:
                if text_color:
                    return (
                        f"\033[38;2;{text_color[0]};" +
                        f"{text_color[1]};{text_color[2]}m" +
                        f"\033[48;2;{pixel_color[0]};" +
                        f"{pixel_color[1]};{pixel_color[2]}m" +
                        text
                    )
                else:
                    return (
                        f"\033[48;2;{pixel_color[0]};" +
                        f"{pixel_color[1]};{pixel_color[2]}m" +
                        text
                    )
            # 4-bit or 8-bit: Quantization
            pixel_color_code = color_quantization_table[
                pixel_color[0] + 
                (pixel_color[1] << 8) + 
                (pixel_color[2] << 16)
            ]
            if text_color:
                text_color_code = color_quantization_table[
                    text_color[0] + 
                    (text_color[1] << 8) + 
                    (text_color[2] << 16)
                ]
            if display_setting == DisplaySetting.ANSI4bit:
                if text_color:
                    return (
                        f"\033[{30 + text_color_code}m" +
                        f"\033[{40 + pixel_color_code}m" +
                        text
                    )
                else:
                    return (
                        f"\033[{40 + pixel_color_code}m" + text
                    )
            elif display_setting == DisplaySetting.ANSI8bit:
                if text_color:
                    return (
                        f"\033[38;5;{text_color_code}m" +
                        f"\033[48;5;{pixel_color_code}m" +
                        text
                    )
                else:
                    return (
                        f"\033[48;5;{pixel_color_code}m" + text
                    )
        
        def set_pixel(
                active_text_tag:TextTag|None, 
                written_char_count:int) -> tuple[TextTag|None, int]:
            """
            Sets pixel value at `self.data[row_starting_index + x]` to `line`
            
            Works with `pixel_color`, `text_color` and `text`. 
            Called for each pixel in the frame

            Returns the updated `active_text_tag`, `written_char_count`
            """
            # Starting of a text tag
            if (x, y) in text_tags.keys():
                # `written_char_count` is reset because two text tags can
                # overlap, which means this variable is not necessarily 0
                # when a new text tag is encountered
                active_text_tag, written_char_count = text_tags[(x, y)], 0
            # Pixel Color
            pixel_color = self.data[row_starting_index + x]
            text_color, text = None, "  "
            if active_text_tag is not None:
                # Text color
                if active_text_tag.color is not None:
                    text_color = compose_alpha(
                            pixel_color, 
                            active_text_tag.color
                        )
                # Text
                text = active_text_tag.text[
                    written_char_count : written_char_count + 2
                ]
                written_char_count += 2
                # All text finishes writing
                if (written_char_count == len(active_text_tag.text)):
                    active_text_tag, written_char_count = None, 0
            line.append(format_pixel_string(pixel_color, text, text_color))
            return active_text_tag, written_char_count

        # Argument Checks
        _validate_str_tagged_args(display_setting, color_quantization_table)
        # Stores output
        lines:list[str] = []
        # Transform text_tag to facilitate the later process
        text_tags = {
            text_tag.get_text_tag_that_fits().starting_position()
            : 
            text_tag.get_text_tag_that_fits()
            for text_tag in text_tags
        }
        if display_setting == DisplaySetting.AsciiGrayscale:
            grayscale_mapping_coef = len(color_quantization_table) / 255
        # The text tag in `text_tags` that is currently being written
        active_text_tag:TextTag = None
        # The number of characters in `active_text_tag` that have been written
        written_char_count:int = 0
        for y in range(self.height):
            line = []
            # Discard the current text tag if it disables line wrapping
            if active_text_tag and  not active_text_tag.line_wrap:
                active_text_tag, written_char_count = None, 0
            # Optimization for indexing pixel
            row_starting_index = y * self.width
            for x in range(self.width):
                active_text_tag, written_char_count = set_pixel(
                    active_text_tag, written_char_count
                )
            if prevent_identical_lines and y & 1:
                line.append(f" {CLEAR_COLOR}\n")
            else:
                line.append(f"{CLEAR_COLOR}\n")
            lines.append("".join(line))

        return "".join(lines)

    def str_ansi_24bit(self, prevent_identical_lines:bool = False) -> str:
        """
        Fastest. Does not support inline text
        """
        # Using a list to accumulate lines
        lines = []
        
        for y in range(self.height):
            row_pixels = self.data[y * self.width:(y + 1) * self.width]
            # Use list comprehension for efficiency
            row_str = "".join(
                f"\033[48;2;{pixel[0]};{pixel[1]};{pixel[2]}m  " 
                for pixel in row_pixels
            )
            # Add nextline
            if prevent_identical_lines and y ^ 1:
                lines.append(row_str + f"{CLEAR_COLOR} \n")
            else:
                lines.append(row_str + f"{CLEAR_COLOR}\n")
        
        # Append newline after each row and join
        return "".join(lines) + f"{CLEAR_COLOR}\n"
    
    def str_ansi_4bit(self, prevent_identical_lines:bool = False) -> str:
        pass
    
    def str_ansi_8bit(self, prevent_identical_lines:bool = False) -> str:
        pass

    def str_ascii_grayscale(self, prevent_identical_lines:bool = False) -> str:
        pass
    
    def display():
        pass
    


class Frame24(Frame):
    __slots__ = ["data", "width", "height", ]
    
    def __init__(self,
                 width:int, 
                 height:int, 
                 settings:Settings = None,
                 data:list[RGB] = None,
                 default_color:RGB = (0, 0, 0),
    ) -> None:
        """
        `settings` only affects how the frame will be disp
        """
        super().__init__(width, height)
        self.settings = settings or Settings()
        if data is None:
            data = [default_color] * (width * height)
        self.data:list[RGB] = data

    def __getitem__(self, pos:Pos) -> RGB:
        """
        An interface to get pixel data, with bound checking.

        Use self.data directly if performance is of concern
        """
        if not self._valid_pos(pos):
            raise ValueError(f"Invalid position {pos}.")
        return self.data[pos[1] * self.width + pos[0]]
    
    def __setitem__(self, pos:Pos, value: Pixel) -> None:
        """
        An interface to set pixel data, with bound checking and type checking

        Use self.data directly if performance is of concern
        """
        if not self._valid_pos(pos):
            raise ValueError(f"Invalid position {pos}.")
        if not isinstance(value, Pixel):
            raise TypeError(f"Invalid value type")
    
    

    