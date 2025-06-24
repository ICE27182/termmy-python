

from __future__ import annotations

from .keys import Key, KeyEvent
from .getch import GETCH_TYPE, GetchType
from .key_constants import TERMIOS_KEY_MAPPING, TERMIOS_SEQUENCE_STARTS
from .key_constants import MSVCRT_KEY_MAPPING, MSVCRT_SEQUENCE_STARTS
from .key_constants import ASCII_MAPPING, FALLBACK_KEY_MAPPING
from .keyboard_recording import KeyboardRecording

from typing import ContextManager, ClassVar, final
from types import MappingProxyType
from threading import Thread, RLock, Condition, Event
from time import time
from copy import copy
from collections import deque

if GETCH_TYPE == GetchType.Termios:
    import termios, tty, sys
    from .getch import _FD, _OLD_SETTINGS
    _set_term_raw = lambda: tty.setraw(_FD)
    _set_term_default = lambda: termios.tcsetattr(_FD, 
                                                 termios.TCSADRAIN, 
                                                 _OLD_SETTINGS)
    _read = sys.stdin.read
elif GETCH_TYPE == GetchType.Msvcrt:
    from msvcrt import getwch

@final
class Keyboard(ContextManager):
    __slots__ = (
        "_inside_safe_io",
        "exit_prompt",
        "_key_mappings",
        "_sequence_startings",
        "key_event_buffer",
        "_char_buffer",
        "_timestamp_buffer",
        "thread",
        "io_lock",
        "not_reading_seq",
        "reading_seq",
        "_stop_reading_keyboard",
        "key_buffer_timeout",
        "sequence_timeout",
        "recording",
    )
    _active_instance_lock: ClassVar[RLock] = RLock()
    _active_instance: ClassVar[Keyboard | None] = None

    _inside_safe_io: bool
    exit_prompt: str

    _key_mappings: dict[str, Key]
    _sequence_startings: set[str]
    key_event_buffer: deque[KeyEvent]

    # Access to these buffers should be synchronized
    # Low level buffer used for sequence interpretation.
    # It can contain a single character, a valid control sequence, an
    # incomplete control sequence, or a series of characters that proves
    # to be an invalid sequence which will then be interpreted as 
    # individual keys.
    # Theoretically, we should use queues here because these buffers
    # should follow FIFO. However, in `_add_key_to_buffer`, the only function
    # that takes element from it, we only use `clear` method.
    _char_buffer: list[str]
    _timestamp_buffer: list[float]
    
    thread: Thread
    io_lock: RLock
    not_reading_seq: Condition
    reading_seq: Event
    _stop_reading_keyboard: Event

    key_buffer_timeout: float
    sequence_timeout: float

    recording: KeyboardRecording | None

    ################################################################
    # Class
    ################################################################
    def __init__(self, exit_prompt: str = "Press 'Enter' to exit ...",
                 key_buffer_timeout: float = 0.25,
                 sequence_timeout: float = 0.1):
        """A context manager for managing terminal input and output. 

        You can take keyboard input within the context with `get_key_event()`.

        In order to take keyboard input, it may interfere with the
        default io operations such as `print`, `intput`, etc.
        Use `safe_print` function and/or `safe_io` context, 
        to prevent such interference.

        The instance should not be reused after exiting the context manager,
        or a RuntimeError will raise.
        
        Try not to change the terminal settings within the context. It 
        internally relies on the terminal to be set to raw mode on certain  
        platforms (e.g. Linux, MacOS) in order to read keyboard input.
        Changeing the terminal within the context will cause undefined 
        behavior.

        A key (usually an enter) needs to be pressed to exit the context 
        manager, which is why `exit_prompt` exists.

        Args:
            exit_prompt (str): Display prompt at exit. Use "" to disable.
            key_buffer_timeout (float): Key presses before the timeout will 
                be ignored. Setting it too high may lead to large latency 
                and setting it too low may lead to missing key presses.
                It is recommended to set it at least larger than 
                `2*sequence_timeout`. Set it larger if there are missing key
                presses, especially Escape key on Unix-like systems.
            sequence_timeout (float): Timeout for waiting for a control
                sequence of keys. Setting it high may lead high latency when
                pressing certain keys and setting it too low may lead to 
                incorrect interpretation of control sequences.
        
        Raises:
            RuntimeError: If the context manager is nested (i.e. an instance
                of Keyboard is already active).
        """
        if Keyboard._active_instance is not None:
            raise RuntimeError("Only one instance of TermioHub can be "
                               "created and used at a time.")
        self._inside_safe_io = False
        self.exit_prompt = exit_prompt

        (self._key_mappings,
         self._sequence_startings) = Keyboard._get_default_key_mappings()
        self.key_event_buffer = deque()

        self._char_buffer: list[str] = []
        self._timestamp_buffer: list[float] = []

        self.thread = Thread(target=self._read_keyboard, daemon=True)
        self.io_lock = RLock()
        self.not_reading_seq = Condition(self.io_lock)
        self.reading_seq = Event()
        self._stop_reading_keyboard = Event()

        self.key_buffer_timeout = key_buffer_timeout
        self.sequence_timeout = sequence_timeout

        self.recording = None

    def __enter__(self):
        """Sets up the terminal for non-blocking keyboard input (if possible),
        starts the keyboard reading thread, and enforces that only one 
        Keyboard instance is active at a time.

        Raises:
            RuntimeError: If another Keyboard instance is already active.
        """
        with Keyboard._active_instance_lock:
            if Keyboard._active_instance is not None:
                raise RuntimeError("Only one instance of TermioHub can be "
                                   "created and used at a time.")
            Keyboard._active_instance = self
            # Ensure the code the terminal is set to raw inside the context
            if GETCH_TYPE == GetchType.Termios:
                _set_term_raw()
            # Start the keyboard reading thread
            try:
                self.thread.start()
            except RuntimeError as e:
                raise RuntimeError("The instance should not be reused"
                                   " after exiting the context manager."
                                   f"Caught: {e}")
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """It joins the keyboard reading thread, deactivates itself from
        `Keyboard._active_instance`, and optionally sets the terminal back
        to default.
        """
        if self.thread.is_alive():
            if self.exit_prompt:
                from .safe_io import safe_print
                safe_print(self.exit_prompt)
            self._stop_reading_keyboard.set()
            self.thread.join()
        # `Keyboard._active_instance_lock` is not used here because 
        # it is assumed that only the thread that set the active instance
        # will set it back to `None`
        if Keyboard._active_instance is self:
            Keyboard._active_instance = None
            if GETCH_TYPE == GetchType.Termios:
                _set_term_default()
    
    ################################################################
    # Input
    ################################################################
    def get_key_event(self) -> KeyEvent | None:
        """Get key event from keyboard or the recording replaying.

        Returns:
            KeyEvent | None: Key event object or `None` if no key is pressed 
                within the timeout.

        Raises:
            RuntimeError: If not called within the context, 
                          or is called inside of a safe_io block.
        """
        if self._inside_safe_io:
            raise RuntimeError("get_key_event() cannot be called inside of "
                               "a safe_io block.")
        with self.io_lock:
            while True:
                if not self.key_event_buffer:
                    if self.reading_seq.is_set():
                        # If it is still reading a sequence, wait till it is done
                        # or timeout and interpret the character(s) as individual 
                        # key(s).
                        # It times out if the user press a single Escape, or a
                        # key with unregistered sequence (e.g. shift + up).
                        # If so, this thread will be responsible for interpreting
                        # the sequence or character.
                        self.not_reading_seq.wait(self.sequence_timeout)
                        self._add_key_to_buffer(time())
                        # Now the key event buffer should not longer be empty.
                    else:
                        return None
                key_event = self.key_event_buffer[0]
                time_diff = time() - key_event.timestamp
                # TODO Remove me
                # print(f"\033[F\033[F\033[38;2;255;220;156m{time_diff:.6f}\t{str(key_event):200}")
                if time_diff < 0.0:
                    # A future key event from the recording being replayed.
                    # Return None for now and return the key event later when
                    # it becomes a present or a past key event that has not
                    # timed out.
                    return None
                elif time_diff <= self.key_buffer_timeout:
                    # Valid key event
                    self.key_event_buffer.popleft()
                    return key_event
                else:
                    # The key event times out
                    self.key_event_buffer.popleft()
                    
    @property
    def key_mappings(self) -> MappingProxyType[dict[str, Key]]:
        """Returns a read-only view of the key mappings.

        Returns:
            MappingProxyType[dict[str, Key]]: A read-only view of the key 
                mappings.
        """
        return MappingProxyType(self._key_mappings)
    
    def update_key_mappings(self, key_mapping: dict[str, Key]) -> None:
        """Customize how keys and control sequences are interpreted.
        You can add new key mappings or update existing ones.

        Use `remove_key_mappings` if you want to remove a specific key mapping.
        
        Args:
            key_mapping (dict[str, Key]): A dictionary of key mappings.
                The keys of the dictionary should be the raw input the terminal sents
                after receiving the keyboard input.
                E.g. `{"a": Key("a", "a"),
                       "\\x1b": Key("escape", "\\033"), 
                       "\\x00\\x3b": Key("F1", "\\x00\\x3b")}`
        """
        self._sequence_startings |= {code[0] for code in key_mapping.keys() if len(code) > 1}
        self._key_mappings.update(key_mapping)

    def remove_key_mappings(self, raw_input: str) -> Key | None:
        """Customize how keys and control sequences are interpreted.
        You can remove an existing key mapping with this method.

        Use `update_key_mappings` to add or modify existing mappings.

        Args:
            raw_input (str): The raw input to remove from the key mapping.
                It should be the raw input the terminal sents after
                receiving your keyboard input. 
                E.g. `"a"`, `"\\x1b"`, or `"\\x00\\x3b"`
        
        Returns:
            Key | None: The removed key mapping, or None if the key mapping
                does not exist.
        """
        out = self._key_mappings.pop(raw_input, None)
        # Cleanup g_sequence_startings if the removed key mapping has a
        # unique starting character
        if out and len(raw_input) > 1:
            starting = raw_input[0]
            if (starting in self._sequence_startings
                and not any(r.startswith(starting)
                            for r in self._key_mappings.keys())):
                del self._sequence_startings[starting]
        return out
    
    ################################################################
    # Recording
    ################################################################
    def is_recording(self) -> bool:
        return self.recording is not None
    
    def start_recording(self) -> None:
        """Starts recording keyboard input.
        
        Raises:
            RecordingExistsError: If the `recording` has ended.
            AlreadyRecordingError: If the keyboard is already recording.
        """
        self.recording = KeyboardRecording()
        self.recording.start_recording()
    
    def end_recording(self, trim_key_events: int = 0) -> KeyboardRecording:
        """Stops recording and returns the recorded KeyboardRecording.

        Args:
            trim_raw_events (int): The number of raw events to remove from the
                end of the recording. Defaults to 0. This can be useful when
                a key pressed is used to stop recording and you want to remove
                that key press from the recording.
           
        Returns:
            KeyboardRecording: The recorded keyboard input.

        Raises:
           NotRecordingError: If the keyboard is not currently recording.
           ValueError: If trim_raw_events is negative
        """
        out = self.recording.end_recording(trim_key_events)
        self.recording = None
        return out
    
    def replay(self, recording: KeyboardRecording, playback_speed: float = 1.0) -> None:
        """Start replaying the provided recording at the given playback speed.
        
        Once the replaying is started, it cannot be paused or stopped until
        it is finished. All key pressed during the replay will be captured and
        added to the end to `key_event_buffer`, which, consequently, are very 
        likely to time out before all the key events to replay have been 
        processed.

        If it is called while playing a recording, that recording will also
        be replayed right after the current one. This if the recording 
        involves keys that may trigger replaying the same recording, it will
        cause it to replay the same recording forever and normal user input 
        
        Raises:
            RecordingNotExistsError: If the provided recording has not been
                finished.
            ValueError: If the recording does not have a start time.
        """
        recording.replay(keyboard=self, playback_speed=playback_speed)

    ################################################################
    # Internals
    ################################################################
    @staticmethod
    def _get_default_key_mappings() -> tuple[dict[str, Key], set[str]]:
        key_mapping = copy(ASCII_MAPPING)
        if GETCH_TYPE == GetchType.Termios:
            key_mapping.update(TERMIOS_KEY_MAPPING)
            sequence_startings = set(TERMIOS_SEQUENCE_STARTS)
        elif GETCH_TYPE == GetchType.Msvcrt:
            key_mapping.update(MSVCRT_KEY_MAPPING)
            sequence_startings = set(MSVCRT_SEQUENCE_STARTS)
        elif GETCH_TYPE == GetchType.Fallback:
            key_mapping.update(FALLBACK_KEY_MAPPING)
            sequence_startings = set()
        return key_mapping, sequence_startings
        
    def _read_keyboard(self) -> None:
        if GETCH_TYPE == GetchType.Msvcrt:
            self._read_keyboard_msvcrt()
        elif GETCH_TYPE == GetchType.Termios:
            self._read_keyboard_termios()
        else:
            self._read_keyboard_fallback()
    
    def _read_keyboard_termios(self) -> None:
        while not self._stop_reading_keyboard.is_set():
            # We use the blocking function here instead of `select` because
            # for some reason it does not work well with control sequences.
            # It will give a true only for the first character in the sequence
            # and even though there are still characters waiting to be read,
            # it does not give another true until another key is pressed.
            char = _read(1)
            timestamp = time()
            with self.io_lock:
                self._char_buffer.append(char)
                self._timestamp_buffer.append(timestamp)
                self._add_key_to_buffer()

    def _read_keyboard_msvcrt(self) -> None:
        while not self._stop_reading_keyboard.is_set():
            # We use the blocking function here instead of checking for 
            # `kbhit` first for consistency because both
            # `_read_keyboard_termios` and `_read_keyboard_fallback` use
            # blocking functions, which makes it necessary to press some
            # extra keys to either exit the context or enter the `safe_io`
            # context (when using `input`).
            char = getwch()
            timestamp = time()
            with self.io_lock:
                self._char_buffer.append(char)
                self._timestamp_buffer.append(timestamp)
                self._add_key_to_buffer()
    

    def _read_keyboard_fallback(self) -> None:
       while not self._stop_reading_keyboard.is_set():
            string = input()
            char = string[-1] if string else ""
            timestamp = time()
            self.key_event_buffer.append(KeyEvent(
                self._key_mappings.get(char, Key.unknown_key(char)),
                timestamp,
            ))

    def _add_key_to_buffer(self, current_time: float | None = None) -> None:
        """Parse characters in `_char_buffer` and `_timestamp_buffer`, and add 
        one or more `KeyEvent` objects to `key_event_buffer` if possible.

        This method should only be called from within a synchronized code block
        in the keyboard reading thread. It handles:
        - Control sequence detection and timeout
        - Fallback to individual key interpretation if the sequence is invalid
        - Notification of the safe_io condition when sequence reading completes

        Args:
            current_time (float | None): Optional override for the current time,
                used to compute control sequence timeout. If None, the timestamp
                of the last character is used. This is 

        Returns:
            None
        """
        char_buf = self._char_buffer
        time_buf = self._timestamp_buffer
        if not char_buf or not time_buf: 
            return
        starting_char = char_buf[0]
        starting_time = time_buf[0]
        key_mappings = self._key_mappings
        # Check if it may be a sequence or not.
        if starting_char in self._sequence_startings:
            self.reading_seq.set()
            seq = "".join(char_buf)
            seq_time_diff = (time_buf[-1] 
                             if current_time is None 
                             else current_time) - starting_time
            is_invalid_seq = False
            # Decide whether it is a valid sequence, an incomplete sequnce
            # or an invalid seqeunce. A (potential) valid sequence can become
            # invalid if it times out.
            if seq_time_diff > self.sequence_timeout:
                # This case only occurs if `seq[:-1]` is not valid, 
                # because this method is called every time a new key input is
                # received. So if the it times out this time, we can
                # say for sure it is not a valid sequence.
                is_invalid_seq = True
            elif len(seq) == 1:
                # This prevent "\x1b" in the beginning of a sequence being 
                # interpreted as a valid key press i.e. Escape.
                # Escape key (especially on Unix-like systems) is handled
                # by the timeout above with `current_time` past in by the
                # caller `get_key_event`
                return
            elif seq in key_mappings:
                is_invalid_seq = False
            # Linear search for valid sequences that starts with seq.
            elif not any(valid_seq.startswith(seq) 
                         for valid_seq in key_mappings):
                is_invalid_seq = True
            else:
                # Incomplete and potentially valid sequence
                return
            # Deal with valid or invalid sequences. If the sequence is 
            # incomplete and potentially valid, it will not reach here.
            if is_invalid_seq:
                # Treat as individual keys
                for char, timestamp in zip(char_buf, time_buf):
                    key = key_mappings.get(char, Key.unknown_key(char))
                    key_event = KeyEvent(key, timestamp)
                    self.key_event_buffer.append(key_event)
                    if self.recording:
                        self.recording.add(key_event)
            else:
                # Return the sequence
                key = key_mappings[seq]
                timestamp = time_buf[0]
                key_event = KeyEvent(key, timestamp)
                self.key_event_buffer.append(key_event)
                if self.recording:
                    self.recording.add(key_event)
            # Reached unless it is an incomplete sequence and it has not
            # yet timed out
            self.reading_seq.clear()
            self.not_reading_seq.notify_all()
        # It is not a sequence i.e. the char buffer has exactly one character
        else:
            key = key_mappings.get(starting_char, 
                                   Key.unknown_key(starting_char))
            key_event = KeyEvent(key, starting_time)
            self.key_event_buffer.append(key_event)
            if self.recording:
                self.recording.add(key_event)
        # Reached everytime except when the sequence is incomplete.
        char_buf.clear()
        time_buf.clear()
