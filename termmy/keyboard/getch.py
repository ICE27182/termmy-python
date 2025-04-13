import sys
import time
from enum import StrEnum, auto
from select import select
from time import sleep

class GetchType(StrEnum):
    Msvcrt = auto()
    Termios = auto()
    Fallback = auto()

if sys.platform == "win32":
    import msvcrt
    def getch():
        return msvcrt.getch().decode("ascii")
    GETCH_TYPE = GetchType.Msvcrt

    def getch_timeout(timeout: float) -> str:
        """
        Wait for a key press for up to `timeout` seconds, returning
        the character if pressed or an empty string if no key is pressed.
        """
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            if msvcrt.kbhit():
                return msvcrt.getch().decode("latin-1")
            # sleep a short time to avoid busy-waiting
            time.sleep(0.01)
        return ""
    
else:
    try:
        import tty
        import termios
        
        termios.tcgetattr(sys.stdin.fileno())
        def getch() -> str:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        GETCH_TYPE = GetchType.Termios

        def getch_timeout(timeout: float) -> str | None:
            """
            Wait for input for up to `timeout` seconds using select.
            Returns the first character if available, or an empty string
            if the timeout expires.

            May not work with control sequences.
            """
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                rlist, _, _ = select([sys.stdin], [], [], timeout)
                if rlist:
                    return sys.stdin.read(1)
                return None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except (ImportError, termios.error):
        GETCH_TYPE = GetchType.Fallback
        # Fallback: no proper timeout implementation; simply use input().
        def getch() -> str:
            return input()
        def getch_timeout(timeout: float) -> str:
            # Timeout not supported; immediately call getch.
            raise NotImplementedError("getch_timeout is not supported "
                                      "on this platform")

if __name__ == "__main__":
    print("Press a key (waiting up to 2 seconds):")
    ch = getch_timeout(2.0)
    if ch:
        print(f"You pressed: {repr(ch)}")
    else:
        print("Timed out waiting for a key press.")
    char = None
    while char != "Q":
        print("-"*80)
        char = getch()
        if char != "\r":
            print(repr(char))
        else:
            print("\n\n\n")