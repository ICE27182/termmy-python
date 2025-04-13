

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum, auto

class ModifierState(StrEnum):
    Yes = auto()
    No = auto()
    Unknown = auto()

@dataclass(slots=True, frozen=True)
class Key:
    name: str
    code: str
    shift: ModifierState = ModifierState.Unknown
    control: ModifierState = ModifierState.Unknown
    command: ModifierState = ModifierState.Unknown
    option: ModifierState = ModifierState.Unknown
    alt: ModifierState = ModifierState.Unknown


@dataclass(slots=True, frozen=True)
class KeyEvent:
    key: Key | None
    timestamp: float
