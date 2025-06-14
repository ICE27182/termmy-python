

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto

class ModifierState(StrEnum):
    YES = auto()
    NO = auto()
    UNKNOWN = auto()

@dataclass(slots=True, frozen=True)
class Key:
    name: str
    code: str
    shift: ModifierState = ModifierState.UNKNOWN
    control: ModifierState = ModifierState.UNKNOWN
    command: ModifierState = ModifierState.UNKNOWN
    option: ModifierState = ModifierState.UNKNOWN
    alt: ModifierState = ModifierState.UNKNOWN

    @classmethod
    def unknown_key(cls, code: str) -> Key:
        """
        Construct a Key object with the given code. The object will have both
        name and code attributes set to the given value, and the modifier 
        attributes set to `ModifierState.Unknown`.

        `code` must have a length of 1, or a ValueError will raise.
        """
        if len(code) != 1:
            raise ValueError("`code` must have a length of 1. "
                             f"Got {repr(code)}(length: {len(code)}).")
        return cls(name=code, code=code)

    def match(self, key: Key | str) -> bool:
        """
        Check if two keys are the same key.

        If `key` is string, then return True when the name matches.
        (case sensitive)
        
        Modifier keys such as shift and control will be ignored 
        if they are unknown. 
        They will only be considered if they are both known.
        """
        return (
            isinstance(key, Key)
            and self.name == key.name
            and (self.shift == ModifierState.UNKNOWN
                 or key.shift == ModifierState.UNKNOWN
                 or key.shift == self.shift)
            and (self.control == ModifierState.UNKNOWN
                 or key.control == ModifierState.UNKNOWN
                 or key.control == self.control)
            and (self.command == ModifierState.UNKNOWN
                 or key.command == ModifierState.UNKNOWN
                 or key.command == self.command)
            and (self.option == ModifierState.UNKNOWN
                 or key.option == ModifierState.UNKNOWN
                 or key.option == self.option)
            and (self.alt == ModifierState.UNKNOWN
                 or key.alt == ModifierState.UNKNOWN
                 or key.alt == self.alt)
            or isinstance(key, str)
            and self.name == key
        )
    
    def match_exactly(self, key: str) -> bool:
        """
        Check if two keys are the exactly same key.

        If `key` is string, then return True when the code matches.
        
        Modifier keys such as shift and control will also have to be the same.
        """
        return (
            isinstance(key, Key)
            and self.name == key.name
            and key.shift == self.shift
            and key.control == self.control
            and key.command == self.command
            and key.option == self.option
            and key.alt == self.alt
            or isinstance(key, str)
            and self.code == key
        )
    
    def match_loosely(self, key: Key) -> bool:
        """
        Check if two keys are the same key.

        If `key` is string, then return True when the name matches
        (case insensitive).

        Modifier keys such as shift and control will be ignored.

        Non-letter Ascii characters may still have to be the exact match:
        e.g. `,` will not match `LESS_THAN_KEY` 
             and `!` will not match `ONE_KEY`,
             even though the differences are just shift on an 
             American/international keyboard. 
             But `A` will match `A_LOWER_KEY`.
        """
        return (
            isinstance(key, Key)
            and self.name.lower() == key.name.lower()
            or isinstance(key, str)
            and self.name.lower() == key.lower()
        )

@dataclass(slots=True, frozen=True)
class KeyEvent:
    key: Key | None
    timestamp: float
