

from __future__ import annotations

from dataclasses import dataclass
from abc import ABC

from ..node import Node

@dataclass(slots=True, kw_only=True)
class Shape(Node, ABC):
    pass
