from dataclasses import dataclass
from enum import StrEnum, auto
from json import dumps, loads
from typing import ClassVar
from re import compile, Pattern

@dataclass(slots=True, frozen=True)
class KeyboardInput:
    """
    A KeyboardInput object contains the name of the key, the raw bytes read
    from the terminal, and the modifier states. It also has an enum class
    `ModifierState` to represent the state of modifier keys.
    
    Modifier keys can be in three states: YES, NO, or UNKNOWN.
    
    Note that key strikes such as shift and ctrl are defined as modifiers,
    rather than separate key inputs. This is because we interpret the input
    based on the control sequences read from the terminal, and no control
    sequence is sent for these modifier keys alone. We can only infer 
    whether they are pressed based on the raw sequence.
    
    Attributes:
        key (str): The name assigned to the key input.
        raw (bytes): The raw byte sequence that was input. It is more like 
            the unique identifier for the key input.
        shift (KeyboardInput.ModifierState): The state of the Shift key.
        ctrl (KeyboardInput.ModifierState): The state of the Control key.
        alt (KeyboardInput.ModifierState): The state of the Alt key.
        control (KeyboardInput.ModifierState):
            Alias for ctrl implemented as a property.
        option (KeyboardInput.ModifierState):
            Alias for alt implemented as a property.
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
    """A MouseInput object contains the button state, cursor position,
    movement/wheel flags, modifier flags and the raw control sequence bytes.
    In addition, it as a nested enum class `Button` to represent the mouse 
    button involved in the event.
    
    The `MouseInput.Button` enum class has four members: `LEFT`, `RIGHT`, 
    `MIDDLE`, and `NONE`.
    
    Note that key strikes such as shift and ctrl are defined as modifiers,
    rather than separate key inputs. This is because we interpret the input
    based on the control sequences read from the terminal, and no control
    sequence is sent for these modifier keys alone. We can only infer 
    whether they are pressed based on the raw sequence.
    
    Unlike `KeyboardInput`, the type for the modifier keys here is just
    `bool` instead of `ModifierState`. This is because in mouse input 
    parsing, there is no ambiguity in determining whether a modifier key
    is pressed. We know for sure whether a modifier key is pressed based 
    on the raw sequence, and thus there is no "UNKNOWN" state.
    
    Attributes:
        raw (bytes): The raw byte sequence that was input. It is more like 
            the unique identifier for the mouse input.
            
        x (int): The column position of the cursor, 1-indexed.
        
        y (int): The row position of the cursor, 1-indexed.
        
        button (MouseInput.Button): The button involved in the event.
        
        wheel_up (bool): Whether the scroll wheel is scrolling up
        
        wheel_down (bool): Whether the scroll wheel is scrolling down
        
        release (bool): Whether the button was released in this event. 
            Note that `release` is True iff the key is released in this event.
            If it is False, it is still possible that the key is not pressed.
            It's just that it might have been released previously.
            
        moving (bool): Whether the cursor is moving in this event. 
            Note that if the cursor moves very little such that it still 
            points to same character cell of the terminal, `moving` can 
            be False
            
        shift (bool): Whether the Shift key is pressed
        
        ctrl (bool): Whether the Control key is pressed
        
        alt (bool): Whether the Alt key is pressed
        
        control (bool): Alias for ctrl implemented as a property.
        
        option (bool): Alias for alt implemented as a property.
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
    raw: bytes

    x: int
    y: int
    
    button: Button
    wheel_up: bool
    wheel_down: bool
    
    release: bool
    moving: bool
    
    shift: bool
    ctrl: bool
    alt: bool
    
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
    
    Attributes:
        input (KeyboardInput | MouseInput): The actual input event.
        timestamp (float): The timestamp of when the event was parsed, 
            in seconds since an arbitrary point in time (e.g. since the
            program started). It is recommended to use `time.monotonic()` 
            for this timestamp to avoid issues
            
    Examples:
    ```python
    with TermIOHub() as iohub:
        match iohub.get_input():
            case InputEvent(input=KeyboardInput(raw=b'Q') 
                            | constants.PredefinedKeys.C_CTRL.value 
                            as kb_input):
                ...
            case InputEvent(input=MouseInput(button=MouseInput.Button.LEFT) as ms_input):
                ...
            case InputEvent(input=MouseInput(moving=True)):
                ...
    ```
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
