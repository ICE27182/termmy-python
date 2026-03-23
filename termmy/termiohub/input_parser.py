# TODO
# 1. Add a timeout on parse (necessaryin edge cases: 
#    dfa = State.numbers(is_final=False) and q[0][0] is a number)
# 2. Merge States

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, TypeVar, Generic, Generator
from collections import deque
from re import compile
from itertools import islice, chain

# from termmy.termiohub.input_event import MouseInput, KeyboardInput, InputEvent

def parse(q: deque[tuple[bytes, float]], dfa: State,
          seq_timeout: float, current_time: float) -> tuple[bytes, float] | None:
    """
    Parse the input q with the given DFA. q may be mutated (via popleft).
    
    Args:
        q (deque[tuple[bytes, float]]): The input queue. 
            Each element is a tuple of a single byte and its timestamp. 
            The byte is expected to be an ascii character.
            
        dfa (State): The DFA to parse the input sequence.
        
        seq_timeout (float): If a string is accepted by the DFA, 
            but it is also a prefix that maybe accepted, the parser will
            wait for more input until the timeout expires. If the timeout
            expires, the longest accepted prefix will be returned. 
            In most cases, this only applies to the ESC key.
    """
    # There are the following cases
    # 1. The first characters is not accepted by the DFA, i.e. it is an
    #    unknown character byte (e.g. 0xFF). In this case, we will just
    #    return it as a single-character sequence. One item from q will
    #    be consumed.
    # 2. The first character is accepted by the DFA and it is not a prefix
    #    of any longer sequence that might be accepted (e.g. b'A', b'*'). 
    #    In this case, we will return it. One item from q will be consumed.
    # 3. The first character is accepted by the DFA and it may also be a 
    #    prefix of a longer sequence.
    #    1. If the first character is pressed very recently before the 
    #       seq_timeout and there is no more input, we will put it back and
    #       return None, waiting for more input to arrive. No item from q 
    #       will be consumed.
    #    2. Otherwise, we will try to parse as many input as possible until
    #       there is no more input or the timeout expires. The longest
    #       accepted sequence will be returned. The corresponding number of
    #       items will be consumed from q.
    #    * The ESC case will be handled by 3.2. 
    #    * Normal escape sequences will be handled by 3.1 and 3.2
    #    * Unknown sequences will be handled by 3.2, where the prefix that
    #      passes 3 will at least be returned. At least one item will be 
    #      consumed from q.
    
    if not q:
        return None
    
    char, timestamp = q.popleft()
    state = dfa.single_transit(char[0])
    if state is None or state.is_final and not state.transition:
        return (char, timestamp)
    
    # Below is the case where we are dealing with a potential sequence
    
    chars: list[bytes] = [char]
    timestamps: list[float] = [timestamp]
    
    # Used in the case where the first char may be accepted by the DFA, 
    # but it may also be a prefix of a longer sequence.
    # Most commonly, it is only meant to handle the single ESC key strike,
    # but it should also work for any other similar cases (likely defined
    # by the user)
    if state.is_final and current_time - timestamp > seq_timeout:
        longest_accepted_length = 1
    else:
        longest_accepted_length = 0
    
    while q:
        char, timestamp = q.popleft()
        chars.append(char)
        timestamps.append(timestamp)
        
        if timestamp - timestamps[0] > seq_timeout:
            break # Timeout, return the longest accepted prefix
        
        next_state = state.single_transit(char[0])
        if next_state is None:
            break # No further transition, return the longest accepted prefix
        elif next_state.is_final:
            longest_accepted_length = len(chars)
        state = next_state
    
    # Prepare the output
    if longest_accepted_length > 0:
        out = (b"".join(chars[:longest_accepted_length]), timestamps[0])
    else:
        out = None
    # Revert the unused input
    q.extendleft(zip(reversed(chars[longest_accepted_length::]), 
                         reversed(timestamps[longest_accepted_length::])))
    return out
    


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

        instructions = _expanded_instructions(cons_list)
        
        linkage: int | None = None
        first: int | Callable[[bool], State] | None = next(instructions, None)
        
        match first:
            case None:
                return cls({}, is_final)
            case int():
                root = last_state = cls({}, False)
                linkage = first
            case _ if callable(first):
                root = last_state = first(False)
            case _:
                raise _CONSTRUCTOR_LIST_TYPE_ERROR
        
        for instruction in instructions:
            match instruction:
                case int():
                    if linkage is None:
                        linkage = instruction
                    else:
                        last_state = last_state.link(linkage, State({}, False))
                        linkage = instruction
                case _ if callable(instruction):
                    if linkage is None:
                        raise ValueError("There must be at least one bytes "
                                         "object between constructors")
                    last_state = last_state.link(linkage, instruction(False))
                    linkage = None
                case _:
                    raise _CONSTRUCTOR_LIST_TYPE_ERROR
        
        if linkage is not None:
            last_state = last_state.link(linkage, State({}, False))
                    
        last_state.is_final = is_final
        return root
    
    @staticmethod
    def merge(states: list[State]) -> State:
        # BFS from the root of each state
        # `Visited` may come in handy with creating new states
        raise NotImplementedError
    
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



_CONSTRUCTOR_LIST_TYPE_ERROR = TypeError("Constructor list must only "
                                         "contain bytes objects and "
                                         "callables that take a boolean "
                                         "and return a State object")

def _expanded_instructions(
            cons_list: Iterable[bytes | Callable[[bool], State]],
        ) -> Generator[int | Callable[[bool], State], None, None]:
            for ins in cons_list:
                match ins:
                    case bytes(): yield from ins
                    case _ if callable(ins): yield ins
                    case _: raise _CONSTRUCTOR_LIST_TYPE_ERROR


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