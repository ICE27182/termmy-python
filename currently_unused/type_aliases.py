import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pixel import Pixel24, Pixel32

type RGB = tuple[int, int, int]
type RGBA = tuple[int, int, int, int]
type Pos = tuple[int, int]
type Pixel = RGB | RGBA | Pixel24 | Pixel32