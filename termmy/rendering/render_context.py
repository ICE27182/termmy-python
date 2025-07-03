

from ..buffers import ColorBuffer, MultisampleColorBuffer

from dataclasses import dataclass

@dataclass
class RenderContext:
    width: int
    height: int
    color_buffer: ColorBuffer
    ms_buffer: MultisampleColorBuffer | None = None
