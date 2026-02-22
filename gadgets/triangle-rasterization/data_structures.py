from __future__ import annotations

from dataclasses import dataclass
from itertools import islice

@dataclass(slots=True)
class Vertex:
    x: float
    y: float
    u: float
    v: float

@dataclass(slots=True)
class Triangle:
    a: Vertex
    b: Vertex
    c: Vertex


@dataclass(slots=True)
class Color:
    r: int
    g: int
    b: int
    a: int = 255


@dataclass(slots=True)
class Buffer:
    width: int
    height: int
    data: list[Color]
    
    @classmethod
    def empty(cls, width: int, height: int, 
              r: int = 0, g: int = 0, b: int = 0) -> Buffer:
        return cls(width, height, [Color(r, g, b) 
                                   for _ in range(width * height)])
    
    @classmethod
    def ice(cls, width: int, height: int) -> Buffer:
        data = [Color(0, 0, 0) for _ in range(width * height)]
        cell = width // 16
        for y in range(height):
            for x in range(width):
                c = data[y * width + x]
                xc = x // cell
                yc = y // cell
                if (xc + yc) & 1:
                    c.r = 156
                    c.g = 220
                    c.b = 255
                else:
                    c.r = 255
                    c.g = 255
                    c.b = 255
        return cls(width, height, data)
    
    def fill(self, r: int = 0, g: int = 0, b: int = 0) -> None:
        for c in self.data: c.r, c.g, c.b = r, g, b
                
    
    def to_ansi(self) -> str:
        ansi_builder = "\033[48;2;%d;%d;%dm  \033[0m"
        data = self.data
        width = self.width
        return "\r\n".join(
            "".join(
                ansi_builder % (c.r, c.g, c.b) 
                for c in islice(data, i, i + width)
            )
            for i in range(0, self.height * width, width)
        )
        
        
@dataclass(slots=True)
class MSAABuffer:
    width: int
    height: int
    sample_level: int
    data: list[Color]
    
    @classmethod
    def from_buffer(cls, buffer: Buffer, sample_level: int) -> MSAABuffer:
        return cls(
            buffer.width,
            buffer.height,
            sample_level, 
            [Color(c.r, c.g, c.b) 
             for c in buffer.data
                for _ in range(1 << sample_level)],
        )
    
    @classmethod
    def empty(cls, width: int, height: int, sample_level: int,
              r: int = 0, g: int = 0, b: int = 0) -> MSAABuffer:
        length = (width * height) << sample_level
        return cls(width, height, sample_level, 
                   [Color(r, g, b) for _ in range(length)])
    
    def resolve_to(self, buffer: Buffer) -> None:
        (width, level, 
         data, buff) = self.width, self.sample_level, self.data, buffer.data
        samples = 1 << level
        resolved = (
            data[pixel_start : pixel_start + samples]
            for row_start in range(0, len(data), width << level)
                for pixel_start in range(row_start, row_start + (width << level), samples)
        )
        for target, colors in zip(buff, resolved):
            target.r = sum(c.r for c in colors) >> level
            target.g = sum(c.g for c in colors) >> level
            target.b = sum(c.b for c in colors) >> level


if  __name__ == "__main__":
    from timeit import repeat
    
    buff = Buffer.ice(80, 24)
    msaa_buff = MSAABuffer.from_buffer(buff, 2)
    msaa_buff.resolve_to(buff)
    print(buff.to_ansi())
    
    N = 1000
    t = min(
        repeat(
            "msaa_buff.resolve_to(buff)",
            "from __main__ import MSAABuffer, Buffer;"
            "buff = Buffer.ice(80, 24);"
            "msaa_buff = MSAABuffer.from_buffer(buff, 2)",
            number=N,
        ),
    )
    print(t / N)
    