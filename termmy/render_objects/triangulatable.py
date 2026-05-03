from termmy.buffers.framebuffer import FrameBuffer, hasColorBuffer
from termmy.render_objects.rasterization import RasterizationTriangle

from .rederable import Renderable
    

class Triangulatable(Renderable):
    """
    A protocol for objects that can be triangulated.
    
    Methods:
        triangulate() -> list[RasterizationTriangle]:
            Returns a list of rasterization triangles representing the object.
    """
    def triangulate(self) -> list[RasterizationTriangle]: ...
