
from __future__ import annotations

from typing import Protocol
from dataclasses import dataclass

@dataclass(slots=True)
class Buffer2D(Protocol):
    width: int
    height: int
