
from __future__ import annotations

from threading import Thread, RLock
from collections import deque
from typing import Self, override
from dataclasses import dataclass, field
from queue import Queue
from enum import StrEnum, auto

from .term_mode import _TermModeContextManager


@dataclass(slots=True, frozen=True)
class KeyboardInput:
    class ModifierState(StrEnum):
        YES = auto()
        NO = auto()
        UNKNOWN = auto()
    key: str
    raw: str
    shift: ModifierState = ModifierState.UNKNOWN
    control: ModifierState = ModifierState.UNKNOWN
    command: ModifierState = ModifierState.UNKNOWN
    alt: ModifierState = ModifierState.UNKNOWN
    option: ModifierState = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "option", self.alt)

@dataclass(slots=True, frozen=True)
class MouseInput:
    class ButtonState(StrEnum):
        LEFT_DOWN = auto()
        LEFT_RELEASE = auto()
        RIGHT_DOWN = auto()
        RIGHT_RELEASE = auto()
        MIDDLE_DOWN = auto()
        MIDDLE_RELEASE = auto()
        SCROLL_UP = auto()
        SCROLL_DOWN = auto()
        NONE = auto()
    x: int
    y: int
    button_state: ButtonState
    raw: str

@dataclass(slots=True, frozen=True)
class InputEvent:
    input: KeyboardInput | MouseInput
    timestamp: float

class TermIOHub(_TermModeContextManager):
    _active_instance: None
    _inputs: deque[str] # One producer, multiple consumers
    _outputs: Queue[str] # Multiple producers, one consumer

    def __init__(self) -> None: ...

    @override
    def __enter__(self) -> Self:
        super().__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: 
        super().__exit__(exc_type, exc_val, exc_tb)

    def get_input(self) -> InputEvent | None: ...
    def get_input_blocking(self) -> InputEvent: ...
    def schedule_output(self, value: str): ...
