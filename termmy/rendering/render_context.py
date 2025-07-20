

from ..buffers import ColorBuffer, MultisampleColorBuffer

from dataclasses import dataclass

@dataclass
class RenderContext:
    width: int
    height: int
    color_buffer: ColorBuffer = None
    ms_buffer: MultisampleColorBuffer | None = None
    scratch_buffer: ColorBuffer | None = None

    # Used to convert absolute coordinates to pixel coordinates in rendering
    # Set in `Renderer.render_nodes` each call
    # `(width**2 + height**2)**0.5 * renderer.scalar`
    _abso_coord_scalar: float = 0.0

    def __post_init__(self):
        self.color_buffer = ColorBuffer(self.width, self.height)