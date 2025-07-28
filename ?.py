

from __future__ import annotations

from abc import ABC, abstractmethod
from os import PathLike
from dataclasses import dataclass, field
from enum import Enum
from typing import overload, ByteString, override, Any, Callable, ClassVar
from re import compile, IGNORECASE
from collections.abc import Iterable, Sequence, Iterator

class Stroke(ABC):
    @abstractmethod
    def get(self, t: float, s: float) -> Color: ...

class Fill(ABC):
    @abstractmethod
    def get(self, x, y) -> Color: ...


@dataclass(slots=True)
class Color(Fill, Stroke):
    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0
    @overload
    def get(self, t: float, s: float) -> Color: ...
    @overload
    def get(self, x: float, y: float) -> Color: ...
    @override
    def get(self, x_or_t, y_or_s) -> Color:
        return Color(self.r, self.g, self.b, self.a)

@dataclass(slots=True)
class Node:
    x: float
    y: float
    z: float
    # Hidden to encourage the user to use `add_child` instead of directly 
    # manipulating `_children`, which may lead to a node is a (grand)parent
    # of itself. Also to maintain order.
    _children: list[Node] = field(default_factory=list)
    
    def add_child(self, child: Node) -> None:
        """Add a new children.
        
        Raises:
           ValueError: If the parent/ancestor of the node or the node itself 
                       cannot be added as a child. 
        """
        if child is self or child.is_parent_of(self):
            raise ValueError("The parent/ancestor of the node or the node "
                             "itself cannot be added as a child.")
        else:
            self._children.append(child)
            self._children.sort(key=lambda node: node.z)
    
    def remove_child(self, child: Node) -> None:
        """Remove a child from this node.
        Raises:
            ValueError: If `child` is not a child of this node.
        """
        self._children.remove(child)
    
    def __contains__(self, node: Node) -> bool:
        return self.is_parent_of(node)
        
    def is_parent_of(self, node: Node) -> bool:
        """Return True if `node` is a child or a descendant of this node.

        Returns:
            bool: True if `node` is a child or a descendant of this node, 
                False otherwise. Whether the two nodes are the same node is
                not considered.
        """
        # TODO Can be optimized since since _children is ordered
        return (node in self._children
                or any(child.is_parent_of(node) 
                       for child in self._children))
    
    def is_direct_parent_of(self, node: Node) -> bool:
        """Return True if `node` is a direct child of this node.

        Returns:
            bool: True if `node` is a direct child of this node, 
                False otherwise.
                Whether the two nodes are the same node is not considered.
        """
        # TODO Can be optimized to O(log n) since _children is ordered
        return node in self._children
    
    def children(self) -> Iterator[Node]:
        return iter(self._children)

    def render(self, width: int, height: int) -> dict[tuple[int, int], Color]:
        out = {}
        self._render(width, height, out)
        return out
    
    def _render(self, width: int, height: int, 
                prev: dict[tuple[int, int], Color]) -> None:
        for child in self._children:
            child._render(width, height, prev)
        
        

@dataclass(slots=True)
class Scene:
    _nodes: list[Node]
    





    
class ResizingStrategy(ABC):
    # NOTE This function signature does not allow to resize to extend with
    # default color. In general, it is not as versatile. A few other examples
    # of its limitations can be resizing with another image as background.
    # As a resize strategy, you can however use it for transformations like
    # flipping, rotation, streching, etc.
    # How to improve the function sig?
    @abstractmethod
    def map_color(self, from_x: float, 
                  from_y: float) -> tuple[float, float]: ...

class ResizingStrategies:
    class AutoResizing(ResizingStrategy):
        ...

    @staticmethod
    # NOTE return AutoResizing or ResizingStrategy?
    def auto() -> ResizingStrategy:
        raise NotImplementedError

    @staticmethod
    # NOTE Return type to be decided
    def strech() -> Callable[[float, float], tuple[float, float]]:
        raise NotImplementedError
    
    ...

class QuantizationStrategy(ABC):
    @staticmethod
    @abstractmethod
    # NOTE should palette be allowed to be None?
    # For example, if the quantization is implemented as a pre-computed
    # lookup table, palette is not really important here, and instead,
    # this lookup table should be passed in.
    #
    # palette is currently stored as an array in Bitmap
    def quantize(self, color: Color, 
                 palette: Sequence[Color] | None,
                 *args,
                 **kwargs) -> int: ...

@dataclass(slots=True)
class Image(ABC):
    class Format(Enum):
        PNG = compile(r"png", IGNORECASE)
        JPEG = compile(r"jpeg|jpg|jpe|jif|jfif|jfi", IGNORECASE)
        BMP = compile(r"bmp", IGNORECASE)
        SVG = compile(r"svg", IGNORECASE)
        GIF = compile(r"gif", IGNORECASE)

        def __eq__(self, other: Any) -> bool:
            try:
                return self.value.fullmatch(other) is not None
            except TypeError:
                return False
        
        def __hash__(self) -> int:
            # NOTE Is it the best option tho?
            return hash(self.name)
    
    class Decoder(ABC):
        @staticmethod
        @abstractmethod
        def decode(data: ByteString, *args, **kwargs) -> Image: ...
    
    class Encoder(ABC):
        @staticmethod
        @abstractmethod
        # NOTE the type of data depends on implementation :(
        # How can it be improved? And should it return a byte, a bytearray or
        # a ByteString
        def encode(data: Any, *args, **kwargs) -> ByteString: ...
    
    metadata: dict[str, Any] = field(default_factory=dict)
    decoders: ClassVar[
        dict[Format, 
             Iterable[Decoder 
                      | Callable[[ByteString], Image]]]
    ] = {}
    encoders: ClassVar[
        dict[Format, 
             Iterable[Encoder 
                      | Callable[[Any], ByteString]]]
    ] = {}
    

    # NOTE Maybe palette should be here already, instead of be in its 
    # subclass Bitmap, because VectorImage and Gif (probably)also support 
    # palette?

    @classmethod
    @abstractmethod
    def from_file(cls, path: PathLike | str, 
                  decoder: Decoder | Callable[[ByteString], Image] | None = None,
                  *args,
                  **kwargs) -> Image: ...

    @abstractmethod
    def save_as(self, path: PathLike | str,
                image_type: Format,
                encoder: Encoder | Callable | None = None,
                *args,
                **kwargs) -> None: ...

    @abstractmethod
    def get_color(self, x: float, y: float) -> Color: ...

    # No set color because setting a color for a given position does not make 
    # sense for a vector image

    @abstractmethod
    def resize(self, horizontal_scalar: float, vertical_scalar: float, 
               stragety: ResizingStrategy) -> None: ...

    @abstractmethod
    def draw(self, shape: Shape) -> None: ...

    @abstractmethod
    def fill(self, color: Color) -> None: ...


@dataclass(slots=True)
class Bitmap(Image):
    # NOTE width: int = None and etc. seem wrong, but if the fields do
    # not have a default value, it will raise:
    # non-default argument 'width' follows default argument 'metadata'
    width: int = None
    height: int = None
    data: tuple[Color] = None
    # NOTE Does it make sense for it to always have an alpha channel?
    # array[float, CHANNEL_NUM * COLOR_NUM]
    palette: array | None = None

    def __post_init__(self):
        if self.data is None:
            self.data = tuple(Color() for _ in range(self.width * self.height))

    @override
    @classmethod
    def from_file(cls, path: PathLike | str, 
                  decoder: Image.Decoder 
                           | Callable[[ByteString], Image]
                           | None = None,
                  *args,
                  **kwargs) -> Image: 
        # NOTE is it necessary to do type checks and range checks here?
        raise NotImplementedError
    
    @override
    def save_as(self, path: PathLike | str,
                image_type: Bitmap.Format,
                encoder: Image.Encoder,
                *args,
                **kwargs) -> None:
        raise NotImplementedError
    
    @overload
    def get_color(self, x: float, y: float) -> Color: ...
    @overload
    def get_color(self, x: int, y: int) -> Color: ...

    @override
    def get_color(self, x: float | int, y: float | int) -> Color:
        # NOTE is it necessary to do type checks and range checks here?
        # Same for set_color and get_color_ref?
        if (isinstance(x, float) and isinstance(y, float)):
            x = int(x * self.width)
            y = int(y * self.height)
        raise NotImplementedError

    @overload
    def setColor(self, x: float, y: float, color: Color) -> None: ...
    @overload
    def setColor(self, x: int, y: int, color: Color) -> None: ...

    def setColor(self, x: float | int, y: float | int) -> None:
        if (isinstance(x, float) and isinstance(y, float)):
            x = int(x * self.width)
            y = int(y * self.height)
        raise NotImplementedError
    
    @overload
    def resize(self, width: int | None = None, height: int | None = None, 
               stragety: ResizingStrategy = ...) -> None: ...
    @overload
    def resize(self, horizontal_scalar: float, vertical_scalar: float, 
               stragety: ResizingStrategy) -> None: ...
    
    @override
    def resize(self, horizontal: float | int | None = None,
               vertical: float | int | None = None,
               stragety: ResizingStrategy = ...) -> None:
        raise NotImplementedError

    @override
    def draw(self, shape: Shape) -> None:
        raise NotImplementedError

    @override
    def fill(self, color: Color) -> None:
        raise NotImplementedError
    

@dataclass(slots=True)
class VectorImage(Image):
    ...


# NOTE Should I have AnimatedBitmap and AnimatedVectorImage?
@dataclass(slots=True)
class AnimatedImage(Image):
    frames: Iterable[Image] = None

    ...

    @override
    @classmethod
    def from_file(cls, path: PathLike | str, 
                  # NOTE The decoder returns an `Image`, not a list of 
                  # `Image`s, which seems problematic here
                  decoder: Image.Decoder 
                           | Callable[[ByteString], Image]
                           | None = None,
                  *args,
                  **kwargs) -> Image: 
        raise NotImplementedError
    
    ...

class Allocator(ABC):
    __slots__ = ("allocated", "index")
    def __init__(self, size: int = 1024) -> None:
        self.allocated = [None] * size
        self.index = 0

    def allocate(self, *args, **kwargs) -> Any:
        if self.index >= len(self.allocated):
            returned_object = None
            self.allocated.append(returned_object)
        else:
            returned_object = self.allocated[self.index]
        self.index += 1
        return returned_object
    
    def deallocate_all(self) -> None:
        self.index = 0

class ColorAllocator(Allocator):
    allocated: list[Color]
    def __init__(self, size: int = 1024) -> None:
        self.allocated = [Color() for _ in range(size)]
        self.index = 0
    def allocate(self, r: float, g: float, b: float, a: float, *args, **kwargs) -> Color:
        if self.index >= len(self.allocated):
            returned_object = Color(r, g, b, a)
            self.allocated.append(returned_object)
        else:
            returned_object = self.allocated[self.index]
            returned_object.r = r
            returned_object.g = g
            returned_object.b = b
            returned_object.a = a
        self.index += 1
        return returned_object



if __name__ == "__main__":
    try:
        Image()
    except Exception as e:
        print(e)

    try:
        VectorImage()
    except Exception as e:
        print(e)

    try:
        AnimatedImage()
    except Exception as e:
        print(e)

    img = Bitmap(width=0, height=0)
    img.metadata["size"] = "size"
    print(img)
