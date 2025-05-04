
# Problem with getch and input

from threading import Thread, Lock
from msvcrt import getch

key = None
lock = Lock()

def workder():
    captured = ""
    for _ in range(4):
        if not lock.locked():
            print("Getch waiting")
            key = getch()
            print("Got key", key)
            captured += key.decode("latin-1")
    print("workder", captured)

Thread(target=workder).start()
print(input())
with lock:
    print("Lock acquired")
    print("main", input())
