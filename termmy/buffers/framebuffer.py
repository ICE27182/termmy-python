from typing import Protocol
from dataclasses import dataclass

from .color_buffer import ColorBuffer

@dataclass(slots=True)
class FrameBuffer:
    color_buffer: ColorBuffer

class hasColorBuffer(Protocol):
    color_buffer: ColorBuffer

if __name__ == "__main__":
    c = ColorBuffer(2, 2)
    def f(f: hasColorBuffer): ...
    f(FrameBuffer(c))