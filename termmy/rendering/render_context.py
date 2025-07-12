

from ..buffers import ColorBuffer, MultisampleColorBuffer

from dataclasses import dataclass

@dataclass
class RenderContext:
    width: int
    height: int
    color_buffer: ColorBuffer = None
    ms_buffer: MultisampleColorBuffer | None = None
    scratch_buffer: ColorBuffer | None = None

    def __post_init__(self):
        self.color_buffer = ColorBuffer(self.width, self.height)