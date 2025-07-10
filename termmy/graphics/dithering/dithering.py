

from abc import ABC, abstractmethod

from ...colors import Color
from ...buffers import ColorBuffer

class Dithering(ABC):
    @abstractmethod
    def dithered_color(self, buffer: ColorBuffer, x: int, y: int) -> Color:
        """Return a color that is dithered from the given buffer 
        at the specified coordinates.

        Performs bound checking.

        Returns:
            Color: A new Color object that represents the dithered color.
        
        Raises:
            IndexError: If x or y are out of bounds.
        """

    def apply_to(self, buffer: ColorBuffer) -> ColorBuffer:
        """Apply dithering effect to the buffer object passed in.

        Returns:
            ColorBuffer: A reference to the buffer passed in.
        """
        width, height, data = buffer.width, buffer.height, buffer.data
        for y in range(height):
            for x in range(width):
                data[y * width + x] = self.dithered_color(buffer, x, y)
        return buffer


