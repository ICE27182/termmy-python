

from .color import Color
from .color_constants import DEFAULT_ANSI_8BIT_RGB, DEFAULT_ANSI_4BIT_RGB, GRAYSCALE_ASCII_70
from .color_constants import GRAYSCALE_ASCII_70
from .get_color_quantization_table import get_color_quantization_table
from hashlib import md5
from copy import deepcopy
from os.path import exists, isfile
from typing import Any

CACHE_NAME_PREFIX = "PaletteLookup_"

def palette_hash(palette: tuple[Color]) -> str:
    palette_bytes = b''.join(
        bytes((
            (round(color.r*255.0) if color.r >= 0.0 else 0)
            if color.r <= 1.0 else 255,
            (round(color.g*255.0) if color.g >= 0.0 else 0)
            if color.g <= 1.0 else 255,
            (round(color.b*255.0) if color.b >= 0.0 else 0)
            if color.b <= 1.0 else 255,
        )) for color in palette
    )
    return md5(palette_bytes, usedforsecurity=False).hexdigest()

class ColorQuantizer:
    def __init__(self, palette: tuple[Color], 
                 ensure_lookup_exists: bool = False,
                 write_to_cache: bool = True,
                 progress_bar: None | int = 20):
        """
        Initilizae a color quantizer with a palette of colors. The palette 
        size must be in [1, 256].

        If `ensure_lookup_exists` is True, the lookup table will be computed.

        `write_to_cache` and `progress_bar` are only relevant if the lookup is
        to be computed.
        """
        if not 1 <= len(palette) <= 256:
            raise ValueError("`palette` must have a length between [1, 256].")
        self._palette: tuple[Color] = palette
        self.lookup: bytes | bytearray | None = None
        cache_name = f"{CACHE_NAME_PREFIX}{palette_hash(palette)}"
        if exists(cache_name) and isfile(cache_name):
            with open(cache_name, "rb") as f:
                self.lookup = f.read()
        elif ensure_lookup_exists and not self.lookup:
            self.compute_lookup(write_to_cache, progress_bar)

    @property
    def palette(self) -> tuple[Color]:
        return deepcopy(self._palette)
    @palette.setter
    def palette(self, palette: tuple[Color]) -> None:
        if not 1 <= len(palette) <= 256:
            raise ValueError("`palette` must have a length between [1, 256].")
        self._palette = palette
        self.lookup = None
    
    def compute_lookup(self, write_to_cache: bool = True, 
                       progress_bar: None | int = 20) -> None:
        print("Calculating lookup table for a "
              f"'{self.__class__.__name__}' object.")
        self.lookup = get_color_quantization_table(
            self.palette,
            progress_bar=progress_bar
        )
        if write_to_cache:
            with open(f"{CACHE_NAME_PREFIX}{palette_hash(self.palette)}", "wb") as f:
                f.write(self.lookup)
    
    def quantize(self, color: Color) -> int:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        return self.lookup[(r << 16) + (g << 8) + b]
    
    def quantize_ansi_bgd(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        color = self.palette[self.lookup[(r << 16) + (g << 8) + b]]
        return f"\033[48;2;{color.r};{color.g};{color.b}m"
    def quantize_ansi_txt(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        color = self.palette[self.lookup[(r << 16) + (g << 8) + b]]
        return f"\033[38;2;{color.r};{color.g};{color.b}m"
    def pixel_str(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        color = self.palette[self.lookup[(r << 16) + (g << 8) + b]]
        return f"\033[48;2;{color.r};{color.g};{color.b}m  "
    

class ColorQuantizerANSI256(ColorQuantizer):
    def __init__(self, palette: tuple[Color] | None = None, 
                 ensure_lookup_exists: bool = False,
                 write_to_cache: bool = True,
                 progress_bar: None | int = 20):
        palette = palette or DEFAULT_ANSI_8BIT_RGB
        super().__init__(palette, ensure_lookup_exists,
                         write_to_cache, progress_bar)

    def quantize_ansi_bgd(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        return f"\033[48;5;{self.lookup[(r << 16) + (g << 8) + b]}m"
    
    def quantize_ansi_txt(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        return f"\033[38;5;{self.lookup[(r << 16) + (g << 8) + b]}m"
    
    def pixel_str(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        return f"\033[48;5;{self.lookup[(r << 16) + (g << 8) + b]}m  "


class ColorQuantizerANSI16(ColorQuantizer):
    def __init__(self, palette: tuple[Color] | None = None, 
                 ensure_lookup_exists: bool = False,
                 write_to_cache: bool = True,
                 progress_bar: None | int = 20):
        palette = palette or DEFAULT_ANSI_4BIT_RGB
        super().__init__(palette, ensure_lookup_exists,
                         write_to_cache, progress_bar)

    def quantize_ansi_bgd(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        color_code = self.lookup[(r << 16) + (g << 8) + b]
        color_code = (40+color_code) if color_code < 8 else (100+color_code)
        return f"\033[{color_code}m"
    
    def quantize_ansi_txt(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        color_code = self.lookup[(r << 16) + (g << 8) + b]
        color_code = (30+color_code) if color_code < 8 else (90+color_code)
        return f"\033[{color_code}m"
    
    def pixel_str(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        r, g, b = color.to24bit()
        color_code = self.lookup[(r << 16) + (g << 8) + b]
        color_code = (40+color_code) if color_code < 8 else (92+color_code)
        return f"\033[{color_code}m  "

class ColorQuantizerTextOnly(ColorQuantizer):
    def __init__(self, lookup: str = GRAYSCALE_ASCII_70):
        self.lookup = lookup
    
    @property
    def palette(self) -> tuple[Color]:
        length = len(self.lookup)
        length_reciprocal = 1 / length
        return tuple(Color.from_illuminance(i*length_reciprocal)
                     for i in range(length))
    @palette.setter
    def palette(self, palette: Any) -> None:
        raise NotImplementedError("`palette` cannot be set for "
                                  "`ColorQuantizerTextOnly`. "
                                  "Change `lookup` directly.")
    
    def quantize_ansi_bgd(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        return ""
    
    def quantize_ansi_txt(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        return ""
    
    def pixel_str(self, color: Color) -> str:
        if self.lookup is None:
            raise ValueError("Lookup table not computed. "
                             "Call `compute_lookup` first.")
        return 2*self.lookup[int(len(self.lookup) * color.illuminance())]

