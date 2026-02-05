import tty, termios, sys
from time import time

_FD = sys.stdin.fileno()
_OLD_SETTINGS = termios.tcgetattr(_FD)

def read() -> str: return sys.stdin.read(1)
def write(s: str) -> None: sys.stdout.write(s)
def flush() -> None: sys.stdout.flush()

ENABLE_MOUSE = "\x1b[?1003h\x1b[?1006h"
DISABLE_MOUSE = "\x1b[?1003l\x1b[?1006l"

TIMEOUT = 0.1

try:
    tty.setraw(_FD)
    write(ENABLE_MOUSE)
    flush()
    
    i = 0
    last = 0.0
    while i < 10:
        ch = read()
        current = time()
        if current - last > TIMEOUT or ch == "\033":
            i += 1
            last = current
            start = "\r\n"
        else:
            start = ""
        write(f"{start}{str(ch.encode("latin-1"))[2:-1]}")
        flush()
    
finally:
    write(DISABLE_MOUSE)
    flush()
    termios.tcsetattr(_FD, termios.TCSADRAIN, _OLD_SETTINGS)
