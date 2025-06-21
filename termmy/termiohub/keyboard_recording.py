
from __future__ import annotations

from .keys import KeyEvent

from dataclasses import dataclass, field
from time import time
from collections.abc import Iterable, Iterator
from typing import Self, TYPE_CHECKING
from json import loads, dumps

if TYPE_CHECKING:
    from .keyboard import Keyboard

class KeyboardRecordingError(Exception):
    """Base exception for keyboard recording errors."""
    pass

class RecordingExistsError(KeyboardRecordingError):
    """Raised when attempting to start a new recording while one already exists."""
    pass

class RecordingNotExistsError(KeyboardRecordingError):
    """Raised when attempting to access a recording that does not exist or is not finished."""
    pass

class AlreadyRecordingError(KeyboardRecordingError):
    """Raised when attempting to start a recording while already recording."""
    pass

class NotRecordingError(KeyboardRecordingError):
    """Raised when attempting to add to or end a recording when not recording."""
    pass

@dataclass(slots=True)
class KeyboardRecording(Iterable):
    """
    Represents a recording of keyboard events, including timing information.

    Attributes:
        start_time (float | None): The timestamp when recording started.
        end_time (float | None): The timestamp when recording ended.
        data (list[KeyEvent]): The list of recorded KeyEvent objects.
    """
    start_time: float | None = None
    end_time: float | None = None
    data: list[KeyEvent] = field(default_factory=list)

    def __bool__(self) -> bool:
        """
        Returns True if the recording has started or ended, 
        False if it has not started i.e. it has no `start_time`.
        """
        return self.start_time is not None
    
    def __iter__(self) -> Iterator[KeyEvent]:
        """
        Returns an iterator over the recorded KeyEvent objects.

        If the recording is ongoing (not finished), this will yield all events
        recorded so far. If the recording has not started, yields nothing.

        Returns:
            Iterator[KeyEvent]: An iterator over the recorded events.
        """
        return iter(self.data)
    
    @classmethod
    def from_json_string(cls, json_string: str) -> Self:
        """
        Deserialize a KeyboardRecording from a JSON string.

        Args:
            json_string (str): The JSON string representing the recording.

        Returns:
            KeyboardRecording: The deserialized recording.
        
        Raises:
            KeyError: If the JSON string does not contain the required keys.
        """
        obj = loads(json_string)
        return cls(
            start_time=obj["start_time"],
            end_time=obj["end_time"],
            data=[KeyEvent.from_json_string(key_event_json) 
                  for key_event_json in obj["data"]],
        )
    
    def to_json(self) -> str:
        """
        Serialize the recording to a JSON string.

        Returns:
            str: The JSON string representing the recording.
        """
        return dumps({
            "start_time": self.start_time,
            "end_time": self.end_time,
            "data": [key_event.to_json() 
                     for key_event in self.data],
        }, indent=4)
    
    def is_recording(self) -> bool:
        """
        Returns True if currently recording (started but not ended).
        """
        return self.start_time is not None and self.end_time is None
    
    def finished(self) -> bool:
        """
        Returns True if the recording has started and ended.
        """
        return self.start_time is not None and self.end_time is not None

    def start_recording(self) -> None:
        """
        Start a new recording.

        Raises:
            RecordingExistsError: If a finished recording already exists.
            AlreadyRecordingError: If already recording.
        """
        if self.finished():
            raise RecordingExistsError()
        elif self.is_recording():
            raise AlreadyRecordingError()
        self.start_time = time()
    
    def add(self, key_event: KeyEvent) -> None:
        """
        Add a KeyEvent to the recording.

        Args:
            key_event (KeyEvent): The event to add.

        Raises:
            NotRecordingError: If not currently recording.
        """
        if not self.is_recording():
            raise NotRecordingError()
        self.data.append(key_event)
    
    def end_recording(self, trim_key_events: int = 0) -> Self:
        """
        End the current recording and optionally trim events from the end.

        Args:
            trim_key_events (int): Number of events to remove from the end.

        Returns:
            KeyboardRecording: The finished recording.

        Raises:
            NotRecordingError: If not currently recording.
            ValueError: If trim_key_events is negative.
        """
        if not self.is_recording():
            raise NotRecordingError()
        elif trim_key_events < 0:
            raise ValueError("trim_key_events must be non-negative.")
        self.end_time = time()
        for _ in range(min(trim_key_events, len(self.data))):
            self.data.pop()
        return self
    
    def clear(self) -> None:
        """
        Clear the recording, resetting start/end times and removing all events.
        """
        self.start_time = None
        self.end_time = None
        self.data.clear()
    
    def replay(self, keyboard: Keyboard,
               playback_speed: float = 1.0) -> None:
        """
        Replay the recorded events by appending them to the keyboard's event buffer
        with adjusted timestamps for playback speed.

        Args:
            keyboard (Keyboard): The keyboard instance to replay events into.
            playback_speed (float): The speed multiplier for playback (1.0 = real time).

        Raises:
            RecordingNotExistsError: If the recording is not finished.
            ValueError: If playback speed is less than or equal to 0.0.
        """
        if not self.finished():
            raise RecordingNotExistsError()
        if playback_speed <= 0.0:
            raise ValueError("Playback speed must be greater than 0.")
        playback_speed_reciprocal = 1.0 / playback_speed
        offset = time()
        # For each recorded event, calculate the new timestamp and append to the buffer.
        for key_event in self.data:
            keyboard.key_event_buffer.append(
                KeyEvent(
                    key_event.key, 
                    offset + playback_speed_reciprocal * (
                        key_event.timestamp - self.start_time
                    ),
                )
            )
    
    @property
    def duration(self) -> float | None:
        """
        Returns the duration of the recording in seconds, or None if not finished.

        Returns:
            float | None: The duration, or None if not available.
        """
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        else:
            return None
        