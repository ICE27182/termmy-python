

from __future__ import annotations

from termmy.colors import ColorQuantizerANSI256, ColorQuantizerANSI16
from termmy.colors import ColorQuantizerTextOnly, ColorQuantizer
from termmy.buffers.msaa_patterns import *

from dataclasses import dataclass
from enum import StrEnum, auto
from os import getenv, PathLike
from os.path import exists
from sys import platform
from shutil import get_terminal_size

class ColorMode(StrEnum):
    ANSI24b = auto()
    ANSI256 = auto()
    ANSI16 = auto()
    TextOnly = auto()
    def supports(self, other: ColorMode) -> bool:
        if not isinstance(other, ColorMode):
            raise TypeError("Comparison not supported between ColorMode and "
                            f"{type(other)}.")
        if self == ColorMode.ANSI24b:
            return False
        elif self == ColorMode.ANSI256:
            return other == ColorMode.ANSI24b
        elif self == ColorMode.ANSI16:
            return (other == ColorMode.ANSI24b
                    or other == ColorMode.ANSI256)
        elif self == ColorMode.TextOnly:
            return other != ColorMode.TextOnly


class ResizeMode(StrEnum):
    AsIs = auto()
    CropRight = auto() # width = min(widths)
    CropRightBottom = auto() # width, height = min(widths), min(heights)
    CropCentered = auto() # width = min(widths); for x in range_of_x
    CropHorizontalCentered = auto() # w, h = min(w_s), min(h_s); range_of_x&y
    Stretch = auto()
    Fit = auto()

@dataclass(slots=True)
class DisplaySettings:
    terminal_color_support: ColorMode
    quantizer: ColorQuantizer | None = None
    width: int = None
    height: int = None
    resize_mode: ResizeMode = ResizeMode.AsIs
    multisampling: MSAAPattern = MSAAx4

    @classmethod
    def auto_detecting(cls,
                       resize_mode: ResizeMode = ResizeMode.Fit,
                       column_padding: int = 4,
                       row_padding: int = 4,
                       ensure_lookup_exsits: bool = False,
                       write_to_cache: bool = True,
                       progress_bar: None | int = 20) -> DisplaySettings:
        """
        Try to automatically detect the terminal envrionment. The result may
        be unreliable. 

        Call `calibrate` if there is any color-related abnormality.

        `write_to_cache` and `progress_bar` are only relevant when 
        `ensure_lookup_exsits` is True and the lookup table needs to be
        calculated.
        """
        # Color mode detection
        terminal_color_support = ColorMode.ANSI24b
        if platform == "win32":
            if getenv("WT_SESSION") is None:
                terminal_color_support = ColorMode.TextOnly
        elif (platform == "darwin" 
              and getenv("TERM_PROGRAM") == "Apple_Terminal"):
            terminal_color_support = ColorMode.ANSI256
        out = cls(terminal_color_support=terminal_color_support, 
                  resize_mode=resize_mode)
        # Set color quantizer
        if terminal_color_support == ColorMode.ANSI24b:
            out.quantizer = None
        elif terminal_color_support == ColorMode.ANSI256:
            out.quantizer = ColorQuantizerANSI256(
                ensure_lookup_exists=ensure_lookup_exsits,
                write_to_cache=write_to_cache,
                progress_bar=progress_bar,
            )
        elif terminal_color_support == ColorMode.ANSI16:
            out.quantizer = ColorQuantizerANSI16(
                ensure_lookup_exists=ensure_lookup_exsits,
                write_to_cache=write_to_cache,
                progress_bar=progress_bar,
            )
        else:
            out.quantizer = ColorQuantizerTextOnly()
        # Set width and height
        cols, rows = get_terminal_size()
        out.width, out.height = (cols - column_padding) // 2, rows - row_padding
        return out
    
    def set_color_mode(self, color_mode: ColorMode, 
                       quantizer: ColorQuantizer | None = None, 
                       ensure_lookup_exists: bool = False):
        """
        Set color mode.

        Raise a TypeError if the quantizer does not fit the color mode.

        Raise a ValueError if the color mode is not supported according to
        `self.terminal_color_support`.

        Set quantizer to quantizer if `color_mode` equals `ColorMode.ANSI24b`.

        Set quantizer to `ColorQuantizerANSI256` if `color_mode` equals 
        `ColorMode.ANSI256` if quantizer is not provided. If quantizer is
        provided, and the quantizer is supported in the given color mode,
        set `self.quantizer` to `quantizer`.

        Set quantizer to `ColorQuantizerANSI16` if `color_mode` equals 
        `ColorMode.ANSI16` if quantizer is not provided. If quantizer is
        provided, and the quantizer is supported in the given color mode,
        set `self.quantizer` to `quantizer`.

        Set quantizer to `ColorQuantizerTextOnly` if `color_mode` equals 
        `ColorMode.TextOnly` if quantizer is not provided. If quantizer is
        provided, and the quantizer is supported in the given color mode,
        set `self.quantizer` to `quantizer`.
        """
        if self.terminal_color_support.supports(color_mode):
            raise ValueError(f"`{color_mode.name}` may not be supported by the "
                             "terminal with `terminal_color_support` set as "
                             f"`{self.terminal_color_support}`.")
        if color_mode == ColorMode.ANSI24b:
            self.quantizer = quantizer
        elif color_mode == ColorMode.ANSI256:
            if quantizer and not isinstance(quantizer, 
                                            (ColorQuantizerANSI256,
                                             ColorQuantizerANSI16,
                                             ColorQuantizerTextOnly)):
                raise TypeError(f"'{quantizer.__class__.__name__}' is not "
                                "supported in the given color mode.")
            self.quantizer = quantizer or ColorQuantizerANSI256(
                ensure_lookup_exists=ensure_lookup_exists,
            )
        elif color_mode == ColorMode.ANSI16:
            if quantizer and not isinstance(quantizer, 
                                            (ColorQuantizerANSI16,
                                             ColorQuantizerTextOnly)):
                raise TypeError(f"'{quantizer.__class__.__name__}' is not "
                                "supported in the given color mode.")
            self.quantizer = quantizer or ColorQuantizerANSI16(
                ensure_lookup_exists=ensure_lookup_exists,
            )
        elif color_mode == ColorMode.TextOnly:
            if quantizer and not isinstance(quantizer, 
                                            ColorQuantizerTextOnly):
                raise TypeError(f"'{quantizer.__class__.__name__}' is not "
                                "supported in the given color mode.")
            self.quantizer = quantizer or ColorQuantizerANSI16(
                ensure_lookup_exists=ensure_lookup_exists,
            )
        else:
            raise ValueError(f"Unknown Color Mode `{color_mode.name}`")
        
    def calibrate() -> None:
        """
        Uses an interactive interface to adjust settings based on user 
        feedback.
        """
        raise NotImplementedError("Not implemented yet.")




