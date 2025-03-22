from struct import Struct
from shared_memory_user import SharedMemoryUser
from collections.abc import Sequence, Iterator

class HomogeneousArray(SharedMemoryUser, Sequence):
    __slots__ = ("max_length", "struct")
    def __init__(self, max_length: int, fmt: str):
        self.max_length = max_length
        self.struct = Struct(fmt)
        super().__init__(max_length * self.struct.size)

    def __getitem__(self, index: int):
        start = index * self.item_size
        data = self._shared_memory.buf[:self.size]
        return self.struct.unpack(data[start:start + self.item_size])
    def __setitem__(self, index: int, value):
        start = index * self.struct.size
        data = self._shared_memory.buf[:self.size]
        data[start:start + self.struct.size] = self.struct.pack(*value)
    
    def __len__(self) -> int:
        return self.max_length
    
    def __iter__(self) -> Iterator:
        return self.struct.iter_unpack(self.data)
