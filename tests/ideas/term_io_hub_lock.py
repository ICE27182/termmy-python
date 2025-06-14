
import tty, termios, sys, threading, queue
from time import time
from contextlib import contextmanager

_FD = sys.stdin.fileno()
_OLD_SETTINGS = termios.tcgetattr(_FD)

set_raw = lambda : tty.setraw(_FD)
set_default = lambda : termios.tcsetattr(_FD, termios.TCSADRAIN, _OLD_SETTINGS)
read = lambda : ch = sys.stdin.read(1)

lock = threading.RLock()
not_reading_seq = threading.Condition(lock)

seq_start: None | tuple[str, float] = None
key_buffer = queue.Queue()
running = True



def read_keyboard():
    while running:
        key = read()
        timestamp = time()

        with lock:
            key_buffer.put( (key, timestamp) )
            if key == '\x1b':
                seq_start = (key, timestamp)
            elif seq_start:
                if timestamp - seq_start[1] > 0.025:
                    seq_start = None
                    not_reading_seq.notify_all()

@contextmanager
def safe_io():
    lock.acquire()
    while seq_start:
        not_reading_seq.wait()
    try:
        set_default()
        yield
    finally:
        set_raw()
        lock.release()

def test():
    set_raw()
    threading.Thread(target=read_keyboard).start()

    ...

