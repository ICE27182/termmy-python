from typing import Protocol

from termmy.buffers.framebuffer import FrameBuffer

class Renderable(Protocol):
    """
    A protocol for objects that can be rendered.
    
    Methods:
        render(frame_buffer: FrameBuffer): 
            Renders the object into the specified frame buffer.
    """
    def render(self, frame_buffer: FrameBuffer): ...
