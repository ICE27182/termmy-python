from __future__ import annotations

from typing import Final, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from termmy.render_objects.rederable import Renderable

@dataclass(slots=True)
class EntityBuffer:
    """
    A 2D buffer of renderable objects, where each object is represented by a `Renderable` object.
    
    Attributes:
        width (Final[int]): The width of the buffer in pixels. 
        height (Final[int]): The height of the buffer in pixels.
        _data (Final[list[Renderable | None, ...]]): 
            A flat list containing the renderable objects for each pixel.
            
            The entity pixel at coordinates (x, y) can be accessed with
            `data[y * width + x]`.
            
            If not provided, it will be initialized with the None.
            
            Do not change its length after initialization.
    """
    
    width: Final[int]
    height: Final[int]
    _data: Final[list[Renderable | None]]
    
    def __init__(self, width: int, height: int, data: list[Renderable | None] | None = None):
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError("Width and height must be integers. "
                            f"Got {type(width).__name__} for width and "
                            f"{type(height).__name__} for height.")
        
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers."
                             f"Got {width=}, {height=}")
            
        if data and len(data) != width * height:
            raise ValueError("Data length must be equal to width * height.")
        
        self.width = width
        self.height = height
        self._data = data if data else [None] * (width * height)

    def clear(self) -> None:
        """
        Clear the entity buffer by setting all pixels to None.
        """
        for i in range(len(self._data)):
            self._data[i] = None
    
    def get_entity(self, x: int, y: int) -> Renderable | None:
        """
        Get the entity at the given coordinates (x, y).
        
        Returns:
            Renderable | None: The entity at the given coordinates,
                or None if there is no entity.
        
        Raises:
            ValueError: If the coordinates are out of bounds.
        """
        if not (0 <= x < self.width) or not (0 <= y < self.height):
            raise ValueError(f"Coordinates (x={x}, y={y}) are out of bounds.")
        
        return self._data[y * self.width + x]
