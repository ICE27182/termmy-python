from tty import setraw
from termios import tcgetattr, tcsetattr, TCSADRAIN
from dataclasses import dataclass, field
from sys import stdin, stdout


ENABLE_MOUSE = "\x1b[?1003h\x1b[?1006h"
DISABLE_MOUSE = "\x1b[?1003l\x1b[?1006l"

@dataclass(slots=True, frozen=True)
class _UnixTermEnv:
    fd: int = field(init=False, default_factory=stdin.fileno)
    old_settings: list = field(
        init=False, 
        default_factory= lambda: tcgetattr(stdin.fileno()),
    )

    def __enter__(self) -> None:
        setraw(self.fd)
        stdout.write(ENABLE_MOUSE)
        stdout.flush()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        stdout.write(DISABLE_MOUSE)
        stdout.flush()
        tcsetattr(self.fd, TCSADRAIN, self.old_settings)
