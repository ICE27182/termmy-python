

from dataclasses import dataclass, field
from time import time
from collections import deque
from typing import Self
from codecs import decode

class KeyboardRecordingError(Exception): pass

class RecordingExistsError(KeyboardRecordingError): pass
class RecordingNotExistsError(KeyboardRecordingError): pass
class AlreadyRecordingError(KeyboardRecordingError): pass
class NotRecordingError(KeyboardRecordingError): pass

@dataclass(slots=True)
class KeyboardRecording:
    start_time: float | None = None
    end_time: float | None = None
    data: list[tuple[str, float]] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.start_time is not None
    
    def __str__(self) -> str:
        timestamp_num_digits = (len(str(round(self.data[-1][1], 3))) if self.data 
                                else len(str(int(round(self.start_time, 3))))
                                if self.start_time is not None else 16)
        return "\n".join(
            f"{raw_key_event[1]:{timestamp_num_digits}.3f}, {repr(raw_key_event[0])}"
            for raw_key_event in self.data
        )
    
    @classmethod
    def from_str(cls, string: str, 
                 starting_time: float | None = None, 
                 end_time: float | None = None) -> Self:
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

    def start(self, raw_key_event: tuple[str, float]) -> None:
        if self.finished():
            raise RecordingExistsError()
        elif self.is_recording():
            raise AlreadyRecordingError()
        self.start_time = time()
        self.data.append(raw_key_event)
    
    def end(self, trim_raw_events: int = 0) -> Self:
        if not self.is_recording():
            raise NotRecordingError()
        self.end_time = time()
        self.pop(trim_raw_events)
        return self
    
    def pop(self, num_raw_key_events: int) -> tuple[tuple[str, float], ...]:
        return reversed(tuple(self.data.pop() for _ in range(num_raw_key_events)))
    
    def clear(self) -> None:
        self.start_time = None
        self.end_time = None
        self.data.clear()
    
    def replay(self, key_buffer: deque[tuple[str, float]],
               playback_speed: float = 1.0) -> None:
        if not self.finished():
            raise RecordingNotExistsError()
        timestamp_last_key = self.start_time
        if timestamp_last_key is None:
            raise ValueError("The recording does not have a start time.")
        playback_speed_reciprocal = 1.0 / playback_speed
        offset = time()
        for raw_key_event in self.data:
            raw_key, timestamp = raw_key_event
            key_buffer.append((
                raw_key, 
                offset 
                + playback_speed_reciprocal * (
                    timestamp - self.start_time
                )
            ))
    
    @property
    def duration(self) -> float | None:
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        else:
            return None
        

