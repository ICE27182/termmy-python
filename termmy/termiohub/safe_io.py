

from .getch import GETCH_TYPE, GetchType
from .keyboard import Keyboard

from typing import Literal
from collections.abc import Generator
from contextlib import contextmanager
from functools import wraps

import builtins
_INPUT = builtins.input

if GETCH_TYPE == GetchType.Termios:
    import termios, tty, sys
    from .getch import _FD, _OLD_SETTINGS
    _set_term_raw = lambda: tty.setraw(_FD)
    _set_term_default = lambda: termios.tcsetattr(_FD, 
                                                 termios.TCSADRAIN, 
                                                 _OLD_SETTINGS)
    _flush_term = lambda: termios.tcflush(sys.stdin, termios.TCIFLUSH)

@contextmanager
def safe_io() -> Generator[None, None, None]:
    """Context manager for safe IO operations within the `Keyboard` 
    context. This ensures that IO operations behave the same way as
    they would outside the `Keyboard` context.

    NOTE This is not thread-safe and it should only be called within the
    `Keyboard` context. 
    - Using it in another thread will cause undefined behavior 
        if the `Keyboard` context exits before this context exits. 
    - Using it in multiple threads will cause undefined behavior.

    An extra Enter must be pressed when entering the context or functions
    such as `input` will take an empty string as its first input. This is
    irrelevant if only output functions such as `print` or `warning` are
    called within the context. Builtin `input` is overwritten within the
    context to ensure it.

    Raises:
        RuntimeError: If `safe_io` is called outside of the `Keyboard` 
            context or if it is nested.
    """
    # If we use `Keyboard._active_instance_lock` here, and if
    # it is used in a third thread, and the main thread is in
    # the keyboard context, we will have to wait for the main
    # thread to exit the context, which can take a long time
    # since that is probably inside a mainloop.

    # It is nested then on
    if (Keyboard._active_instance is None 
        or Keyboard._active_instance._inside_safe_io):
        raise RuntimeError("`safe_io` must be used within a `Keyboard` "
                           "context and it must not be nested.")
    with Keyboard._active_instance.io_lock:
        if Keyboard._active_instance.reading_seq.is_set():
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
            Keyboard._active_instance.not_reading_seq.wait(
                Keyboard._active_instance.sequence_timeout
            )
        try:
            Keyboard._active_instance._inside_safe_io = True
            if GETCH_TYPE == GetchType.Termios:
                _set_term_default()
                _flush_term()
            builtins.input = _overwritten_input
            yield
        finally:
            if GETCH_TYPE == GetchType.Termios:
                _flush_term()
                _set_term_raw()
            builtins.input = _INPUT
            Keyboard._active_instance._inside_safe_io = False
            return

def safe_print(*values: object,
               sep: str | None = " ",
               end: str | None = "\n",
               flush: Literal[False] | bool = False) -> None:
    """A safe version of print to use within `Keyboard`.

    NOTE This is not thread-safe and it should only be called within the
    `Keyboard` context. 
    - Using it in another thread will cause undefined behavior 
        if the Keyboard context exits before this function returns. 
    - Using it in multiple threads will cause undefined behavior.
    
    Raises:
        RuntimeError: If `safe_io` is called outside of the `Keyboard` 
            context or if it is used within a `safe_io` context.
    """
    if (Keyboard._active_instance is None 
        or Keyboard._active_instance._inside_safe_io):
        raise RuntimeError("`safe_print` must be used within a `Keyboard` "
                           "context and it must not be called within a "
                           "`safe_io` context.")
    with safe_io():
        print(*values, sep=sep, end=end, flush=flush)

def wait_for_input_ready(func):
    """Decorator that waits for input readiness before calling the function.

    This prevents race conditions where the keyboard reading threads trys to
    read the characters in the `safe_io` context while the `func` is also 
    trying to do so . It will take effect at most once per `safe_io` context. 
    To be exact, the first decorated function call within the `safe_io` 
    context will wait until a key (e.g. Enter) is pressed before proceeding.

    Builint `input` function is overwritten with this decorator within the
    `safe_io` context.
    ```python
    @wait_for_input_ready
    def _overwritten_input(prompt: str = "", /) -> str:
        Keyboard._active_instance._not_blocking.wait()
        return _INPUT(prompt)
    ```
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if Keyboard._active_instance:
            Keyboard._active_instance._not_blocking.wait()
        return func(*args, **kwargs)
    return wrapper

@wait_for_input_ready
def _overwritten_input(prompt: str = "", /) -> str:
    return _INPUT(prompt)
