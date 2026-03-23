from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, TypeVar, Generic
from collections import deque
from re import compile
from itertools import islice

# from termmy.termiohub.input_event import MouseInput, KeyboardInput, InputEvent

def parse(q: deque[tuple[bytes, float]], seq_timeout: float, 
           current_time: float) -> InputEvent | None:
    if not q:
        return None
    
    char, timestamp = q.popleft()
    char = char.decode("latin-1")


T = TypeVar("T")
@dataclass(slots=True, frozen=False)
class Visited(Generic[T]):
    visited: dict[int, int] = field(default_factory=dict)
    counter: int = 0
    
    def __contains__(self, item: T) -> bool:
        return id(item) in self.visited
    
    def __getitem__(self, item: T) -> int:
        v = self.visited.get(id(item))
        if v is None:
            raise KeyError(item)
        return v
    
    def __setitem__(self, key: T, value: int) -> None:
        self.visited[id(key)] = value
    
    def get(self, item: T) -> int:
        """Return the unique id of the item
        A new id will be allocated if its not visited before"""
        v = self.visited.get(id(item))
        if v is None:
            v = self.counter
            self.visited[id(item)] = v
            self.counter += 1
        return v
    
    def add(self, item: T) -> None:
        """Add the item to visited and return its unique id
        If the item is already visited, raise KeyError"""
        if id(item) in self.visited:
            return
        v = self.counter
        self.visited[id(item)] = v
        self.counter += 1
    

@dataclass(slots=True, frozen=False)
class State:
    transition: dict[int, State]
    is_final: bool
    
    def to_str(self, indentation: str = "|" + " " * 5, 
               *, depth: int = 0, visited: Visited | None = None) -> str:
        visited = Visited() if visited is None else visited
        visited.add(self)
        is_final = self.is_final
        indent = indentation * depth
        indent_ = indentation * (depth + 1)
        
        if self.transition:
            return (
                f"State {visited[self]} {"Final" if is_final else ""} {{\n{indent_}"
                + f",\n{indent_}".join(
                    f"{(repr(chr(c)))}: " + (
                        f"... ({visited[s]})"
                        if s in visited
                        else f"{s.to_str(indentation, depth = depth + 1, 
                                         visited = visited)}"
                    )
                    for c, s in self.transition.items()
                )
                + f"\n{indent}}}"
            )
        else:
            return f"State {visited[self]} {"Final" if is_final else ""} {{}}"
    
    @classmethod
    def from_bytes(cls, seq: bytes, is_final: bool = True) -> State:
        root = cls({}, is_final=False)
        state = root
        for b in seq:
            state.transition[b] = State({}, False)
            state = state.transition[b]
        state.is_final = is_final
        return root
    
    @classmethod
    def numbers(cls, is_final: bool = False) -> State:
        state = cls({}, is_final)
        for i in range(10):
            state.transition[ord(str(i))] = state
        return state
    
    @classmethod
    def from_constructor_list(
        cls, 
        cons_list: Iterable[bytes | Callable[[bool], State]],
        is_final: bool = False,
    ) -> State:
        """
        Args:
            cons_list (Iterable[bytes | Callable[[bool], State]]):
                A list of bytes objects (and callables) that represent 
                the construction of the state machine.
                
                Each bytes objects represents a chain of states with 
                one transition per byte.
                
                Each callable is a state constructor that takes a boolean
                indicating whether the state is final or not and returns
                a State object.
                
                After each callable, except the callable at the end of the
                list, there must be at least one bytes object that indicates
                the transition condition. This is enforced because the idea
                is that constructor list represents a chain.
        
        Returns:
            State: The root state of the state machine.
        """         
        if not cons_list: 
            return cls({}, True)
        
        last_was_callable = False
        root = cls({}, False)
        state = root
        
        for instruction in cons_list:
            match instruction:
                case bytes():
                    bytes_chain = State.from_bytes(instruction[1:], False)
                    state = (state.link(instruction[0], bytes_chain)
                                    .last_of_the_chain())
                    last_was_callable = False
                case _ if callable(instruction):
                    if last_was_callable:
                        raise ValueError("Constructor list must start "
                                         "with a bytes object")
                    new_state = instruction(False)
                    state.copy_transitions_from(new_state)
                    
                    last_was_callable = True
                case _:
                    raise ValueError("Constructor list must only contain "
                                     "bytes objects and callables")
            print(root.to_str())
                    
        state.is_final = is_final
        return root
    
    def link(self, upon: int, target: State) -> State:
        """
        Link the target state to the current state with the given input.
        
        It is expected (though not enforced) that `upon` is a byte value 
        that represent a character in the input sequence (0-127).
        
        Return the **target state** for chaining.
        """
        if upon in self.transition:
            raise ValueError(f"Transition for {upon} already exists")
        self.transition[upon] = target
        return target
            
    def single_transit(self, upon: int) -> State | None:
        return self.transition.get(upon)
    
    def multi_transit(self, upon: bytes) -> State | None:
        state = self
        print(state.to_str())
        for b in upon:
            print(f"{b} {repr(chr(b))}")
            state = state.single_transit(b)
            if state is None:
                return None
            print(state.to_str())
        return state
    
    def last_of_the_chain(self) -> State:
        state = self
        while len(state.transition) == 1:
            state = next(iter(state.transition.values()))
        return state
    
    def copy_transitions_from(self, state: State) -> None:
        """
        Copy transitions from another state.
        
        Note that it is not a deep copy so after they copy, 
        `self` and `state` can transit to the same state object
        upon the same input.
        """
        if self.transition.keys() & state.transition.keys():
            raise ValueError("Cannot copy transitions from a state that has "
                             "overlapping transition keys")
        self.transition.update(state.transition)

if __name__ == "__main__":
    # Debug from_constructor_list
    mouse_move = State.from_constructor_list([
        b"\x1b[<35;",
        State.numbers,
        b";",
        State.numbers,
        b"M",
    ], is_final=True)
    
    print("\n" + '-' * 99 + "\n")
    
    seqs = [
        b"\x1b[<35;55;21M",
        b"\x1b[<35;56;21M",
        b"\x1b[<35;58;20M",
        b"\x1b[<35;61;19M",
        b"\x1b[<35;68;18M",
        b"\x1b[<35;73;17M",
        b"\x1b[<35;79;17M",
        b"\x1b[<35;83;17M",
        b"\x1b[<35;86;16M",
        b"\x1b[<35;88;16M",
        b"\x1b[<35;89;16M",
    ]
    for seq in seqs:
        assert mouse_move.multi_transit(seq) is not None