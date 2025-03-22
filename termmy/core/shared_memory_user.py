

from __future__ import annotations
from uuid import uuid4
from atexit import register
from signal import SIGINT, SIGTERM, signal
from multiprocessing.shared_memory import SharedMemory

created_shared_memory: dict[str, SharedMemory] = {}

def cleanup_created_shared_memory():
    for shared_memory in created_shared_memory.values():
        shared_memory.close()
        shared_memory.unlink()

register(cleanup_created_shared_memory)
signal(SIGINT, lambda signum, frame: cleanup_created_shared_memory())
signal(SIGTERM, lambda signum, frame: cleanup_created_shared_memory())

class SharedMemoryUser:
    __slots__ = ('size', '_shared_memory')
    def __init__(self, size, name=None):
        self.size = size
        if name in created_shared_memory:
            raise ValueError(f"SharedMemory with name '{name}' already exists.")
        # 31 is sometimes the maxium length of a file name
        name = name or str(uuid4()).replace("-","")[:30]
        try:
            shm = SharedMemory(name, create=False)
            shm.close()
            shm.unlink()
        except FileNotFoundError:
            pass
        try:
            self._shared_memory = SharedMemory(name=name, create=True, size=size)
        except Exception as e:
            if self._shared_memory:
                self._shared_memory.close()
                self._shared_memory.unlink()
            raise e
        created_shared_memory[name] = (self._shared_memory)

    def __del__(self):
        self.cleanup()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
    
    def cleanup(self):
        try:
            if self._shared_memory:
                self._shared_memory.close()
                self._shared_memory.unlink()
                del created_shared_memory[self.name]
        except Exception as e:
            print(f"Error cleaning up shared memory: {e}")

    @property
    def data(self) -> memoryview:
        return self._shared_memory.buf[:self.size]
    @data.setter
    def data(self, data) -> None:
        self._shared_memory.buf[:self.size] = data
    