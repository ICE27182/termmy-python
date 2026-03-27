from dataclasses import dataclass
from enum import StrEnum, auto
from json import dumps, loads
from typing import ClassVar
from re import compile, Pattern

@dataclass(slots=True, frozen=True)
class KeyboardInput:
    """
    Represents a Keyboard input. 
    
    Modifier keys can be in three states: YES, NO, or UNKNOWN.
    """
    class ModifierState(StrEnum):
        """3 Modifier possibilities: YES, NO, UNKNOWN."""
        YES = auto()
        NO = auto()
        UNKNOWN = auto()
        
    key: str
    raw: bytes
    shift: ModifierState = ModifierState.UNKNOWN
    ctrl: ModifierState = ModifierState.UNKNOWN
    alt: ModifierState = ModifierState.UNKNOWN
    
    @property
    def control(self) -> ModifierState: return self.ctrl
    @property
    def option(self) -> ModifierState: return self.alt
    
    @classmethod
    def from_json(cls, json_str: str, **kwargs) -> KeyboardInput:
        data = loads(json_str, **kwargs)
        return cls(
            key=data["key"],
            raw=data["raw"],
            shift=cls.ModifierState(data["shift"]),
            ctrl=cls.ModifierState(data["ctrl"]),
            alt=cls.ModifierState(data["alt"]),
        )
    
    def to_json(self, *, indent=None, **kwargs) -> str:
        return dumps({
            "key": self.key,
            "raw": self.raw,
            "shift": self.shift.value,
            "ctrl": self.ctrl.value,
            "alt": self.alt.value,
        }, indent=indent, **kwargs)


@dataclass(slots=True, frozen=True)
class MouseInput:
    """Represents a mouse input.

    This model follows xterm-style mouse reporting and stores button state,
    movement/wheel flags, modifier flags, pointer position, and raw bytes.
    Use `from_raw` to parse CSI mouse sequences into a `MouseInput`.
    
    `release` is True iff the key is released in this event. If it is False,
    it is still possible that the key is not pressed.
    """
    class Button(StrEnum):
        """
        4 mouse button possibilities: LEFT, RIGHT, MIDDLE, NONE.
        """
        LEFT = auto()
        RIGHT = auto()
        MIDDLE = auto()
        NONE = auto()
        
        @classmethod
        def from_state(cls, state: int) -> MouseInput.Button:
            if state >= 64 or state & 0b11 == 3:
                return cls.NONE
            button_code = state & 0b11
            if button_code == 0:
                return cls.LEFT
            elif button_code == 1:
                return cls.RIGHT
            elif button_code == 2:
                return cls.MIDDLE
            else:
                return cls.NONE

    button: Button
    release: bool
    
    moving: bool
    
    wheel_up: bool
    wheel_down: bool
    
    shift: bool
    ctrl: bool
    alt: bool
    
    x: int
    y: int
    
    raw: bytes
    
    REGEX: ClassVar[Pattern] = compile(r"^\x1b\[<(\d+);(\d+);(\d+)([mM])$")
    SHIFT_MASK: ClassVar[int] = 4
    ALT_MASK: ClassVar[int] = 8
    CTRL_MASK: ClassVar[int] = 16
    MOVING_MASK: ClassVar[int] = 32
    
    @property
    def control(self) -> bool: return self.ctrl
    @property
    def option(self) -> bool: return self.alt
    
    @classmethod
    def from_raw(cls, raw: bytes) -> MouseInput | None:
        decoded = raw.decode("latin-1")
        matched = (decoded.startswith("\x1b[<")
                   and MouseInput.REGEX.match(decoded))
        if matched:
            state, x, y, release = (*map(int, matched.groups()[:3]),
                                          matched.group(4) == 'm')
            return MouseInput(
                button=cls.Button.from_state(state),
                release=release,
                moving=bool(state & cls.MOVING_MASK),
                wheel_up=bool(state & 64 and not state & 1),
                wheel_down=state & 65 == 65,
                shift=bool(state & cls.SHIFT_MASK),
                ctrl=bool(state & cls.CTRL_MASK),
                alt=bool(state & cls.ALT_MASK),
                x=x,
                y=y,
                raw=raw,
            )
        else:
            return None
    
    @classmethod
    def from_json(cls, json_str: str, **kwargs) -> MouseInput:
        data = loads(json_str, **kwargs)
        return cls(
            button=cls.Button(data["button"]),
            release=data["release"],
            moving=data["moving"],
            wheel_up=data["wheel_up"],
            wheel_down=data["wheel_down"],
            shift=data["shift"],
            ctrl=data["ctrl"],
            alt=data["alt"],
            x=data["x"],
            y=data["y"],
            raw=data["raw"].encode("latin-1"),
        )
    
    def to_json(self, *, indent=None, **kwargs) -> str:
        return dumps({
            "button": self.button.value,
            "release": self.release,
            "moving": self.moving,
            "wheel_up": self.wheel_up,
            "wheel_down": self.wheel_down,
            "shift": self.shift,
            "ctrl": self.ctrl,
            "alt": self.alt,
            "x": self.x,
            "y": self.y,
            "raw": self.raw,
        }, indent=indent, **kwargs)


@dataclass(slots=True, frozen=True)
class InputEvent:
    """
    Timestamped union of keyboard or mouse input.
    """
    input: KeyboardInput | MouseInput
    timestamp: float
    
    @staticmethod
    def from_raw(raw: bytes, timestamp: float, 
                 mapping: dict[bytes, KeyboardInput]) -> InputEvent:
        if raw in mapping:
            return InputEvent(input=mapping[raw], timestamp=timestamp)
        
        mouse = MouseInput.from_raw(raw)
        if mouse is not None:
            return InputEvent(input=mouse, timestamp=timestamp)
        
        return InputEvent(
            input=KeyboardInput(key=raw.decode("latin-1"), raw=raw),
            timestamp=timestamp
        )
