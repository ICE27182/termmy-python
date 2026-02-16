import sys
from ctypes import wintypes, windll, byref
from contextlib import contextmanager
from typing import Generator
from time import time

# Windows API Constants
KERNEL32 = windll.kernel32
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
ENABLE_EXTENDED_FLAGS = 0x0080
ENABLE_MOUSE_INPUT = 0x0010
ENABLE_ECHO_INPUT = 0x0004
ENABLE_LINE_INPUT = 0x0002
ENABLE_PROCESSED_INPUT = 0x0001

ENABLE_MOUSE = "\x1b[?1003h\x1b[?1006h"
DISABLE_MOUSE = "\x1b[?1003l\x1b[?1006l"


def store_win_term_into(original_in_config, original_out_config):
    h_in = KERNEL32.GetStdHandle(STD_INPUT_HANDLE)
    h_out = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE)
    
    # Save the modes
    KERNEL32.GetConsoleMode(h_in, byref(original_in_config))
    KERNEL32.GetConsoleMode(h_out, byref(original_out_config))

def restore_win_term_from(original_in_config, original_out_config):
    h_in = KERNEL32.GetStdHandle(STD_INPUT_HANDLE)
    h_out = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE)
    
    # Restore exactly what the user had before
    KERNEL32.SetConsoleMode(h_in, original_in_config)
    KERNEL32.SetConsoleMode(h_out, original_out_config)

def setup_win_io_config():
    # Output
    # Get handle and mode
    h_out = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE)
    out_mode = wintypes.DWORD()
    KERNEL32.GetConsoleMode(h_out, byref(out_mode))
    # Prepare new mode
    out_mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
    # Set new mode
    KERNEL32.SetConsoleMode(h_out, out_mode)

    # Input
    # Get handle and mode
    h_in = KERNEL32.GetStdHandle(STD_INPUT_HANDLE)
    in_mode = wintypes.DWORD()
    KERNEL32.GetConsoleMode(h_in, byref(in_mode))
    # Prepare new mode
    new_in_mode = in_mode.value | ENABLE_VIRTUAL_TERMINAL_INPUT | ENABLE_MOUSE_INPUT
    new_in_mode &= ~(ENABLE_ECHO_INPUT | ENABLE_LINE_INPUT | ENABLE_PROCESSED_INPUT)
    # Set new mode
    KERNEL32.SetConsoleMode(h_in, new_in_mode)

@contextmanager
def terminal_mode() -> Generator[None, None, None]:
    # To store the user's original settings
    original_in_config = wintypes.DWORD()
    original_out_config = wintypes.DWORD()
    try:
        store_win_term_into(original_in_config, original_out_config)
        setup_win_io_config()
        print(ENABLE_MOUSE, end="", flush=True)
        yield
    finally:
        print(DISABLE_MOUSE, end="", flush=True)
        restore_win_term_from(original_in_config, original_out_config)


with terminal_mode():
    print("Move your mouse! (Press Ctrl+C to stop)\nBegin:")
    last = 0.0
    for _ in range(20):
        while True:
            char = sys.stdin.read(1)
            print(str(char.encode("latin-1"))[2:-1], end="")
            if time() - last > 0.1:
                break
        print("")
        last = time()
