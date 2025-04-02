

from __future__ import annotations
from .image_format import ImageFormat
from .bmp import is_bmp, decode_bmp
from termmy.buffers import ColorBuffer, Buffer2D
from termmy.core import get_path_extension
from termmy.colors import Color
from os import PathLike
from typing import ByteString, ClassVar
from copy import copy
from dataclasses import dataclass

@dataclass(slots=True)
class Image:
    path: str | PathLike | None
    buffer: ColorBuffer
    metadata: dict

    image_formats: ClassVar[dict] = {
        "jpeg": ImageFormat.Jpeg,
        "jpg": ImageFormat.Jpeg,
        "jFIF": ImageFormat.Jpeg,
        "jIF": ImageFormat.Jpeg,
        "png": ImageFormat.Png,
        "bmp": ImageFormat.Bmp,
    }
    
    @classmethod
    def from_buffer2d(cls, buffer: Buffer2D) -> Image:
        """
        Create an Image object from a buffer. 
        
        The attribute `data` will not be a reference to the buffer past in.
        """
        width, height = buffer.width, buffer.height
        data = cls(width=width, 
                   height=height,
                   data=(
                       tuple(
                           copy(color)
                           for color in buffer.data
                       )
                       if isinstance(buffer, ColorBuffer)
                       else tuple(
                           buffer.get(x, y)
                           for y in range(height)
                           for x in range(width)
                       )
                   ))
        return Image(path=None, buffer=data, metadata={})
    
    @classmethod
    def from_image_file(cls, path: str | PathLike) -> Image:
        image = cls(path, None, {})
        image.read()
        return image

    @property
    def width(self) -> int:
        return self.buffer.width if self.buffer else None
    @property
    def height(self) -> int:
        return self.buffer.height if self.buffer else None
    
    def get_color(self, x:int, y:int) -> Color:
        """
        Return a new Color object at (x, y).

        The return value is not a reference to the pixel stored in the buffer.

        Performs bounds checking.
        """
        return self.buffer.get(x, y)

    def set_color(self, x:int, y:int, color: Color) -> Buffer2D:
        """
        Set the given color at (x, y). 
        
        The color will not be a reference to the argument.

        Performs bounds checking.
        """
        return self.buffer.set(x, y, color)

    def add_color(self, x:int, y:int, color: Color) -> Buffer2D:
        """
        Add the given color to (x, y). 
        
        The color will not be a reference to the argument.

        Performs bounds checking.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError("x or y out of bounds. "
                             f"Expected 0 <= x < {self.width} and 0 <= y < {self.height}, "
                             f"but got x={x}, y={y}.")
        base_color = self.buffer.data[y*self.width + x]
        base_color += color
        return self

    def decode(self, byte_string: ByteString) -> ColorBuffer:
        if is_bmp(byte_string):
            return decode_bmp(byte_string, self.metadata)
        raise NotImplementedError("Yet to be implemented")
    
    def encode(self, format: str | ImageFormat, write_metadata: bool = True) -> bytearray:
        raise NotImplementedError("Yet to be implemented")

    def read(self, path: str | PathLike | None = None) -> None:
        """
        Read the image file from `path`, decode it, save it to self.data

        Use `self.path` if `path` is not provided
        """
        path = path or self.path
        if not path:
            raise ValueError("`path` is not provided.")
        with open(path, "rb") as image_file:
            self.buffer = self.decode(image_file.read())
    
    def write(self, 
              path: str | PathLike | None = None, 
              format: str | ImageFormat = "", 
              write_metadata: bool = True) -> None:
        """
        Read the image file from `path`, decode it, save it to self.data

        Use `self.path` if `path` is not provided
        """
        path = path or self.path
        if not path:
            raise ValueError("`path` is not provided.")
        format = format or get_path_extension(path)
        with open(path, "wb") as image_file:
            image_file.write(self.encode(format=format, 
                                         write_metadata=write_metadata))
