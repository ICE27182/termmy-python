
from __future__ import annotations

from threading import Thread, RLock
from collections import deque
from typing import Self
from dataclasses import dataclass, field
from queue import Queue

class TermIOHub:
    _active_instance: None
    _inputs: deque[str] # One producer, multiple consumers
    _outputs: Queue[str] # Multiple producers, one consumer

    def __init__(self) -> None: ...

    def __enter__(self) -> Self: return self.start()
    def __exit__(self, exc_type, exc_val, exc_tb): return self.close()

    def start(self) -> Self: ...
    def close(self): ...        

    def get_input(self) -> ...: ...
    def schedule_output(self, value: str): ...
