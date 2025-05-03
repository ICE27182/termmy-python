

from .getch import GETCH_TYPE, GetchType, _OLD_SETTINGS, _FD
from .keyboard import g_io_lock, g_key_buffer, g_sequence_startings
from typing import overload, Literal
from contextlib import contextmanager
from time import monotonic, time, sleep

if GETCH_TYPE == GetchType.Termios: 
    import termios
    import tty
    def _disable_echo(fd):
        attrs = termios.tcgetattr(fd)
        attrs[3] = attrs[3] & ~termios.ECHO  # lflags: unset ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, attrs)

    def _enable_echo(fd):
        attrs = termios.tcgetattr(fd)
        attrs[3] = attrs[3] | termios.ECHO   # lflags: set ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, attrs)

@overload
def safe_print(*values: object,
               sep: str | None = " ",
               end: str | None = "\n",
               flush: Literal[False] = False) -> None: ...

@overload
def safe_print(*values: object,
               sep: str | None = " ",
               end: str | None = "\n",
               flush: bool = False) -> None: ...

def safe_print(*values, sep=' ', end='\n', flush=False) -> None:
    """
    Use `safe_print` instead of builtin `print` function. 
    
    The terminal may be set to raw mode sometimes to read keyboard on 
    unix-like platforms.
    Builtin `print` will print in raw mode which is usually not ideal.
    `safe_print` can ensure the content will be printed in normal terminal
    mode.

    Note that all keyboard inputs will be discarded while printing.

    Has no effect on Windows platforms that supports msvcrt.
    
    T1 T2
     |
    -+

       |
       +-
    
    -+
    o|
    x|
       +-
       |o
       |x

    
    T1 T2
     |
    -+

       |
       +-
       +-
       |o
       |x
    
    -+
    o|
    x|
       
    """
    if GETCH_TYPE == GetchType.Termios:
        with g_io_lock:
            _wait_sequence()
            try:
                termios.tcsetattr(_FD, termios.TCSADRAIN, _OLD_SETTINGS)
                _disable_echo(_FD)
                print(*values, sep=sep, end=end, flush=flush)
            finally:
                _enable_echo(_FD)
                tty.setraw(_FD)
    else:
        print(*values, sep=sep, end=end, flush=flush)


@contextmanager
def safe_io():
    """
    A context manager that ensures functions that may be affected by terminal
    being set to raw mode (e.g. `print`, `input`, `warnings.warn`) will work
    as if the terminal was not. The terminal will be set to raw mode on 
    unix-like platforms to allow reading keyboard inputs.

    Note that when code within the context is running, all keyboard inputs
    will be discarded.
    
    Has no effect on Windows platforms that supports msvcrt.
    """
    if GETCH_TYPE == GetchType.Termios: 
        with g_io_lock:
            _wait_sequence()
            try:
                termios.tcsetattr(_FD, termios.TCSADRAIN, _OLD_SETTINGS)
                yield
            finally:
                tty.setraw(_FD)
    else:
        yield

def _wait_sequence():
    if g_key_buffer:
        last_key, timestamp = g_key_buffer[-1]
        if last_key in g_sequence_startings:
            wait_time = time() + 0.05 - timestamp
            if wait_time > 0:
                # This function is called within a `with g_io_lock`, so it is
                # safe to release the lock here
                g_io_lock.release()
                try:
                    sleep(wait_time)
                finally:
                    g_io_lock.acquire()
    
