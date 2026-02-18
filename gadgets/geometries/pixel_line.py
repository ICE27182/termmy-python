
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from basics import Vertex, Color, Triangle, Buffer

@dataclass(slots=True, frozen=True)
class PixelLine:
    start: Vertex
    end: Vertex
    color: Color
