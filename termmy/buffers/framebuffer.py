from typing import Protocol
from dataclasses import dataclass

from .color_buffer import ColorBuffer
from .entity_buffer import EntityBuffer

@dataclass(slots=True)
class FrameBuffer:
    color_buffer: ColorBuffer
    entity_buffer: EntityBuffer
    
    @classmethod
    def from_size(cls, width: int, height: int) -> FrameBuffer:
        return cls(ColorBuffer(width, height), 
                   EntityBuffer(width, height))


class hasColorBuffer(Protocol):
    color_buffer: ColorBuffer

class hasEntityBuffer(Protocol):
    entity_buffer: EntityBuffer
