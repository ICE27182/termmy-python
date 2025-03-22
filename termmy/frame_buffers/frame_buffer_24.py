

from termmy.core import Color, SharedMemoryUser
from .frame_buffer_base import FrameBufferBase
from .text_tag import TextTag

from typing import override, overload
from collections.abc import Iterable
from multiprocessing.shared_memory import SharedMemory


class FrameBuffer24(FrameBufferBase):
    __slots__ = ("width", "height", "_data", "format_str")
    channel_num = 3
    def __init__(self, width: int, height: int,
                 data: SharedMemory|None = None, name: str = "frame_buffer"):
        """
        `width` and `height` should be positive integers.

        `channel_num` should be an integer equal to either 3 or 4.
        """
        self.width = width
        self.height = height
        try:
            shm = SharedMemory(name, create=False)
            shm.close()
            shm.unlink()
        except FileNotFoundError:
            pass
        try:
            size = width*height*FrameBuffer24.channel_num
            self._data = data or SharedMemory(name, create=True, size=size)
        except Exception as e:
            if self._data:
                self._data.close()
                self._data.unlink()
            raise e
        self.format_str = ("\033[48;2;%d;%d;%dm  " * width) + "\033[0m\n"

    def __del__(self) -> None:
        try:
            if self._data:
                self._data.close()
                self._data.unlink()
        except Exception as e:
            print(e)
        
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self._data.close()
        self._data.unlink()

    @property
    def data(self) -> memoryview:
        return self._data.buf
    @data.setter
    def data(self, data: bytearray) -> None:
        buf = self._data.buf
        if len(data) > len(buf):
            buf[:] = data[:len(buf)]
        else:
            buf[:len(data)] = data

    @override
    def clear(self) -> None:
        length = self.width * self.height * self.channel_num
        self._data.buf[:length] = b"\0" * length

    @override
    def fill(self, 
             color: bytes | bytearray | Color | None = None) -> FrameBufferBase:
        """
        Fill the frame buffer with `color`.

        `color` will default to Color(255, 255, 255, 255) if not provided.
        """
        color = color or Color(255, 255, 255, 255)
        if isinstance(color, Color):
            color = color.to_bytes_24()
        resolution = self.width * self.height
        self._data.buf[:resolution*self.channel_num] = color * resolution
        return self

    @overload
    def colored_string_24(self) -> str: ...
    
    @overload
    def colored_string_24(self, text_tags: Iterable[TextTag]) -> str: ...
    
    def colored_string_24(self, 
                          text_tags: None | Iterable[TextTag] = None) -> str:
        """
        """
        if not text_tags:
            data = self.data
            channel_num = self.channel_num
            byte_row_width = self.width * channel_num
            format_str = self.format_str
            str_buff = (
                (format_str % tuple(data[y : y+byte_row_width]))
                for y in range(0, self.height*byte_row_width, byte_row_width)
            )
            return "".join(str_buff)
        else:
            return super().colored_string_24(text_tags)
    
    def __getitem__(self, y: int) -> memoryview:
        return self._data.buf[y : y + self.width*self.channel_num]
    
    @override
    def get_color(self, x:int, y:int) -> Color:
        """
        Return a new Color object at (x, y).

        The return value is not a reference to the pixel stored in the buffer.
        """
        address = (y*self.width + x) * self.channel_num
        return Color(*self._data.buf[address : address+self.channel_num])
    
    @override
    def get_color_byte(self, x:int, y:int) -> bytes:
        """
        Return a bytes object of size 3 or 4 depending on whether alpha is stored
        """
        address = (y*self.width + x) * self.channel_num
        return bytes(self._data.buf[address : address+self.channel_num])

    @override
    def set_color(self, x:int, y:int, 
                 color: bytes | bytearray | Color) -> FrameBufferBase:
        """
        Set the given color at (x, y). 
        
        The color will not be a reference to the argument.
        """
        frame_buf = self._data.buf
        address = (y*self.width + x) * self.channel_num
        frame_buf[address : address+self.channel_num] = color.to_bytes_24()
        return self

    @override
    def add_color(self, x:int, y:int, 
                 color: bytes | bytearray | Color) -> FrameBufferBase:
        """
        Set the given color at (x, y). 
        
        The color will not be a reference to the argument.
        """
        frame_buf = self._data.buf
        address = (y*self.width + x) * self.channel_num
        color = Color.from_bytes(
            frame_buf[address : address+self.channel_num]
        ) + color
        frame_buf[address : address+self.channel_num] = color.to_bytes_24()
        return self

    
