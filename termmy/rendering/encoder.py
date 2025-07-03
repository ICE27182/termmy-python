

from ..colors import Color
from ..buffers import Buffer2D, ColorBuffer

from abc import ABC, abstractmethod
from typing import overload, override, TYPE_CHECKING
from itertools import islice

if TYPE_CHECKING:
    from ..graphics import Scene
    from ..rendering import Renderer, RenderContext

class BufferEncoder(ABC):
    """Encode a buffer object into a string so it can be displayed in
    the terminal or saved in plain text. Alternatively, it can also 
    convert a scene into a string so the text tags are visible.
    """
    @overload
    def encode_buffer(self, buffer: Buffer2D) -> str: ...
    @overload
    def encode_buffer(self, buffer: ColorBuffer) -> str: ...
    @abstractmethod
    def encode_buffer(self, buffer: Buffer2D | ColorBuffer) -> str: ...

class SceneEncoder(ABC):
    @abstractmethod
    def render_and_encode(self, scene: Scene, renderer: Renderer, 
               render_context: RenderContext) -> str:
        ...

class ColorEncoder(BufferEncoder, SceneEncoder):
    @abstractmethod
    def convert(self, color: Color) -> str: ...
    @override
    def encode_buffer(self, buffer: Buffer2D | ColorBuffer) -> str:
        raise NotImplementedError
    @abstractmethod
    def render_and_encode(self, scene: Scene, renderer: Renderer, 
               render_context: RenderContext) -> str:
        pass
