"""
This package groups the public API for terminal input parsing and device
events. Import from here to access common types and helpers without reaching
into internal modules.

Exports:
	- PredefinedKeys: Named key constants for matching input. 
 		It is useful to match with the returned value of the 
   		method `TermIOHub.get_input`
	- InputEvent, KeyboardInput, MouseInput: Event models.
	- State: Parser state used by the input parser.
	- get_default_dfa, get_default_keyboard_dfa, get_default_mouse_dfa: 
 		Functions to obtain the default DFAs for input parsing.
	- TermIOHub: High-level interface for terminal IO handling.
"""

from .constants import PredefinedKeys, get_default_dfa
from .constants import get_default_keyboard_dfa, get_default_mouse_dfa
from .input_event import InputEvent, KeyboardInput, MouseInput
from .input_parser import State
from .termiohub import TermIOHub
