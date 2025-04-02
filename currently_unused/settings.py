

from .constants import BOX_SIZE
from .type_aliases import RGB
from .color_constants import DEFAULT_ANSI_4BIT_RGB, DEFAULT_ANSI_8BIT_RGB, GRAYSCALE_ASCII_10
from .color import get_color_quantization_table, get_grayscale

from os import PathLike
from enum import Enum, auto

    
class DisplaySetting(Enum):
    AsciiGrayscale = auto() 
    ANSI4bit = auto() 
    ANSI8bit = auto() 
    ANSI24bit = auto()


class Settings:
    def __init__(self):
        self.width = None
        self.height = None
        self.display_settings:int = DisplaySetting.AsciiGrayscale
        self._ansi_4bit_rgb = DEFAULT_ANSI_4BIT_RGB
        self._ansi_8bit_rgb = DEFAULT_ANSI_8BIT_RGB
        self.ansi_4bit_lookup:None|bytearray = None
        self.ansi_8bit_lookup:None|bytearray = None
        # Should be set to false if `self._ansi_4bit_rgb` is modified
        self._ansi_4bit_lookup_updated:bool = False
        # Should be set to false if `self._ansi_8bit_rgb` is modified
        self._ansi_8bit_lookup_updated:bool = False
        self._grayscale_ascii_str= GRAYSCALE_ASCII_10
        self.prevent_identical_lines = False
    
    @property
    def ansi_4bit_rgb(self) -> tuple[RGB]:
        return self._ansi_4bit_rgb
    
    @property
    def ansi_8bit_rgb(self) -> tuple[RGB]:
        return self._ansi_8bit_rgb
    

    def update_ansi_4bit_lookup(self, box_size:int = BOX_SIZE, progress_bar_width:int|None=20) -> None:
        self.ansi_4bit_lookup = get_color_quantization_table(
            self._ansi_4bit_rgb, 
            box_size, 
            progress_bar_width
        )
        self._ansi_4bit_lookup_updated:bool = True
    
    def update_ansi_8bit_lookup(self, box_size:int = BOX_SIZE, progress_bar_width:int|None=20) -> None:
        self.ansi_8bit_lookup = get_color_quantization_table(
            self._ansi_8bit_rgb, 
            box_size, 
            progress_bar_width
        )
        self._ansi_8bit_lookup_updated:bool = True

    def write_ansi_4bit_lookup(self, path:PathLike="ansi_4bit_lookup") -> None:
        """
        Store the large `ansi_4bit_lookup` as raw binary file so it can be
        directly loaded next time needed instead of being re-calculated
        """
        with open(path, "wb") as file:
            file.write(self.ansi_4bit_lookup)
    
    def read_ansi_4bit_lookup(self, path:PathLike="ansi_4bit_lookup") -> None:
        """
        Read the large `ansi_4bit_lookup` file so it can be
        directly loaded next time instead of being re-calculated.

        Note that `self._ansi_4bit_lookup_updated` will be set `True` even if
        the loaded table may not match `self._ansi_4bit_rgb`
        """
        with open(path, "rb") as file:
            self.ansi_4bit_lookup = file.read()
        self._ansi_4bit_lookup_updated = True
    
    def write_ansi_8bit_lookup(self, path:PathLike="ansi_8bit_lookup") -> None:
        """
        Store the large `ansi_8bit_lookup` as binary file so it can be
        directly loaded next time needed instead of being re-calculated
        """
        with open(path, "wb") as file:
            file.write(self.ansi_8bit_lookup)
    
    def read_ansi_8bit_lookup(self, path:PathLike="ansi_8bit_lookup") -> None:
        """
        Read the large `ansi_8bit_lookup` file so it can be
        directly loaded next time instead of being re-calculated.

        Note that `self._ansi_8bit_lookup_updated` will be set `True` even if
        the loaded table may not match `self._ansi_8bit_rgb`
        """
        with open(path, "rb") as file:
            self.ansi_8bit_lookup = file.read()
        self._ansi_8bit_lookup_updated = True
    
    def calibrate():
        pass

