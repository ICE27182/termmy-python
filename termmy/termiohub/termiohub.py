
from __future__ import annotations

from threading import Thread, RLock, Event
from collections import deque
from typing import Self, ClassVar, override
from dataclasses import dataclass, field
from queue import Queue
from time import monotonic
# Must be imported as a module for static analysis
# `from sys import platform` will not work for the static analyzer
import sys
from sys import stdin, stdout


if sys.platform == "win32":
    from ._env_setup_win import _WinTermEnv as _TermEnv
else:
    from ._env_setup_unix import _UnixTermEnv as _TermEnv

from .input_parser import parse
from .input_event import InputEvent
from .constants import DFA, KEY_MAPPING


# It appears the static analyzer may have some trouble understanding _TermEnv
# It is not a problem in the runtime. Thus the type ignore
@dataclass(slots=True, frozen=True)
class TermIOHub(_TermEnv):
    """
    A context manager for managing terminal input and output.

    Within the context, input bytes are read from stdin in a background
    thread and can be consumed with `get_input()` as parsed `InputEvent`
    values.

    In order to read terminal input reliably, this class will interfere with
    regular terminal I/O (for example `print` and `input`)

    The instance should not be reused after exiting the context manager,
    or `RuntimeError` will be raised. And the instance should only be used
    within the context manager, or `RuntimeError` will be raised.

    Changes to the terminal settings while inside the context manager may
    cause undefined behavior and the change may be lost. This is because
    upon entering, the terminal setting will be saved and modified, and upon
    exiting, the terminal setting will be restored to the saved state.

    A key press or a mouse movement may be needed to let the input thread
    proceed and complete shutdown, which is why `exit_prompt` exists.
    Typically, a simple mouse movement or a key press will be sufficient.
    An 'enter' key press will almost always work.
    
    The key interpretation is based on xterm's default settings and 
    US / international keyboard layouts, and may not be correct with certain
    OS or terminal settings, or with a different keyboard layout.
    
    Within the context, nextlines in the strings to be printed or sent to 
    `output` need to be "\r\n" instead of just "\n". For example, a call
    `print("Termmy\nICE27182")` needs to be rewrite as 
    `print("Termmy\r\nICE27182", end="\r\n")` to work properly.

    Args:
        read_input: Whether to start the input thread and allow `get_input()`.
        exit_prompt: Prompt written during shutdown when `read_input` is
            enabled. Use `""` to disable.
        concurrent_output: Whether `output()` writes through a dedicated
            output thread (thread-safe producer/consumer queue) instead of
            writing directly to stdout. This can potentially improve the IO
            performance when the output string is very large (e.g. a frame).

    Raises:
        RuntimeError: If the context manager is nested (that is, another
            `TermIOHub` instance is already active).
    """
    
    _active_instance: ClassVar[None | TermIOHub] = None
    
    read_input: bool = True
    exit_prompt: str = "Provide any input to exit...\n\r"
    
    concurrent_output: bool = True
    
    
    _stop: Event = field(kw_only=True, default_factory=Event)
    _new_input: Event = field(kw_only=True, default_factory=Event)
    
    _input_thread: Thread = field(init=False)
    # One producer, multiple consumers
    _inputs: deque[tuple[bytes, float]] = field(kw_only=True, default_factory=deque)
    _inputs_lock: RLock = field(kw_only=True, default_factory=RLock)
    
    _output_thread: Thread = field(init=False)
    # Multiple producers, one consumer
    _outputs: Queue[str] = field(kw_only=True, default_factory=Queue)
    
    def __post_init__(self):
        object.__setattr__(
            self, 
            "_input_thread", 
            Thread(target=_input_thread_func, args=(self,), daemon=True)
        )
        object.__setattr__(
            self,
            "_output_thread",
            Thread(target=_output_thread_func, args=(self,), daemon=True)
        )
    
    @override
    def __enter__(self) -> Self:
        if TermIOHub._active_instance is not None:
            raise RuntimeError("Only one instance of TermIOHub "
                               "can be active at a time.")
        TermIOHub._active_instance = self
        
        super().__enter__()
        
        if self.read_input:
            self._input_thread.start()
        if self.concurrent_output:
            self._output_thread.start()
            
        return self
    
    @override
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.read_input:
            self._stop.set()
            self.output(self.exit_prompt)
            self._input_thread.join()
        
        super().__exit__(exc_type, exc_val, exc_tb)
        
        TermIOHub._active_instance = None

    def get_input(self, max_latency: float = 0.5, 
                  sequence_timeout: float = 0.05, 
                  current_time: float | None = None) -> InputEvent | None:
        """
        Parse the input q with the given DFA. q may be mutated (via popleft).
    
        Args:
            max_latency (float): If a queued input exceeds this latency, it
                will be discarded.
                
            sequence_timeout (float): 
                Typically not needed to be set by the user.
                
                If a string is accepted by the DFA, 
                but it is also a prefix that maybe accepted, the parser will
                wait for more input until the timeout expires. If the timeout
                expires, the longest accepted prefix will be returned. 
                In most cases, this only applies to the ESC key.
            
            current_time (float | None): 
                The monotonic time to be considered as the current time, used
                for timeout calculation. 
                If it is None, the time will be obtained with 
                `time.monotonic()`.
            
        Returns:
            InputEvent | None: The parsed input event or None if no valid 
                event is available.

        Behaviors:
        - Returns None when no input is available or when currently
            buffered bytes are still ambiguous and more bytes may arrive
            before `sequence_timeout`.
        - Returns one parsed `InputEvent` at a time and consumes only the
            bytes that form that event from the internal queue.
        - If the leading byte is unknown to the DFA, it is returned as a
            single-byte keyboard event (unless discarded by latency).
        - For prefix-ambiguous sequences (for example ESC vs ESC-prefixed
            control sequences), parsing is greedy and returns the longest
            accepted prefix available at the time.
        - Stale input is dropped when the event timestamp is older than
            `max_latency` relative to `current_time`.
        """
        
        self._check()
        current_time = monotonic() if current_time is None else current_time
        with self._inputs_lock:
            parsed = parse(self._inputs, DFA, sequence_timeout, 
                           max_latency, current_time)
            if not parsed:
                return None
            return InputEvent.from_raw(*parsed, KEY_MAPPING)
        
    def output(self, value: str) -> None:
        """
        Write text to stdout.

        Behavior:
            - If `concurrent_output` is True, the value is enqueued and a
              dedicated output thread performs the actual write.
            - If `concurrent_output` is False, this method calls
              `stdout.write()` directly.
        """
        self._check()
        if self.concurrent_output:
            self._outputs.put(value)
        else:
            stdout.write(value)
            stdout.flush()
    
    def _check(self) -> None:
        if TermIOHub._active_instance is not self:
            raise RuntimeError("TermIOHub instance is not active.")



def _input_thread_func(termiohub: TermIOHub) -> None:
    while not termiohub._stop.is_set():
        char = stdin.buffer.read(1)
        if not char:
            termiohub._stop.set()
            
        with termiohub._inputs_lock:
            termiohub._inputs.append((char, monotonic()))
            
        termiohub._new_input.set()


def _output_thread_func(termiohub: TermIOHub) -> None:
    while not termiohub._stop.is_set() or not termiohub._outputs.empty():
        value = termiohub._outputs.get()
        if value is None:
            break
        stdout.write(value)
        stdout.flush()
