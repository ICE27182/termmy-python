from ctypes import windll, byref
from ctypes.wintypes import DWORD
from mimetypes import init
from time import time
from dataclasses import dataclass, field
from sys import stdin, stdout


# Windows API Constants
KERNEL32 = windll.kernel32
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11

ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

ENABLE_EXTENDED_FLAGS = 0x0080

ENABLE_MOUSE_INPUT = 0x0010
ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_LINE_INPUT = 0x0002
ENABLE_ECHO_INPUT = 0x0004

ENABLE_MOUSE = "\x1b[?1003h\x1b[?1006h"
DISABLE_MOUSE = "\x1b[?1003l\x1b[?1006l"


def _store_win_term_into(original_in_config, original_out_config):
    h_in = KERNEL32.GetStdHandle(STD_INPUT_HANDLE)
    h_out = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE)
    
    # Save the modes
    KERNEL32.GetConsoleMode(h_in, byref(original_in_config))
    KERNEL32.GetConsoleMode(h_out, byref(original_out_config))

def _restore_win_term_from(original_in_config, original_out_config):
    h_in = KERNEL32.GetStdHandle(STD_INPUT_HANDLE)
    h_out = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE)
    
    # Restore exactly what the user had before
    KERNEL32.SetConsoleMode(h_in, original_in_config)
    KERNEL32.SetConsoleMode(h_out, original_out_config)

def _setup_win_io_config():
    # Output
    # Get handle and mode
    h_out = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE)
    out_mode = DWORD()
    KERNEL32.GetConsoleMode(h_out, byref(out_mode))
    # Prepare new mode
    out_mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
    # Set new mode
    KERNEL32.SetConsoleMode(h_out, out_mode)

    # Input
    # Get handle and mode
    h_in = KERNEL32.GetStdHandle(STD_INPUT_HANDLE)
    in_mode = DWORD()
    KERNEL32.GetConsoleMode(h_in, byref(in_mode))
    # Prepare new mode
    new_in_mode = in_mode.value | ENABLE_VIRTUAL_TERMINAL_INPUT | ENABLE_MOUSE_INPUT
    new_in_mode &= ~(ENABLE_ECHO_INPUT | ENABLE_LINE_INPUT | ENABLE_PROCESSED_INPUT)
    # Set new mode
    KERNEL32.SetConsoleMode(h_in, new_in_mode)


@dataclass(slots=True, frozen=True)
class _WinTermEnv:
    original_in_config: DWORD = field(init=False, default_factory=DWORD)
    original_out_config: DWORD = field(init=False, default_factory=DWORD)

    def __enter__(self) -> None:
        _store_win_term_into(self.original_in_config, self.original_out_config)
        _setup_win_io_config()
        stdout.write(ENABLE_MOUSE)
        stdout.flush()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        stdout.write(DISABLE_MOUSE)
        stdout.flush()
        _restore_win_term_from(self.original_in_config, self.original_out_config)


if __name__ == "__main__":
    with _WinTermEnv():
        last = 0.0
        for _ in range(20):
            loop = True
            while loop:
                char = stdin.buffer.read(1)
                if time() - last > 0.1 or char == b"\033":
                    stdout.write("\r\n")
                    stdout.flush()
                    last = time()
                    loop = False
                # stdout.write(str(char.encode("latin-1"))[2:-1])
                stdout.write(str(char)[2:-1])
                stdout.flush()
