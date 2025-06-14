

from __future__ import annotations

from .keys import Key, KeyEvent
from .getch import GETCH_TYPE, GetchType
from .key_constants import TERMIOS_KEY_MAPPING, TERMIOS_SEQUENCE_STARTS
from .key_constants import MSVCRT_KEY_MAPPING, MSVCRT_SEQUENCE_STARTS
from .key_constants import ASCII_MAPPING, FALLBACK_KEY_MAPPING
from .keyboard_recording import KeyboardRecording

from typing import Literal, ContextManager, ClassVar
from collections.abc import Generator
from types import MappingProxyType
from contextlib import contextmanager
from threading import Thread, Lock, RLock, Condition, Event
from time import time
from copy import copy
from queue import Queue

if GETCH_TYPE == GetchType.Termios:
    import termios, tty, sys
    from .getch import _FD, _OLD_SETTINGS
    set_term_raw = lambda: tty.setraw(_FD)
    set_term_default = lambda: termios.tcsetattr(_FD, 
                                                 termios.TCSADRAIN, 
                                                 _OLD_SETTINGS)
    flush_term = lambda: termios.tcflush(sys.stdin, termios.TCIFLUSH)
    read = sys.stdin.read

class TermIOHub(ContextManager):
    __slots__ = () # TODO Finish me
    active_instance: ClassVar[TermIOHub | None] = None

    exit_prompt: str

    _key_mappings: dict[str, Key]
    _sequence_startings: set[str]
    key_event_buffer: Queue[KeyEvent]
    
    thread: Thread
    io_lock: Lock
    not_reading_seq: Condition
    reading_seq: Event
    _stop_reading_keyboard: Event

    key_buffer_timeout: float
    sequence_timeout: float

    recording: KeyboardRecording | None

    ################################################################
    # Class
    ################################################################
    def __init__(self, exit_prompt: str = "Press enter to exit ...", 
                 key_buffer_timeout: float = 0.25,
                 sequence_timeout: float = 0.125):
        """A context manager for managing terminal input and output.

        It focuses on taking keyboard input, which may interfere with the
        default io operations such as `print`, `intput`, exceptions, etc.
        Use `safe_print` and/or `safe_io`, etc. to prevent such interference.

        The instance should not be reused after exiting the context manager,
        or a Runtime will raise.
        
        TODO Do I need to inform the user that they should not peddel with
        the terminal mode (raw/default) inside the block if they are using
        unix-like system, in which 

        A key (usually an enter) must be pressed to exit the context manager,
        which is why `exit_prompt` exists.

        Args:
            exit_prompt str: Display prompt at exit. Use "" to disable.
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
        if TermIOHub.active_instance is not None:
            raise RuntimeError("Only one instance of TermioHub can be "
                               "created and used at a time.")
        self.exit_prompt = exit_prompt

        (self._key_mappings,
         self._sequence_startings) = TermIOHub._get_default_key_mappings()
        self.key_event_buffer = Queue()

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
        if TermIOHub.active_instance is not None:
            raise RuntimeError("Only one instance of TermioHub can be "
                               "created and used at a time.")
        TermIOHub.active_instance = self
        # Ensure the code the terminal is set to raw inside the context
        if GETCH_TYPE == GetchType.Termios:
            set_term_raw()
        # Start the keyboard reading thread
        try:
            self.thread.start()
        except RuntimeError as e:
            raise RuntimeError("The instance should not be reused"
                               " after exiting the context manager."
                               f"Caught: {e}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
    
    def __del__(self):
        self._close()
    
    def _close(self) -> None:
        """Called in __exit__ and __del__.
        
        It joins the keyboard reading thread, deactivates itself from
        `TermIOHub.active_instance`, and optionally sets the terminal back
        to default.
        """
        if self.thread.is_alive():
            self._stop_reading_keyboard.set()
            self.thread.join()
        if TermIOHub.active_instance is self:
            TermIOHub.active_instance = None
            if GETCH_TYPE == GetchType.Termios:
                set_term_default()

    ################################################################
    # Input
    ################################################################
    def get_key_event(self) -> KeyEvent | None:
        """Get key event from keyboard or the recording replaying.
        Returns:
            KeyEvent | None: Key event object or `None` if no key is pressed 
                within the timeout.

        Raises:
            RuntimeError: If not called within the context.
        """
        # TODO: Implement this method
        raise NotImplementedError

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
    if GETCH_TYPE == GetchType.Termios:
        @contextmanager
        def safe_io(self) -> Generator[None, None, None]:
            """Context manager for safe IO operations within the TermIOHub 
            context. This ensures that IO operations behave the same way as
            they would outside the TermIOHub context.

            Raises:
                RuntimeError: If called outside of the TermIOHub context or in
                              the context of another TermIOHub instance.
            """
            if not (TermIOHub.active_instance is self):
                raise RuntimeError("`safe_io` is called outside of the "
                                   "TermIOHub context or in the context of "
                                   "another TermIOHub instance.")
            with self.io_lock:
                while self.reading_seq.is_set():
                    # Even if `_stop_reading_keyboard` is set while the
                    # keyboard reading thread is reading a sequence, it should
                    # not cause a deadlock.
                    # While only the keyboard reading thread can send notify
                    # the `not_reading_seq` or clear `reading_seq`, 
                    # `_stop_reading_keyboard` is only set when exiting the
                    # TermIOHub context. Since `safe_io` can only be called
                    # within the context, the keyboard reading thread must be
                    # running and will keep running until at least after
                    # `safe_io` lock exits.
                    self.not_reading_seq.wait()
                try:
                    set_term_default()
                    yield
                finally:
                    flush_term()
                    set_term_raw()
                    return
    else:
        @contextmanager
        def safe_io(self) -> Generator[None, None, None]:
            """Context manager for safe IO operations within the TermIOHub 
            context. This ensures that IO operations behave the same way as
            they would outside the TermIOHub context.

            Raises:
                RuntimeError: If called outside of the TermIOHub context or in
                              the context of another TermIOHub instance.
            """
            if not (TermIOHub.active_instance is self):
                raise RuntimeError("`safe_io` is called outside of the "
                                   "TermIOHub context or in the context of "
                                   "another TermIOHub instance.")
            with self.io_lock:
                while self.reading_seq.is_set():
                    # Even if `_stop_reading_keyboard` is set while the
                    # keyboard reading thread is reading a sequence, it should
                    # not cause a deadlock.
                    # While only the keyboard reading thread can send notify
                    # the `not_reading_seq` or clear `reading_seq`, 
                    # `_stop_reading_keyboard` is only set when exiting the
                    # TermIOHub context. Since `safe_io` can only be called
                    # within the context, the keyboard reading thread must be
                    # running and will keep running until at least after
                    # `safe_io` lock exits.
                    self.not_reading_seq.wait()
                try:
                    yield
                finally:
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
    
    def end_recording(self, trauncate_num_raw_key_events: int = 0) -> KeyboardRecording:
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
        lock = self.io_lock
        not_reading_seq = self.not_reading_seq
        reading_seq = self.reading_seq
        # Low level buffer used for sequence interpretation.
        # It can contain a single character, a valid control sequence, an
        # incomplete control sequence, or a series of characters that proves
        # to be an invalid sequence which will then be interpreted as 
        # individual keys.
        # While it would make sense to use a deque instead of a list here,
        # a list would suffice here and it probably performs better.
        char_buffer: list[str] = []
        timestamp_buffer: list[float] = []
        while not self._stop_reading_keyboard.is_set():
            char = read(1)
            timestamp = time()
            with lock:
                char_buffer.append(char)
                timestamp_buffer.append(timestamp)
                self._add_key_to_buffer(char_buffer, timestamp_buffer,
                                        not_reading_seq, reading_seq)

    def _read_keyboard_msvcrt(self) -> None:
        # TODO
        raise NotImplementedError

    def _read_keyboard_fallback(self) -> None:
        # TODO
        raise NotImplementedError

    def _add_key_to_buffer(self, char_buffer: list[str], 
                           timestamp_buffer: list[float],
                           not_reading_seq: Condition,
                           reading_seq: Event) -> None:
        """Used only in `_read_keyboard_*`. Parse the `char_buffer` and add 
        the key event(s) to the buffer if the sequence is complete or not a
        sequence at all.

        When `char_buffer` starts with a sequence starting character,
        it sets the `reading_seq` event to True.

        When a sequence is added to the self.key_event_buffer, 
        it notifies the `not_reading_seq` condition and sets the 
        `reading_seq` event to False.

        Raises:
            IndexError: If `char_buffer` or `timestamp_buffer` is empty.
        """
        starting_char = char_buffer[0]
        starting_time = timestamp_buffer[0]
        if starting_char in self._sequence_startings:
            reading_seq.set()
            seq = "".join(char_buffer)
            is_invalid_seq = False
            # This condition will only be true if `seq[:-1]` is not valid, 
            # i.e. the sequence of last iteration in `_read_keyboard_*` was
            # not yet deemed valid. So if the it times out this time, we can
            # say for sure it is not a valid sequence.
            if timestamp_buffer[-1] - starting_time > self.sequence_timeout:
                is_invalid_seq = True
            elif seq in self._key_mappings:
                is_invalid_seq = False
            # Linear search for valid sequences that starts with seq.
            elif not any(valid_seq.startswith(seq) for valid_seq in self._key_mappings):
                is_invalid_seq = True
            else:
                # An early return to prevent the buffers from being cleared
                return
            if is_invalid_seq:
                # Treat as individual keys
                for char, timestamp in zip(char_buffer, timestamp_buffer):
                    key = self._key_mappings.get(char, Key.unknown_key(char))
                    self.key_event_buffer.put(KeyEvent(key=key, 
                                                       timestamp=timestamp))
                
                reading_seq.clear()
                not_reading_seq.notify_all()
            else:
                # Return the sequence
                key = self._key_mappings[seq]
                timestamp = timestamp_buffer[0]
                self.key_event_buffer.put(KeyEvent(key=key, 
                                                   timestamp=timestamp))
                reading_seq.clear()
                not_reading_seq.notify_all()
        else:
            # Technically we should use popleft here because these buffers
            # should follow FIFO. However, when the char buffer does not
            # start with a sequence starting character, it will be cleared
            # after the character is added.
            key = self._key_mappings.get(starting_char,
                                        Key.unknown_key(starting_char))
            self.key_event_buffer.put(KeyEvent(key=key, 
                                               timestamp=starting_time))
        # Reached everytime except when the sequence is incomplete.
        char_buffer.clear()
        timestamp_buffer.clear()
