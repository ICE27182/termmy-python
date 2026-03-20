from sys import platform, stdin, stdout
import os
from typing import Self


ENABLE_MOUSE = "\x1b[?1003h\x1b[?1006h"
DISABLE_MOUSE = "\x1b[?1003l\x1b[?1006l"

if os.name == "nt": # Windows
    from ctypes import wintypes, windll, byref

    # Windows API Constants
    _KERNEL32 = windll.kernel32
    _STD_INPUT_HANDLE = -10
    _STD_OUTPUT_HANDLE = -11
    _ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
    _ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    _ENABLE_MOUSE_INPUT = 0x0010
    _ENABLE_ECHO_INPUT = 0x0004
    _ENABLE_LINE_INPUT = 0x0002
    _ENABLE_PROCESSED_INPUT = 0x0001


    def store_win_term_into(original_in_config, original_out_config):
        h_in = _KERNEL32.GetStdHandle(_STD_INPUT_HANDLE)
        h_out = _KERNEL32.GetStdHandle(_STD_OUTPUT_HANDLE)
        
        # Save the modes
        _KERNEL32.GetConsoleMode(h_in, byref(original_in_config))
        _KERNEL32.GetConsoleMode(h_out, byref(original_out_config))


    def restore_win_term_from(original_in_config, original_out_config):
        h_in = _KERNEL32.GetStdHandle(_STD_INPUT_HANDLE)
        h_out = _KERNEL32.GetStdHandle(_STD_OUTPUT_HANDLE)
        
        # Restore exactly what the user had before
        _KERNEL32.SetConsoleMode(h_in, original_in_config)
        _KERNEL32.SetConsoleMode(h_out, original_out_config)


    def setup_win_io_config():
        # Output
        # Get handle and mode
        h_out = _KERNEL32.GetStdHandle(_STD_OUTPUT_HANDLE)
        out_mode = wintypes.DWORD()
        _KERNEL32.GetConsoleMode(h_out, byref(out_mode))
        # Prepare new mode
        out_mode.value |= _ENABLE_VIRTUAL_TERMINAL_PROCESSING
        # Set new mode
        _KERNEL32.SetConsoleMode(h_out, out_mode)

        # Input
        # Get handle and mode
        h_in = _KERNEL32.GetStdHandle(_STD_INPUT_HANDLE)
        in_mode = wintypes.DWORD()
        _KERNEL32.GetConsoleMode(h_in, byref(in_mode))
        # Prepare new mode
        new_in_mode = (in_mode.value 
                       | _ENABLE_VIRTUAL_TERMINAL_INPUT 
                       | _ENABLE_MOUSE_INPUT)
        new_in_mode &= ~(_ENABLE_ECHO_INPUT 
                         | _ENABLE_LINE_INPUT 
                         | _ENABLE_PROCESSED_INPUT)
        # Set new mode
        _KERNEL32.SetConsoleMode(h_in, new_in_mode)

    class _TermModeContextManager:
        _original_in_config: wintypes.DWORD
        _original_out_config: wintypes.DWORD

        def __enter__(self) -> Self:
            self._original_in_config = wintypes.DWORD()
            self._original_out_config = wintypes.DWORD()
            store_win_term_into(self._original_in_config, 
                                self._original_out_config)
            setup_win_io_config()
            stdout.write(ENABLE_MOUSE)
            stdout.flush()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> None:
            stdout.write(DISABLE_MOUSE)
            stdout.flush()
            restore_win_term_from(self._original_in_config, 
                                  self._original_out_config)


else: # POSIX
    import tty, termios, sys

    class _TermModeContextManager:
        _fd: int
        _old_settings: ...

        def __enter__(self) -> Self:
            self._fd = stdin.fileno()
            self._old_settings = termios.tcgetattr(self._fd)

            tty.setraw(self._fd)
            stdout.write(ENABLE_MOUSE)
            stdout.flush()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> None:
            stdout.write(DISABLE_MOUSE)
            stdout.flush()
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)
