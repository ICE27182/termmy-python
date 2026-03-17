
from __future__ import annotations

from threading import Thread, RLock
from collections import deque
from typing import Self, ClassVar
from dataclasses import dataclass, field
from queue import Queue
from enum import StrEnum, auto
# Must be imported as a module for static analysis
# `from sys import platform` will not work for the static analyzer
import sys


if sys.platform == "win32":
    from ._env_setup_win import _WinTermEnv as _TermEnv
else:
    from ._env_setup_unix import _UnixTermEnv as _TermEnv

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


# It appears the static analyzer may have some trouble understanding _TermEnv
# It is not a problem in the runtime. Thus the type ignore
@dataclass(slots=True, frozen=True)
class TermIOHub(_TermEnv):
    _active_instance: ClassVar[None | TermIOHub] = None
    # One producer, multiple consumers
    _inputs: deque[str] = field(default_factory=deque)
    # Multiple producers, one consumer
    _outputs: Queue[str] = field(default_factory=Queue)

    def __post_init__(self) -> None:
        if TermIOHub._active_instance is not None:
            raise RuntimeError("Only one instance of TermIOHub "
                               "can be active at a time.")
        TermIOHub._active_instance = self

    def get_input(self) -> InputEvent | None: ...
    def get_input_blocking(self) -> InputEvent: ...
    def schedule_output(self, value: str): ...
