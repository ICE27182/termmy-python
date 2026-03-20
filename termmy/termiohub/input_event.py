from dataclasses import dataclass, field
from enum import StrEnum, auto

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
