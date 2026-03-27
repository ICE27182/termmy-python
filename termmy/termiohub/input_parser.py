from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, TypeVar, Generic, Generator, ClassVar
from collections import deque


def parse(q: deque[tuple[bytes, float]], dfa: State,
          seq_timeout: float, latency_timeout: float,
          current_time: float) -> tuple[bytes, float] | None:
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
            
        latency_timeout (float): Timeout for latency issues. All input 
            that is received before the timeout will be discarded.
        
        current_time (float): The current time, used for timeout calculation.
        
    Returns:
        tuple[bytes, float] | None: The accepted sequence and the timestamp
        of the first character in the sequence. If no sequence is accepted,
        None is returned.

    Behavior:
            - If q is empty, return None.
            - If the first byte is not recognized by dfa, return that single byte.
            - If the first byte reaches a terminal state with no outgoing
                transitions, return that single byte immediately.
            - If the first byte is a prefix of a longer candidate sequence,
                parse greedily and return the longest accepted prefix observed
                within seq_timeout.
            - If no accepted prefix is currently available, return None and keep
                input bytes in q for future calls.

    Queue Mutation Contract:
            - q is consumed from the left while parsing.
            - Any bytes not part of the returned sequence are pushed back to the
                front of q in original order.
            - When returning None, all bytes examined for this parse attempt are
                restored to q.

    Timeouts:
            - seq_timeout controls ambiguity resolution for prefix states. The
                parser waits for more bytes while a longer match is still possible.
            - latency_timeout drops stale input: if the oldest candidate byte is
                older than latency_timeout, that candidate is discarded and parsing
                continues from newer input.
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
    #
    # For the timeout sequences, we will still parse the input, even though
    # the first character may have already passed the timeout. This is to
    # handle the case where the first character may be timed out but the 
    # rest of the sequence is still valid, leading to a broken sequence
    # that should have been dumped being treated as separate characters /
    # unknown sequences.
    
    if not q:
        return None
    
    char, timestamp = q.popleft()
    state = dfa.single_transit(char[0])
    if state is None or state.is_final and not state.transition:
        if current_time - timestamp > latency_timeout:
            return parse(q, dfa, seq_timeout, latency_timeout, current_time)
        else:
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
    
    if current_time - timestamps[0] > latency_timeout:
        return parse(q, dfa, seq_timeout, latency_timeout, current_time)
    else:
        return out


@dataclass(slots=True, frozen=False)
class State:
    _counter: ClassVar[int] = 0
    transition: dict[int, State]
    is_final: bool
    
    def to_str(self, indentation: str = "|" + " " * 5, 
               *, 
               depth: int = 0, 
               visited: _Visited[State] | None = None) -> str:
        """
        Return a string representation of the state and its reachable states.
        
        Args:
            indentation (str): 
                The string used for indentation. Default is "|     ".
            depth (int): 
                The current depth of the state in the state machine.
            visited (Visited[State] | None): 
                A Visited object to keep track of visited states for 
                cycle detection.
        
        Example:
            `b"ICE"` is accepted by:
            ```
            State 0  {
            |     'I': State 1  {
            |     |     'C': State 2  {
            |     |     |     'E': State 3 Final {}
            |     |     }
            |     }
            }
            ```
            `b"(271, 828)"` is accepted by:
            ```
            State 0  {
            |     '(': State 1  {
            |     |     '0': ... (1),
            |     |     '1': ... (1),
            |     |     '2': ... (1),
            |     |     '3': ... (1),
            |     |     '4': ... (1),
            |     |     '5': ... (1),
            |     |     '6': ... (1),
            |     |     '7': ... (1),
            |     |     '8': ... (1),
            |     |     '9': ... (1),
            |     |     ',': State 2  {
            |     |     |     ' ': State 3  {
            |     |     |     |     '0': ... (3),
            |     |     |     |     '1': ... (3),
            |     |     |     |     '2': ... (3),
            |     |     |     |     '3': ... (3),
            |     |     |     |     '4': ... (3),
            |     |     |     |     '5': ... (3),
            |     |     |     |     '6': ... (3),
            |     |     |     |     '7': ... (3),
            |     |     |     |     '8': ... (3),
            |     |     |     |     '9': ... (3),
            |     |     |     |     ')': State 4  {}
            |     |     |     }
            |     |     }
            |     }
            }
            ```
        """
        visited = _Visited() if visited is None else visited
        visited.add(self)
        is_final = self.is_final
        indent = indentation * depth
        indent_ = indentation * (depth + 1)
        
        if self.transition:
            return (
                f"State {visited[self]} {"Final" if is_final else ""} "
                f"{{\n{indent_}"
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
        """
        Construct a state machine with given byte sequence.
        
        Args:
            seq (bytes): 
                The byte sequence from which the state machine
                is constructed.
            is_final (bool): 
                Whether the last state of the chain should be a final state.
                Default is True. 
                - If this is True, then the state machine will accept the 
                given sequence
                - If it is False, then the state machine will not accept the 
                given sequence directly. It is useful in state machine 
                construction.
        
        Example:
            `State.from_bytes(b"ICE")` will construct a state machine that
            accepts `b"ICE"` and has the following structure:
            ```
            State 0  {
            |     'I': State 1  {
            |     |     'C': State 2  {
            |     |     |     'E': State 3 Final {}
            |     |     }
            |     }
            }
            ```
        """
        
        root = cls({}, is_final=False)
        state = root
        for b in seq:
            state.transition[b] = State({}, False)
            state = state.transition[b]
        state.is_final = is_final
        return root
    
    @classmethod
    def numbers(cls, is_final: bool = False) -> State:
        """
        Construct a state machine for any length of numbers. It is equivalent
        to this regex `[0-9]*`.
        
        Args:
            is_final (bool): Whether the state machine should accept the
                empty sequence. Default is False. This method is typically
                used in state machine construction.
        Returns:
            State: The root state of the state machine. Depending on the 
                value of `is_final`, the output is either
                ```
                State 0  {
                |     '0': ... (0),
                |     '1': ... (0),
                |     '2': ... (0),
                |     '3': ... (0),
                |     '4': ... (0),
                |     '5': ... (0),
                |     '6': ... (0),
                |     '7': ... (0),
                |     '8': ... (0),
                |     '9': ... (0)
                }
                ```
                or
                ```
                State 0 Final {
                |     '0': ... (0),
                |     '1': ... (0),
                |     '2': ... (0),
                |     '3': ... (0),
                |     '4': ... (0),
                |     '5': ... (0),
                |     '6': ... (0),
                |     '7': ... (0),
                |     '8': ... (0),
                |     '9': ... (0)
                }
                ```
        """
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
            
            is_final (bool): Whether the last state of the chain should be 
                a final state. Default is False. This is useful in state 
                machine construction.
        
        Returns:
            State: The root state of the state machine.
        
        Example:
            `State.from_constructor_list([b'(', State.numbers, b', ', State.numbers, b')'])`
            will construct a state machine that accepts inputs such as
            `b"(271, 828)"` and has the following structure:
            ```
            State 0  {
            |     '(': State 1  {
            |     |     '0': ... (1),
            |     |     '1': ... (1),
            |     |     '2': ... (1),
            |     |     '3': ... (1),
            |     |     '4': ... (1),
            |     |     '5': ... (1),
            |     |     '6': ... (1),
            |     |     '7': ... (1),
            |     |     '8': ... (1),
            |     |     '9': ... (1),
            |     |     ',': State 2  {
            |     |     |     ' ': State 3  {
            |     |     |     |     '0': ... (3),
            |     |     |     |     '1': ... (3),
            |     |     |     |     '2': ... (3),
            |     |     |     |     '3': ... (3),
            |     |     |     |     '4': ... (3),
            |     |     |     |     '5': ... (3),
            |     |     |     |     '6': ... (3),
            |     |     |     |     '7': ... (3),
            |     |     |     |     '8': ... (3),
            |     |     |     |     '9': ... (3),
            |     |     |     |     ')': State 4  {}
            |     |     |     }
            |     |     }
            |     }
            }
            ```
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
    
    @classmethod
    def accepts(cls, accepted: Iterable[bytes]) -> State:
        """
        Construct a state machine that accepts all the given byte sequences.
        """
        return State.merge(*(cls.from_bytes(seq) for seq in accepted))
    
    @staticmethod
    def merge(*states: State) -> State:
        """
        Merges multiple states into their union. 
        
        The output does not involve any references to the input states so
        this function will not have any side effects on the input states.
        """
        return _merge_states(*states)
    
    def link(self, symbol: int, target: State) -> State:
        """
        Link the target state to the current state with the given input.
        
        It is expected (though not enforced) that `symbol` is a byte value 
        that represent a character in the input sequence (0-127).
        
        Return the **target state** for chaining.
        """
        if symbol in self.transition:
            raise ValueError(f"Transition for {symbol} already exists")
        self.transition[symbol] = target
        return target
    
    def last_of_the_chain(self, ignore_self_loops: bool = False) -> State:
        """
        Transits through the chain of states until it reaches a state where
        there are more than one transitions or no transition at all.
        The state will then be returned.
        
        Args:
            ignore_self_loops (bool): Whether to ignore self loops when
                determining the end of the chain.
        """
        state = self
        if ignore_self_loops:
            while True:
                i = iter(n for n in state.transition.values() if n is not state)
                s = next(i, None)
                if s is None:
                    return state # No transition or only self loop
                elif next(i, None) is not None:
                    return s # More than one transition
                state = s
        else:
            while len(state.transition) == 1:
                state = next(iter(state.transition.values()))
        return state
            
    def single_transit(self, symbol: int) -> State | None:
        return self.transition.get(symbol)
    
    def multi_transit(self, symbol: bytes) -> State | None:
        state = self
        for b in symbol:
            state = state.single_transit(b)
            if state is None:
                return None
        return state
    
    def single_transit_(self, symbol: int) -> State:
        """
        Raises:
            KeyError: If there is no transition for the given symbol.
        """
        state = self.single_transit(symbol)
        if state is None:
            raise KeyError(f"No transition for {symbol}")
        return state
    
    def multi_transit_(self, symbol: bytes) -> State:
        """
        Raises:
            KeyError: If there is no transition for the given symbol.
        """
        state = self
        for b in symbol:
            state = state.single_transit_(b)
        return state
    
    

################################################################
# 
# Helper functions & Classes
#
################################################################

################################################################
# runtime-id-based-hashable dict with unique 0-based id allocation
################################################################

T = TypeVar("T")

@dataclass(slots=True, frozen=False)
class _Visited(Generic[T]):
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

################################################################
# State.from_constructor_list
################################################################

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

################################################################
# State.merge
################################################################

type _HashableState = tuple[int | None, ...]
type _States = tuple[State | None, ...]

def _merge_states(*states: State) -> State:
    # Yes i have given up naming stuff after fighting with this function
    # for hours only to find that the implementation is so simple
    #
    # Just a simple dfs
    #
    # Looking at the helper functions inside. I want to inline them so much
    # (with an inliner of course). A simple ast replacemen will already do
    # the job since all but `dfs` are JUST expressions
    #
    # u know what. I think i have decided. I'm going to call them 
    # "Just expressions", in comparison to the "pure functions" that are
    # actually pure in a functional langauge like haskell. "Just" comes 
    # from the type Maybe in haskell, which is a Functor, Applicative, 
    # Monad and Alternative :)))))))
    visited_states: _Visited[State] = _Visited()
    asssignment: dict[_HashableState, State] = {}
    visited_transitions: set[_HashableState] = set()
    
    def symbols_of(states: _States) -> set[int]:
        return set().union(*(s.transition.keys() 
                             for s in states 
                                if s is not None))

    def goodevening(states: _States) -> _HashableState:
        return tuple(None if s is None else visited_states.get(s)
                     for s in states)

    def mercycourt(symbol: int, 
                   states: _States) -> _HashableState:
        return (symbol, *(goodevening(states)))

    def pizza(states: _States) -> State:
        return asssignment[goodevening(states)]

    def massive_transit(symbol: int, 
                        states: _States) -> _States:
        return tuple(None if s is None else s.single_transit(symbol)
                     for s in states)

    def is_final(states: _States) -> bool:
        return any(s.is_final for s in states if s is not None)
    
    def dfs(states: _States) -> None:
        evening = goodevening(states)
        
        if evening in asssignment:
            return
        
        asssignment[evening] = State({}, is_final=is_final(states))
        
        for symbol in symbols_of(states):
            neighbor = massive_transit(symbol, states)
            
            if mercycourt(symbol, states) not in visited_transitions:
                visited_transitions.add(mercycourt(symbol, states))
                dfs(neighbor)
                pizza(states).link(symbol, pizza(neighbor))
                
    dfs(states)
    return pizza(states)

################################################################
# For Debugging
################################################################

def in_one_row(sep: str, *args: str, middle: bool = True, wraping_columns: int | None = None) -> str:
    splited = [a.split('\n') for a in args]
    height = max(map(len, splited))
    widths = [max(map(len, a)) for a in splited]
    
    if wraping_columns is not None:
        if max(widths) > wraping_columns:
            raise ValueError("Impossible to fit the content in the given wraping columns")
        accum = 0
        for i, w in enumerate(widths):
            if accum + w > wraping_columns:
                return (in_one_row(sep, *args[:i], middle=middle) + "\n" +
                        in_one_row(sep, *args[i:], middle=middle, wraping_columns=wraping_columns))
            accum += w + len(sep) * (i > 0)
            
    if middle:
        for i, a in enumerate(splited):
            s = height - len(a)
            splited[i] = [''] * (s // 2 - s % 1) + a + [''] * (s // 2)
    else:
        splited = [a + [''] * (height - len(a)) for a in splited]
        
    out = []
    for lines in zip(*splited):
        out.append(sep.join((s + ' ' * (w - len(s)) for s, w in zip(lines, widths))))
    return "\n".join(out)


if __name__ == "__main__":
    n = State.numbers
    mouse_move = State.from_constructor_list([b"\x1b[<", n, b";", n, b";", n], is_final=False)
    
    mouse_move.multi_transit_(b"\x1b[<0;0;0").link(ord('m'), State({}, is_final=True))
    mouse_move.multi_transit_(b"\x1b[<0;0;0").link(ord('M'), State({}, is_final=True))
    
    others = [
        b"\x1bOQ",
        b"\x1bOS",
        b"\x1b[A",
        b"\x1b[D",
        b"\x1b[B",
        b"\x1b[C",
        b"\r",
        b"\x15",
        b"\x7f",
        b"\x1b",
        b"\r",
        b"\x03",
        b"\x04",
        b"\x08",
        b"\x01",
        b"\x05",
        *map(lambda x: str(x).encode(), range(10)),
    ]
    state = State.merge(mouse_move, *map(State.from_bytes, others))
    
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
        b"\x1b[<0;88;16m",
        b"\x1b[<35;89;16M",
        *others,
    ]
    for seq in seqs:
        assert state.multi_transit(seq) is not None
        
    from string import ascii_lowercase
    for seq in ascii_lowercase:
        assert state.multi_transit(seq.encode()) is None
