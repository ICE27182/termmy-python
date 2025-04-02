import sys
from time import time
from collections import deque

if sys.platform == "win32":
    import msvcrt

    def getch():
        return msvcrt.getch()  # Read single byte, decode to UTF-8

else:
    try:
        import tty
        import termios

        def getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)  # Set to raw mode
                ch = sys.stdin.read(1)  # Read one character
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # Restore settings
            return ch
    except ImportError:
        getch = input

if __name__ == "__main__":
    last = time()
    history = deque([None]*10, maxlen=10)
    direction_map = {"A": "Up", "B": "Down", "C": "Right", "D": "Left"}
    while True: 
        this = time()
        key = getch()
        if key == '\x03':
            break
        if history[-2] == '\x1b' and history[-1] == '[' and key in direction_map:
            history.pop()
            history.pop()
            key = direction_map[key]
        history.append(key)
        print(f"{repr(key):10} {this - last:.12f} {history}")
        last = this