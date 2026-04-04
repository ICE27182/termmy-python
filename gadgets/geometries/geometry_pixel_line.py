
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from basics import Vertex, Color, RasterizationTriangle, Buffer

@dataclass(slots=True, frozen=True)
class PixelLine:
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    color: Color