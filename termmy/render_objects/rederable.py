from typing import Protocol

from buffers.framebuffer import FrameBuffer, hasColorBuffer

class Renderable(Protocol):
    """
    A protocol for objects that can be rendered.
    
    Methods:
        render(frame_buffer: FrameBuffer): 
            Renders the object into the specified frame buffer.
    """
    def render(self, frame_buffer: FrameBuffer): ...
