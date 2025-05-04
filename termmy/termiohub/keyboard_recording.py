

from dataclasses import dataclass, field
from time import time
from collections import deque

@dataclass(slots=True)
class KeyboardRecording:
    start_time: float | None = field(default_factory=time)
    end_time: float | None = None
    recording: list[tuple[str, float]] = field(default_factory=list)

    def records(self, raw_key_event: tuple[str, float]) -> None:
        self.recording.append(raw_key_event)

    def set_start_time(self, start_time: float | None = None) -> None:
        self.start_time = start_time or time()
    
    def set_end_time(self, end_time: float | None = None) -> None:
        self.end_time = end_time or time()
    
    def pop(self, num_raw_key_events: int) -> tuple[tuple[str, float], ...]:
        return reversed(tuple(self.recording.pop() for _ in range(num_raw_key_events)))
    
    def replays(self, key_buffer: deque[tuple[str, float]],
                          playback_speed: float = 1.0) -> None:
        timestamp_last_key = self.start_time
        if timestamp_last_key is None:
            raise ValueError("The recording does not have a start time.")
        playback_speed_reciprocal = 1.0 / playback_speed
        offset = time()
        for raw_key_event in self.recording:
            raw_key, timestamp = raw_key_event
            key_buffer.append((
                raw_key, 
                offset 
                + playback_speed_reciprocal * (
                    timestamp - timestamp_last_key
                )
            ))

    def __str__(self) -> str:
        timestamp_num_digits = (len(str(round(self.recording[-1][1], 3))) if self.recording 
                                else len(str(int(round(self.start_time, 3))))
                                if self.start_time is not None else 16)
        return "\n".join(
            f"{raw_key_event[1]:{timestamp_num_digits}.3f}, {repr(raw_key_event[0])}"
            for raw_key_event in self.recording
        )
    
    @property
    def duration(self) -> float | None:
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        else:
            return None
        
class KeyboardRecordingError(Exception): pass

class AlreadyRecordingError(KeyboardRecordingError): pass
class NotRecordingError(KeyboardRecordingError): pass
