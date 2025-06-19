

from __future__ import annotations

from .keys import Key, KeyEvent
from .getch import GETCH_TYPE, GetchType
from .key_constants import TERMIOS_KEY_MAPPING, TERMIOS_SEQUENCE_STARTS
from .key_constants import MSVCRT_KEY_MAPPING, MSVCRT_SEQUENCE_STARTS
from .key_constants import ASCII_MAPPING, FALLBACK_KEY_MAPPING
from .keyboard_recording import KeyboardRecording

from typing import Literal, ContextManager, ClassVar, final
from collections.abc import Generator
from types import MappingProxyType
from contextlib import contextmanager
from threading import Thread, Lock, RLock, Condition, Event
from time import time
from copy import copy
from queue import Queue, Empty

if GETCH_TYPE == GetchType.Termios:
    import termios, tty, sys
    from .getch import _FD, _OLD_SETTINGS
    _set_term_raw = lambda: tty.setraw(_FD)
    _set_term_default = lambda: termios.tcsetattr(_FD, 
                                                 termios.TCSADRAIN, 
                                                 _OLD_SETTINGS)
    _flush_term = lambda: termios.tcflush(sys.stdin, termios.TCIFLUSH)
    _read = sys.stdin.read

@final
class TermIOHub(ContextManager):
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
    _active_instance: ClassVar[TermIOHub | None] = None

    _inside_safe_io: bool
    exit_prompt: str

    _key_mappings: dict[str, Key]
    _sequence_startings: set[str]
    key_event_buffer: Queue[KeyEvent]

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
                 sequence_timeout: float = 0.125):
        """A context manager for managing terminal input and output. 

        You can take keyboard input within the context with `get_key_event()`.

        In order to take keyboard input, it may interfere with the
        default io operations such as `print`, `intput`, etc.
        Use `safe_print` and/or `safe_io`, etc. to prevent such interference.

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
            key_buffer_timeout (float): Key presses before the timeout will be
                ignored. Setting it too high may lead to large latency and
                setting it too low may lead to missing key presses.
            sequence_timeout (float): Timeout for waiting for a control
                sequence of keys. Setting it high may lead high latency when
                pressing certain keys and setting it too low may lead to 
                incorrect interpretation of control sequences.
        
        Raises:
            RuntimeError: If the context manager is nested (i.e. an instance
                of TermIOHub is already active).
        """
        if TermIOHub._active_instance is not None:
            raise RuntimeError("Only one instance of TermioHub can be "
                               "created and used at a time.")
        self._inside_safe_io = False
        self.exit_prompt = exit_prompt

        (self._key_mappings,
         self._sequence_startings) = TermIOHub._get_default_key_mappings()
        self.key_event_buffer = Queue()

        self._char_buffer: list[str] = []
        self._timestamp_buffer: list[float] = []

        self.thread = Thread(target=self._read_keyboard, daemon=True)
        self.io_lock = RLock()
        self.not_reading_seq = Condition(self.io_lock)
        self.reading_seq = Event()
        self._stop_reading_keyboard = Event()

        self.key_buffer_timeout = key_buffer_timeout
        self.sequence_timeout = sequence_timeout

        # TODO finish recording
        self.recording = None

    def __enter__(self):
        """Sets up the terminal for non-blocking keyboard input (if possible),
        starts the keyboard reading thread, and enforces that only one 
        TermIOHub instance is active at a time.

        Raises:
            RuntimeError: If another TermIOHub instance is already active.
        """
        with TermIOHub._active_instance_lock:
            if TermIOHub._active_instance is not None:
                raise RuntimeError("Only one instance of TermioHub can be "
                                   "created and used at a time.")
            TermIOHub._active_instance = self
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
        `TermIOHub._active_instance`, and optionally sets the terminal back
        to default.
        """
        if self.thread.is_alive():
            if self.exit_prompt:
                self.safe_print(self.exit_prompt)
            self._stop_reading_keyboard.set()
            self.thread.join()
        # `TermIOHub._active_instance_lock` is not used here because 
        # it is assumed that only the thread that set the active instance
        # will set it back to `None`
        if TermIOHub._active_instance is self:
            TermIOHub._active_instance = None
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
            if self.key_event_buffer.empty():
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
            return self.key_event_buffer.get_nowait()
                    
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
    # Safe IO
    ################################################################
    @contextmanager
    def safe_io(self) -> Generator[None, None, None]:
        """Context manager for safe IO operations within the TermIOHub 
        context. This ensures that IO operations behave the same way as
        they would outside the TermIOHub context.

        Raises:
            RuntimeError: If called outside of the TermIOHub context or in
                            the context of another TermIOHub instance.
        """
        if not (TermIOHub._active_instance is self):
            raise RuntimeError("`safe_io` is called outside of the "
                                "TermIOHub context or in the context of "
                                "another TermIOHub instance.")
        with self.io_lock:
            if self.reading_seq.is_set():
                # If it is still reading a sequence, wait till it is done
                # or timeout and interpret the character(s) as individual 
                # key(s).
                # It times out if the user press a single Escape, or a
                # key with unregistered sequence (e.g. shift + up).
                # This function is not responsible for interpreting the
                # sequence because it only needs to make sure it will
                # not happen that the terminal is set from raw to default
                # will a sequence is not fully read, leading to it being
                # interpreted as individual characters later.
                self.not_reading_seq.wait(self.sequence_timeout)
            try:
                self._inside_safe_io = True
                if GETCH_TYPE == GetchType.Termios:
                    _set_term_default()
                yield
            finally:
                if GETCH_TYPE == GetchType.Termios:
                    _flush_term()
                    _set_term_raw()
                self._inside_safe_io = False
                return
    
    def safe_print(self,
                   *values: object,
                   sep: str | None = " ",
                   end: str | None = "\n",
                   flush: Literal[False] | bool = False) -> None:
        """A safe version of print to use within TermIOHub.
        ```
        with TermIOHub() as io_hub:
            ...
            io_hub.safe_print(...)
            # It is the same as using
            with io_hub.safe_io():
                print(...)
            ...
        """
        with self.safe_io():
            print(*values, sep=sep, end=end, flush=flush)

    ################################################################
    # Recording
    ################################################################
    def is_recording(self) -> bool:
        raise NotImplementedError
    
    def start_recording(self) -> None:
        raise NotImplementedError
    
    def end_recording(self, ignore_tail_key_events: int = 0) -> KeyboardRecording:
        raise NotImplementedError
    
    def replay(self, recording: KeyboardRecording, playback_speed: float = 1.0) -> None:
        raise NotImplementedError
    
    def get_recording(self) -> KeyboardRecording | None:
        raise NotImplementedError

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
        # TODO
        raise NotImplementedError

    def _read_keyboard_fallback(self) -> None:
       while not self._stop_reading_keyboard.is_set():
            string = input()
            char = string[-1] if string else ""
            timestamp = time()
            self.key_event_buffer(KeyEvent(
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
                    self.key_event_buffer.put(KeyEvent(key, timestamp))
            else:
                # Return the sequence
                key = key_mappings[seq]
                timestamp = time_buf[0]
                self.key_event_buffer.put(KeyEvent(key, timestamp))
            # Reached unless it is an incomplete sequence and it has not
            # yet timed out
            self.reading_seq.clear()
            self.not_reading_seq.notify_all()
        # It is not a sequence i.e. the char buffer has exactly one character
        else:
            key = key_mappings.get(starting_char, 
                                   Key.unknown_key(starting_char))
            self.key_event_buffer.put(KeyEvent(key, starting_time))
        # Reached everytime except when the sequence is incomplete.
        char_buf.clear()
        time_buf.clear()
