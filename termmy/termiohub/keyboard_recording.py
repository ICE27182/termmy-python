
from __future__ import annotations

from .keys import KeyEvent

from dataclasses import dataclass, field
from time import time
from collections.abc import Iterable, Iterator
from typing import Self, TYPE_CHECKING
from codecs import decode

if TYPE_CHECKING:
    from .keyboard import Keyboard

class KeyboardRecordingError(Exception): pass

class RecordingExistsError(KeyboardRecordingError): pass
class RecordingNotExistsError(KeyboardRecordingError): pass
class AlreadyRecordingError(KeyboardRecordingError): pass
class NotRecordingError(KeyboardRecordingError): pass

@dataclass(slots=True)
class KeyboardRecording(Iterable):
    start_time: float | None = None
    end_time: float | None = None
    data: list[KeyEvent] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.start_time is not None
    
    def __iter__(self) -> Iterator[KeyEvent]:
        return self.data.__iter__()
    
    def __str__(self) -> str:
        return "\n".join(
            f"{key_event.timestamp} {repr(key_event.key)}" 
            for key_event in self.data
        )
    
    @classmethod
    def from_str(cls, string: str, 
                 starting_time: float | None = None, 
                 end_time: float | None = None) -> Self:
        raise NotImplementedError
        data = [
            (values[1][1:-1], float(values[0]))
            for line in decode(string, "unicode_escape").splitlines()
            if (values:=line.split(", ") or True)
        ]
        return cls(starting_time or data[0][1] - 1.0,
                   end_time or data[-1][1] + 1.0,
                   data)
    
    def is_recording(self) -> bool:
        return self.start_time is not None and self.end_time is None
    
    def finished(self) -> bool:
        return self.start_time is not None and self.end_time is not None

    def start_recording(self) -> None:
        if self.finished():
            raise RecordingExistsError()
        elif self.is_recording():
            raise AlreadyRecordingError()
        self.start_time = time()
    
    def add(self, key_event: KeyEvent) -> None:
        if not self.is_recording():
            raise NotRecordingError()
        self.data.append(key_event)
    
    def end_recording(self, trim_key_events: int = 0) -> Self:
        if not self.is_recording():
            raise NotRecordingError()
        elif trim_key_events < 0:
            raise ValueError("trim_key_events must be non-negative.")
        self.end_time = time()
        for _ in range(min(trim_key_events, len(self.data))):
            self.data.pop()
        return self
    
    def clear(self) -> None:
        self.start_time = None
        self.end_time = None
        self.data.clear()
    
    def replay(self, keyboard: Keyboard,
               playback_speed: float = 1.0) -> None:
        if not self.finished():
            raise RecordingNotExistsError()
        playback_speed_reciprocal = 1.0 / playback_speed
        offset = time()
        for key_event in self.data:
            keyboard.key_event_buffer.put(
                KeyEvent(
                    key_event.key, 
                    offset + playback_speed_reciprocal * (
                        key_event.timestamp - self.start_time
                    ),
                )
            )
    
    @property
    def duration(self) -> float | None:
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        else:
            return None
        