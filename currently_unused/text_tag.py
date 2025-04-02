

from .type_aliases import Pos, RGBA
from .type_utils import is_pos

from typing import Self
from math import ceil

class TextTag:
    """
    `TextTag` should only be used for debugging.
    Performence related to `TextTag` will be less optimized.
    """
    def __init__(self, 
                 text:str = "", 
                 position:Pos = (0, 0),
                 color:RGBA|None = None,
                 centered:bool = False,
                 disabled:bool = False,
                 line_wrap:bool = None) -> None:
        # The initialization order is due to how the setters work
        self._centered = centered
        self.position = position
        self.color = color
        self.text = text
        self.disabled = disabled
        if line_wrap is None:
            self._line_wrap = not centered
        else:
            self.line_wrap = line_wrap
    
    def get_text_tag_that_fits(self) -> Self:
        """
        If the text tag starts left to the screen, it may have trouble
        displaying. 
        
        This methods return a new instance that should look the same as the
        original instance when displayed by removing off-screen part of its
        text and reset its position so it starts at 0.

        If the text tag starts in the screen or right to the screen, `self`
        will be returned.
        """
        x, y = self._position
        if x < 0 and -x < len(self._text) // 2:
            return TextTag(
                self._text[len(self._text) + x * 2 :],
                (0, y),
                color = self.color,
                centered=False,
                line_wrap=self._line_wrap
            )
        return self

    @property
    def centered(self) -> bool:
        return self._centered
    
    @property
    def line_wrap(self) -> bool:
        return self._line_wrap

    @property
    def text(self) -> str:
        return self._text
    
    @property
    def position(self) -> Pos:
        return (self._position[0] + len(self._text) // 2, self._position[1])
    
    def starting_position(self) -> Pos:
        return self._position
    
    @centered.setter
    def centered(self, is_centered:bool) -> None:
        if not isinstance(is_centered, bool):
            raise TypeError(
                "`self.centered` should be a boolean value. "
                f"Got {is_centered} of type {type(is_centered)}"
            )
        if self._line_wrap and is_centered:
            raise ValueError(
                "centered and line_wrap must not be True at the same time."
            )
        if self.centered == is_centered:
            return
        elif is_centered:
            self._position = (
                self._position[0] - len(self._text) // 4,
                self._position[1]
            )
        else: # elif not is_centered:
            self._position = (
                self._position[0] + len(self._text) // 4,
                self._position[1]
            )
        self._centered = is_centered

    @line_wrap.setter
    def line_wrap(self, is_line_wrap:bool) -> None:
        if not isinstance(is_line_wrap, bool):
            raise TypeError(
                "`self.line_wrap` should be a boolean value. "
                f"Got {is_line_wrap} of type {type(is_line_wrap)}"
            )
        if self._centered and is_line_wrap:
            raise ValueError(
                "centered and line_wrap must not be True at the same time."
            )
        self._line_wrap = is_line_wrap
    
    @text.setter
    def text(self, text:str = ""):
        """
        len(self.text) is always even to facilitate displaying. A space will
        be appended if the length is odd.
        """
        if not isinstance(text, str):
            raise TypeError(
                "text must be a str, "
                f"got {type(text).__name__}."
            )
        if "\n" in text or "\r" in text:
            raise ValueError(
                "newline character is not allowed in "
                f"{self.__class__.__name__}."
            )
        
        diff = 0
        if self._centered:
            diff = (len(self._text) - len(text)) // 4
        self._text = f"{text} " if len(text) & 1 else text
        self._position = (self._position[0] + diff, self._position[1])
    
    @position.setter
    def position(self, position:Pos):
        if not is_pos(position):
            raise TypeError(
                    "pos must be of type Pos, "
                    f"got {type(position).__name__}."
                )
        elif position[0] < 0 or position[1] < 0:
            raise ValueError(
                f"Coordinates must not be negative, got {position}."
            )
        self._position = position
        
            
    def __str__(self) -> str:
        """
        Result string is not affected by `self.disabled`
        """
        return self._text
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"_text = {self._text}, _position = {self._position}, "
            f"_centered = {self._centered}, _line_wrap = {self._line_wrap}"
            f"disabled = {self.disabled}, color = {self.color}"
            ")"
        )