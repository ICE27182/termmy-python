

from .getch import GetchType, GETCH_TYPE, getch
from .keys import Key, KeyEvent
from .key_constants import TERMIOS_KEY_MAPPING, TERMIOS_SEQUENCE_STARTS
from .key_constants import MSVCRT_KEY_MAPPING, MSVCRT_SEQUENCE_STARTS
from .key_constants import ASCII_MAPPING, FALLBACK_KEY_MAPPING
from .keyboard_recording import KeyboardRecording
from .keyboard_recording import AlreadyRecordingError, NotRecordingError

from time import time, sleep
from collections import deque
from threading import Lock, Thread
from copy import copy
from contextlib import contextmanager

if GETCH_TYPE == GetchType.Termios:
    import tty, termios
    from .getch import _FD, _OLD_SETTINGS
    from sys import stdin
    import builtins
    _ORIGINAL_PRINT = builtins.print

g_key_mapping = copy(ASCII_MAPPING)
if GETCH_TYPE == GetchType.Termios:
    g_key_mapping.update(TERMIOS_KEY_MAPPING)
    g_sequence_startings = set(TERMIOS_SEQUENCE_STARTS)
elif GETCH_TYPE == GetchType.Msvcrt:
    g_key_mapping.update(MSVCRT_KEY_MAPPING)
    g_sequence_startings = set(MSVCRT_SEQUENCE_STARTS)
elif GETCH_TYPE == GetchType.Fallback:
    g_key_mapping.update(FALLBACK_KEY_MAPPING)
    g_sequence_startings = set()
else:
    raise ValueError(f"Unsupported GETCH_TYPE: '{GETCH_TYPE}'")

g_read_keyboard: bool = False
g_io_lock = Lock()

g_get_key_event_lock = Lock()
g_key_buffer: deque[tuple[str, float]] = deque()

g_recording: KeyboardRecording | None = None
# Only used in get_key_event
# See the function for more details
g_pending_future_key_event: KeyEvent | None = None


@contextmanager
def read_keyboard(exit_prompt: str | bool = True):
    """
    Context manager to read keyboard input.

    A RuntimeError will be raised if it is used within the 
    `read_keyboard` context.

    `get_key_event`, `get_key`, `start_recording`, `end_recording` 
    and `replay`  must be called within the context.

    recording will be stopped when the context exits.

    Generally, you need to press enter to exit the context.
    It will block until the key is pressed due to internal implementation.
    You can use `exit_prompt` to setup prompt to acknowledge the user.

    `exit_prompt` can be a string, or a boolean. When the context exits:
        string -> Prompts the string  
        True -> Prompts "Press enter to exit ..."
        False -> no prompt will be printed.
    """
    global g_read_keyboard
    # Check existing context
    if g_read_keyboard:
        raise RuntimeError("Already in the context of `read_keyboard`.")
    # Setup thread
    keyboard_reading_thread = Thread(target=_read_keyboard, daemon=False)
    try:
        if GETCH_TYPE == GetchType.Termios:
            from .safe_io import safe_print
            tty.setraw(_FD)
            builtins.print = safe_print
        g_read_keyboard = True
        keyboard_reading_thread.start()
        yield
    finally:
        if g_recording:
            end_recording()
        g_read_keyboard = False
        g_key_buffer.clear()
        if not g_read_keyboard and exit_prompt:
            if exit_prompt == True:
                print("Press enter to exit ...")
            else:
                print(exit_prompt)
        keyboard_reading_thread.join()
        if GETCH_TYPE == GetchType.Termios:
            termios.tcsetattr(_FD, termios.TCSADRAIN, _OLD_SETTINGS)
            builtins.print = _ORIGINAL_PRINT


def get_key_event(key_buffer_timeout: float = 0.2, 
                  sequence_timeout: float = 0.125) -> KeyEvent | None:
    """
    Get a key event (key with a timestamp) from the keyboard or the recording
    currently replaying. It must becalled within the context of `read_keyboard`.

    Key presses before key_buffer_timeout will be ignored. 
    Return None if the buffer is empty.

    `sequence_timeout` decide how far apart can key presses be to still be
    considered as a control sequence. For example, if a '\\x1b' is received
    10 seconds before receiving a 'B', then it will not be considered as a
    'down'.

    Note that key modifiers such as shift and control will be speculated based
    on an American/International keyboard layout and thus may be incorrect.

    Control keys such as escape, left, F1, etc. only have limited supports on
    certain platforms. Windows, macos and linux have better supports. You can
    always update/delete keymapping with `update_key_mapping` and
    `remove_key_mapping`.

    Unrecognized keys / sequences will be read as (separated) keys. Each such
    key will have all its modifiers set to Modifirer.Unknown and it will have
    exactly one character for both `name` and `code` attributes.
    """
    # A simple workaround to support recording replay
    # With the global variable :(, I dont have to refactor get_key_event and
    # _get_sequence to accommodate future keys. I can just store it in the 
    # global variable if a key turns out to be a future key.
    # The cost is using a global variable.
    global g_pending_future_key_event

    if not g_read_keyboard:
        raise RuntimeError("`get_key_event` must be called within the context"
                           " of `read_keyboard`")

    with g_get_key_event_lock:
        if g_pending_future_key_event:
            # In the past or at present
            if g_pending_future_key_event.timestamp <= time():
                g_pending_future_key_event = None
                # Return it if it is not too old
                if g_pending_future_key_event.timestamp > time() - key_buffer_timeout:
                    key_event = g_pending_future_key_event
                    return key_event
            # Still in the future
            else:
                return None
        # Oo g_future_key_event_buffer or it has expired
        while g_key_buffer:
            raw_key, timestamp = g_key_buffer.popleft()
            if raw_key in g_sequence_startings:
                key = _get_sequence(raw_key, timestamp, sequence_timeout)
            else:
                key = g_key_mapping.get(raw_key)
            # Check timestamp after getting `key` so we can be sure the whole
            # sequence will be ignored, as by now, all keys from a 
            # sequence have already been popped out from the key buffer
            if timestamp < time() - key_buffer_timeout:
                continue # Ignore and enter the next iteration
            # Unknown characters such as ®, ∆, ≤
            # Unknown sequence will be handled by `_get_sequence`
            key_event = (KeyEvent(key, timestamp) if key 
                         else KeyEvent(Key.unknown_key(raw_key), timestamp))
            # A part of a recording
            if timestamp > time():
                g_pending_future_key_event = key_event
                return None
            else:
                return key_event
        else:
            return None

def get_key(key_buffer_timeout: float = 0.2, 
            sequence_timeout: float = 0.125) -> Key | None:
    """
    Get a key from the keyboard or the recording currently replaying. 
    It must becalled within the context of `read_keyboard`.

    Key presses before key_buffer_timeout will be ignored. 
    Return None if the buffer is empty.

    `sequence_timeout` decide how far apart can key presses be to still be
    considered as a control sequence. For example, if a '\\x1b' is received
    10 seconds before receiving a 'B', then it will not be considered as a
    'down'.

    Note that key modifiers such as shift and control will be speculated based
    on an American/International keyboard layout and thus may be incorrect.

    Control keys such as escape, left, F1, etc. only have limited supports on
    certain platforms. Windows, macos and linux have better supports. You can
    always update/delete keymapping with `update_key_mapping` and
    `remove_key_mapping`.

    Unrecognized keys / sequences will be read as (separated) keys. Each such
    key will have all its modifiers set to Modifirer.Unknown and it will have
    exactly one character for both `name` and `code` attributes.
    """
    if not g_read_keyboard:
        raise RuntimeError("`get_key` must be called within the context"
                           " of `read_keyboard`")
    key_event: KeyEvent | None = get_key_event(key_buffer_timeout, 
                                               sequence_timeout)
    return key_event.key if key_event else None


def update_key_mapping(key_mapping: dict[str, Key]) -> None:
    """
    Customize how `get_key_event` and `get_key` react to your input and add
    support for more key mappings. 
    
    The keys of `key_mapping` should be the raw input the terminal sents after
    receiving your keyboard input. 
    E.g. {"a": Key("a", "a"), 
          "\\x1b": Key("escape", "\\033"), 
          "\\x00\\x3b": Key("F1", "\\x00\\x3b")}

    You can remove existing mappings with `remove_key_mapping`.
    """
    for raw_input in key_mapping:
        if len(raw_input) > 1 and raw_input[0] not in g_sequence_startings:
            g_sequence_startings |= {raw_input[0]}
    g_key_mapping.update(key_mapping)

def remove_key_mapping(raw_input: str):
    """
    Customize how `get_key_event` and `get_key` react to your input by
    removing certain mappings.

    `raw_input` should be the raw input the terminal sents after
    receiving your keyboard input. 
    E.g. "a", "\\x1b", "\\x00\\x3b"
    
    A ValueError will raise if `raw_input` does not exist.
    
    You can modify existing mappings 
    or add new mappings with `remove_key_mapping`.
    """
    if raw_input in g_key_mapping:
        del g_key_mapping[raw_input]
    else:
        raise ValueError(f"`{raw_input}` does not exist in the key mapping.")
    # Cleanup g_sequence_startings if the removed key mapping has a unique 
    # starting
    starting = raw_input[0]
    if (len(raw_input) > 1 
        and not any(r.startswith(starting) for r in g_key_mapping.keys())):
        del g_sequence_startings[starting]

def get_key_mapping_view() -> dict[str, Key]:
    """
    Return a dictionary of current key mapping between raw key code and
    resulted key. 
    
    Changing the returned dictionary WILL NOT affect the internal key 
    mapping. Use `update_key_mapping` or `remove_key_mapping` if you want to
    change how inputs are mapped to the key you get from `get_key_event` and
    `get_key`.
    """
    # copy should be good enough and there is no need to use deepcopy because
    # both str and Key are immutable.
    return copy(g_key_mapping)

def start_recording() -> None:
    """
    Start recording keyboard events. 

    It must be called within the context of `read_keyboard`.

    Recording will stop when `end_recording` is called or when the context
    exits.
    """
    if not g_read_keyboard:
        raise RuntimeError("`start_recording` must be called within the "
                           "context of `read_keyboard`")
    global g_recording
    if g_recording is not None:
        raise AlreadyRecordingError()
    g_recording = KeyboardRecording()

def end_recording(trauncate_num_raw_key_events: int = 0) -> KeyboardRecording:
    """
    End the current recording and return the recorded keyboard events.

    :param truncate_num_raw_key_events: Number of raw key events to remove 
    from the recording. This is useful to remove the key presses that ends
    the recording. It must be the number of raw key events, not just the
    number of keys. For a control sequence, one key corresponds to multiple
    character inputs.

    It must be called within the context of `read_keyboard`.
    """
    if not g_read_keyboard:
        raise RuntimeError("`end_recording` must be called within the "
                           "context of `read_keyboard`")
    global g_recording
    if g_recording is None:
        raise NotRecordingError()
    g_recording.set_end_time()
    g_recording.pop(trauncate_num_raw_key_events)
    recording = g_recording
    g_recording = None
    return recording

def replay(recording: KeyboardRecording, playback_speed: float = 1.0) -> None:
    """
    Replay the recording at provided playback speed. Playback speed must be a
    positive number.

    It must be called within the context of `read_keyboard`.

    Note that once replay starts, all keyboard inputs will be ignored until
    the end of the recording and you cannot stop or pause it.
    """
    if not g_read_keyboard:
        raise RuntimeError("`replay` must be called within the "
                           "context of `read_keyboard`")
    recording.replays(g_key_buffer, playback_speed)

def is_recording() -> bool:
    return bool(g_recording)


def _get_sequence(starting: str, timestamp: float, 
                  sequence_timeout: float) -> Key:
    """
    Read a control sequence from `g_key_buffer`. 
    
    It will not return None because it can at least return the starting key,
    which may be an escape on a unix-like platform, or an unrecognized key.
    """
    pushback: list[str, float] = []
    sequence = starting
    while True :
        # Wait if key buffer is empty
        if not g_key_buffer:
            wait_time = timestamp + sequence_timeout - time()
            if wait_time > 0:
                sleep(wait_time)
            # Timeout (maybe just a regular escape key)
            if not g_key_buffer:
                break
        next_key = g_key_buffer.popleft()
        pushback.append(next_key)
        # += should be faster than 
        # using "".join(seq_list) and seq_list.append(next_key)
        # because while join is faster as a string buffer in string building,
        # it is probably slower when we need to access the string in every
        # iteration. 
        # In this case, we then need to join the buffer in every single
        # iteration, leading to the same time complexity O(n^2) as +=, while
        # introducing list & join overheads.
        # Ideally, we can use a tree for the candidates and check for match
        # character by character, but since there is no such builtin data
        # structure, and implementing it in python to solve such low scale
        # problem will probably make it considerally slower than even the join
        # method, it's better to keep it this way i think.
        sequence += next_key[0]
        candidates = {candidate 
                      for candidate in g_key_mapping.keys() 
                      if candidate.startswith(sequence)}
        if not candidates:
            break
        elif sequence in candidates:
            return g_key_mapping[sequence]
    # Skip the first element and push back backwards
    for raw_key_event in reversed(pushback[1:]):
        g_key_buffer.appendleft(raw_key_event)
    return (g_key_mapping[starting] 
            if starting in g_key_mapping 
            else Key.unknown_key(starting))


def _read_keyboard() -> None:
    """
    Target function
    """
    if GETCH_TYPE == GetchType.Fallback:
        while g_read_keyboard:
            raw_input, timestamp = getch(), time()
            raw_key = raw_input[-1] if raw_input else ""
            raw_key_event = (raw_key, timestamp)
            g_key_buffer.append((raw_key, timestamp))
            if g_recording:
                g_recording.records(raw_key_event)
    elif GETCH_TYPE == GetchType.Msvcrt:
        
        while g_read_keyboard:
            if not g_io_lock.locked():
                raw_key_event = (getch(), time())
                g_key_buffer.append(raw_key_event)
                if g_recording:
                    g_recording.records(raw_key_event)
    elif GETCH_TYPE == GetchType.Termios:
        while g_read_keyboard:
            if not g_io_lock.locked():
                # inlined getch to avoid switching back and forth between
                # terminal modes
                raw_key_event = (stdin.read(1), time())
                with g_io_lock:
                    g_key_buffer.append(raw_key_event)
                    if g_recording:
                        g_recording.records(raw_key_event)
            else:
                sleep(0.03)
