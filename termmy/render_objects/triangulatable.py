from typing import Protocol

from termmy.buffers.framebuffer import FrameBuffer, hasColorBuffer
from termmy.render_objects.rasterization import RasterizationTriangle
    

class Triangulatable(Protocol):
    """
    A protocol for objects that can be triangulated.
    
    Methods:
        triangulate() -> list[RasterizationTriangle]:
            Returns a list of rasterization triangles representing the object.
    """
    def triangulate(self) -> list[RasterizationTriangle]: ...
