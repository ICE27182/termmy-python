
# FIXME How should press down and up be handled? 
#     Raw (Pressed down until next key)
# FIXME HUGE PROBLEM: getch changes the terminal io settings, making print in
# another thread behave strangely. Bascially, print in the main thread is not
# as useable.
#     Refactor
from .exceptions import *
from .getch import GetchType, GETCH_TYPE, getch, getch_timeout
from .keys import Key, KeyEvent, ModifierState
from .constants import *

from time import time, sleep
from collections import deque
from copy import copy
from threading import Thread

g_key_event: KeyEvent | None = None
g_is_recording: bool = False
# recording_being_recorded will only contain values when is_replaying is True
g_recording_being_recorded: deque[KeyEvent] | None = None
g_recording_being_replayed: deque[KeyEvent] | None = None
g_playback_speed: float = 1.0

g_key_mapping = copy(ASCII_MAPPING)
if GETCH_TYPE == GetchType.Termios:
    g_key_mapping.update(TERMIOS_KEY_MAPPING)
    SEQUENCE_STARTINGS = TERMIOS_SEQUENCE_STARTS
elif GETCH_TYPE == GetchType.Msvcrt:
    g_key_mapping.update(MSVCRT_KEY_MAPPING)
    SEQUENCE_STARTINGS = TERMIOS_SEQUENCE_STARTS
elif GETCH_TYPE == GetchType.Fallback:
    pass
else:
    raise ValueError(f"Unsupported GETCH_TYPE: '{GETCH_TYPE}'")


def get_key() -> Key | None:
    return g_key_event.key

def get_key_event() -> KeyEvent | None:
    return g_key_event

def get_key_mapping() -> dict[str, Key]:
    """
    Return a reference of a dictionary. Key mapping can be customized by
    mutating the dictionary.
    """
    return g_key_mapping

def clear() -> None:
    global g_key_event
    g_key_event = None

def start_recording(latest_n_keys: int | None = None, 
                    playback_speed: float = 1.0) -> None:
    global g_is_recording, g_recording_being_recorded, g_playback_speed
    if g_is_recording:
        raise AlreadyRecordingError("It is recording already. "
                                    "End it first before statring a new "
                                    "recording.")
    g_is_recording = True
    g_recording_being_recorded = deque(maxlen=latest_n_keys)
    g_playback_speed = playback_speed

def end_recording() -> deque[KeyEvent]:
    global g_is_recording, g_recording_being_recorded
    if not g_is_recording:
        raise NotRecordingError("It is not recording right now.")
    g_is_recording = False
    return_value = g_recording_being_recorded
    g_recording_being_recorded = None
    return return_value

def start_replaying(recording: deque[KeyEvent], 
                    playback_speed: float = 1.0) -> None:
    global g_recording_being_replayed, g_playback_speed
    if g_recording_being_replayed:
        raise AlreadyReplayingError("It is replaying already. "
                                    "Stop it first before replaying another "
                                    "recording.")
    g_recording_being_replayed = copy(recording)
    g_playback_speed = playback_speed

def stop_replaying() -> None:
    global g_recording_being_replayed, g_playback_speed
    if not g_recording_being_replayed:
        raise NotReplayingError("It is not replaying right now.")
    g_recording_being_replayed = None
    g_playback_speed = 1.0


def _read_keyboard(control_sequence_cutoff_time: float = 0.05) -> None:
    char: None | str = None
    # Though input function cannot capture control + C, it will treat
    # control + C as a normal KeyboardInterrupt.
    while char != "\x03":
        if g_recording_being_replayed:
            recorded_key_event = g_recording_being_replayed.popleft()
            _set_key_event(recorded_key_event.key)
            # NOTE Now the key WON'T chang e to None before next iteration
            sleep(
                (g_recording_being_replayed[0].timestamp
                 - recorded_key_event.timestamp) * g_playback_speed
                if g_recording_being_replayed
                else 0.0
            )
            continue
        else:
            char = getch()
            key_press_time = time()
            if GETCH_TYPE == GetchType.Fallback:
                if char == "":
                    char = "\r"
                else:
                    char = char[-1]
                if char in g_key_mapping:
                    _set_key_event(g_key_mapping[char], key_press_time)
                # Undefined key input: e.g. ∆, ǎ, \x07F
                else:
                    _set_key_event(Key(char, char), key_press_time)
            # GETCH_TYPE has been assured to be either Termios, Msvcrt or
            # Fallback at the beginning of the file
            else:
                if char in SEQUENCE_STARTINGS:
                    char_cache = [char]
                    time_cache = [key_press_time]
                    while (time() - key_press_time
                           < control_sequence_cutoff_time):
                        #######################################
                        # FIXME esc will require the second key strike to be
                        # available.
                        #     Refactor
                        # # This can be solved by the following code that has
                        # # been commented out because getch_timeout does not
                        # # work with control sequences
                        # # A far from perfect solution would require the user 
                        # # the double click the esc key  
                        char_cache.append(getch())
                        time_cache.append(time())
                        sequence = "".join(char_cache) # NOTE O(n^2)?
                        if sequence in g_key_mapping:
                            _set_key_event(g_key_mapping[sequence], key_press_time)
                            break
                        # k = getch_timeout(control_sequence_cutoff_time)
                        # if k:
                        #     char_cache.append(k)
                        #     time_cache.append(time())
                        #     sequence = "".join(char_cache) # NOTE O(n^2)?
                        #     if sequence in g_key_mapping:
                        #         _set_key_event(g_key_mapping[sequence], key_press_time)
                        #         break
                        #######################################
                    # It may just be the user manually typing esc key and
                    # other keys, or it can be an undefined control sequence.
                    # Treat as individual key presses and replay the cache.
                    # This may lead to a little lag in operation, depending on
                    # `control_sequence_cutoff_time`
                    else:
                        for i, (ch, tm) in enumerate(zip(char_cache, 
                                                         time_cache)):
                            if ch in g_key_mapping:
                                _set_key_event(g_key_mapping[ch], tm)
                            else:
                                _set_key_event(Key(ch, ch), tm)
                            if i < len(time_cache) - 1:
                                sleep(time_cache[i + 1] - tm)
                elif char in g_key_mapping:
                    _set_key_event(g_key_mapping[char], key_press_time)
                # Undefined key input: e.g. ∆, ǎ, \x07F
                else:
                    _set_key_event(Key(char, char), key_press_time)

def _set_key_event(key: Key | None = None, 
                   timestamp: float | None = None) -> None:
    global g_key_event
    g_key_event = KeyEvent(key, timestamp or time())
    if g_is_recording:
        g_recording_being_recorded.append(g_key_event)


Thread(name="keyboard-module-_read_keyboard", target=_read_keyboard).start()
