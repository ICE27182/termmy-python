from .keys import Key, ModifierState

_UNKNOWN = ModifierState.Unknown
_NO = ModifierState.No
_YES = ModifierState.Yes

################################################################
# Directions
################################################################
UP_TERMIOS = Key("up", "\x1b[A", shift=_UNKNOWN, control=_UNKNOWN, command=_UNKNOWN, option=_UNKNOWN, alt=_NO)
DOWN_TERMIOS = Key("down", "\x1b[B", shift=_UNKNOWN, control=_UNKNOWN, command=_UNKNOWN, option=_UNKNOWN, alt=_NO)
RIGHT_TERMIOS = Key("right", "\x1b[C", shift=_NO, control=_UNKNOWN, command=_UNKNOWN, option=_NO, alt=_NO)
LEFT_TERMIOS = Key("left", "\x1b[D", shift=_NO, control=_UNKNOWN, command=_UNKNOWN, option=_NO, alt=_NO)

RIGHT_OPTION_TERMIOS = Key("right", "\x1bf", shift=_NO, control=_UNKNOWN, command=_UNKNOWN, option=_YES, alt=_NO)
LEFT_OPTION_TERMIOS = Key("left", "\x1bb", shift=_NO, control=_UNKNOWN, command=_UNKNOWN, option=_YES, alt=_NO)

RIGHT_SHIFT_TERMIOS = Key("right", "\x1b[1;2;C", shift=_YES, control=_NO, command=_UNKNOWN, option=_NO, alt=_NO)
LEFT_SHIFT_TERMIOS = Key("left", "\x1b[1;2;D", shift=_YES, control=_NO, command=_UNKNOWN, option=_NO, alt=_NO)

RIGHT_CONTROL_COMMAND_TERMIOS = Key("right", "\x1b[1;5;C", shift=_YES, control=_YES, command=_YES, option=_NO, alt=_NO)
LEFT_CONTROL_COMMAND_TERMIOS = Key("left", "\x1b[1;2;D", shift=_YES, control=_YES, command=_YES, option=_NO, alt=_NO)
# ------------------------------
UP_MSVCRT = Key("up", "\xe0H", shift=_UNKNOWN, control=_NO, command=_NO, option=_NO, alt=_NO)
DOWN_MSVCRT = Key("down", "\xe0P", shift=_UNKNOWN, control=_NO, command=_NO, option=_NO, alt=_NO)
RIGHT_MSVCRT = Key("right", "\xe0M", shift=_UNKNOWN, control=_NO, command=_NO, option=_NO, alt=_NO)
LEFT_MSVCRT = Key("left", "\xe0K", shift=_UNKNOWN, control=_NO, command=_NO, option=_NO, alt=_NO)

UP_CONTROL_MSVCRT = Key("up", "\xe0\x8d", shift=_UNKNOWN, control=_YES, command=_NO, option=_NO, alt=_NO)
DOWN_CONTROL_MSVCRT = Key("down", "\xe0\x91", shift=_UNKNOWN, control=_YES, command=_NO, option=_NO, alt=_NO)
RIGHT_CONTROL_MSVCRT = Key("right", "\xe0t", shift=_UNKNOWN, control=_YES, command=_NO, option=_NO, alt=_NO)
LEFT_CONTROL_MSVCRT = Key("left", "\xe0s", shift=_UNKNOWN, control=_YES, command=_NO, option=_NO, alt=_NO)

UP_ALT_MSVCRT = Key("up", "\x00\x98", shift=_UNKNOWN, control=_UNKNOWN, command=_NO, option=_NO, alt=_YES)
DOWN_ALT_MSVCRT = Key("down", "\x00\xa0", shift=_UNKNOWN, control=_UNKNOWN, command=_NO, option=_NO, alt=_YES)
RIGHT_ALT_MSVCRT = Key("right", "\x00\x9d", shift=_UNKNOWN, control=_UNKNOWN, command=_NO, option=_NO, alt=_YES)
LEFT_ALT_MSVCRT = Key("left", "\x00\x9b", shift=_UNKNOWN, control=_UNKNOWN, command=_NO, option=_NO, alt=_YES)


################################################################
# Tab
################################################################
# control + i will also be \t and there is no way to tell
TAB_TERMIOS = Key("tab", "\t", shift=_NO, alt=_NO)
TAB_SHIFT_TERMIOS = Key("tab", "\t", shift=True, alt=_NO)
# ------------------------------
TAB_MSVCRT = Key("tab", "\t", shift=_UNKNOWN, command=_NO, option=_NO)


################################################################
# Backspace
################################################################
BACKSPACE_TERMIOS = Key("backspace", "\x7f", alt=_NO)
# ------------------------------
BACKSPACE_MSVCRT = Key("backspace", "\x08", command=_NO, option=_NO)


################################################################
# Enter
################################################################
ENTER_TERMIOS = Key("enter", "\r", alt=_NO)
# ------------------------------
ENTER_MSVCRT = Key("enter", "\r", control=_NO, command=_NO, option=_NO)
# control + i will also be \n and there is no way to tell
ENTER_CONTROL_MSVCRT = Key("enter", "\n", control=_YES, command=_NO, option=_NO)
ENTER_CONTROL_ALT_MSVCRT = Key("enter", "\x00\x1c", control=_YES, alt=_YES, command=_NO, option=_NO)


################################################################
# Delete
################################################################
DELETE_TERMIOS = Key("delete", "\x1b[3~", alt=_NO, shift=_NO, control=_NO)
DELETE_SHIFT_TERMIOS = Key("delete", "\x1b[3;2~", alt=_NO, shift=_YES)
DELETE_CONTROL_TERMIOS = Key("delete", "\x1b[3;5~", alt=_NO, shift=_NO, control=_YES)
# ------------------------------
DELETE_MSVCRT = Key("delete", "\xe0S", command=_NO, option=_NO, control=_NO, alt=_NO)
DELETE_CONTROL_MSVCRT = Key("delete", "\xe0\x93", command=_NO, option=_NO, control=_YES, alt=_NO)
DELETE_ALT_MSVCRT = Key("delete", "\x00\xA3", command=_NO, option=_NO, control=_UNKNOWN, alt=_YES)


################################################################
# Escape
################################################################
ESCAPE_TERMIOS = Key("escape", "\x1b", alt=_NO)
# ------------------------------
ESCAPE_MSVCRT = Key("escape", "\x1b", command=_NO, option=_NO)

################################################################
# Fn keys
################################################################
F1_TERMIOS = Key("f1", "\x1bOP", alt=_NO)
F2_TERMIOS = Key("f2", "\x1bOQ", alt=_NO)
F3_TERMIOS = Key("f3", "\x1bOR", alt=_NO)
F4_TERMIOS = Key("f4", "\x1bOS", alt=_NO)
F5_TERMIOS = Key("f5", "\x1b[15~", alt=_NO)
F6_TERMIOS = Key("f6", "\x1b[17~", alt=_NO)
F7_TERMIOS = Key("f7", "\x1b[18~", alt=_NO)
F8_TERMIOS = Key("f8", "\x1b[19~", alt=_NO)
F9_TERMIOS = Key("f9", "\x1b[20~", alt=_NO)
F10_TERMIOS = Key("f10", "\x1b[21~", alt=_NO)
F11_TERMIOS = Key("f11", "\x1b[23~", alt=_NO)
F12_TERMIOS = Key("f12", "\x1b[24~", alt=_NO)
# ------------------------------
F1_MSVCRT = Key("f1", "\x00\x3b", command=_NO, option=_NO)
F2_MSVCRT = Key("f2", "\x00\x3c", command=_NO, option=_NO)
F3_MSVCRT = Key("f3", "\x00\x3d", command=_NO, option=_NO)
F4_MSVCRT = Key("f4", "\x00\x3e", command=_NO, option=_NO)
F5_MSVCRT = Key("f5", "\x00\x3f", command=_NO, option=_NO)
F6_MSVCRT = Key("f6", "\x00\x40", command=_NO, option=_NO)
F7_MSVCRT = Key("f7", "\x00\x41", command=_NO, option=_NO)
F8_MSVCRT = Key("f8", "\x00\x42", command=_NO, option=_NO)
F9_MSVCRT = Key("f9", "\x00\x43", command=_NO, option=_NO)
F10_MSVCRT = Key("f10", "\x00\x44", command=_NO, option=_NO)
F11_MSVCRT = Key("f11", "\xe0\x85", command=_NO, option=_NO)
F12_MSVCRT = Key("f12", "\xe0\x86", command=_NO, option=_NO)



################################################################
# Ascii 0x20 - 0x7E
################################################################
# Second Row on the keyboard
BACKTICK_KEY = Key("`", "`", shift=_NO, option=_NO)
ONE_KEY = Key("1", "1", shift=_NO, option=_NO)
TWO_KEY = Key("2", "2", shift=_NO, option=_NO)
THREE_KEY = Key("3", "3", shift=_NO, option=_NO)
FOUR_KEY = Key("4", "4", shift=_NO, option=_NO)
FIVE_KEY = Key("5", "5", shift=_NO, option=_NO)
SIX_KEY = Key("6", "6", shift=_NO, option=_NO)
SEVEN_KEY = Key("7", "7", shift=_NO, option=_NO)
EIGHT_KEY = Key("8", "8", shift=_NO, option=_NO)
NINE_KEY = Key("9", "9", shift=_NO, option=_NO)
ZERO_KEY = Key("0", "0", shift=_NO, option=_NO)
MINUS_KEY = Key("-", "-", shift=_NO, option=_NO)
EQUAL_KEY = Key("=", "=", shift=_NO, option=_NO)

# Second Row on the keyboard with shift
TILDE_KEY = Key("~", "~", shift=_YES, option=_NO)
EXCLAMATION_KEY = Key("!", "!", shift=_YES, option=_NO)
AT_KEY = Key("@", "@", shift=_YES, option=_NO)
HASH_KEY = Key("#", "#", shift=_YES, option=_NO)
DOLLAR_KEY = Key("$", "$", shift=_YES, option=_NO)
PERCENT_KEY = Key("%", "%", shift=_YES, option=_NO)
CARET_KEY = Key("^", "^", shift=_YES, option=_NO)
AMPERSAND_KEY = Key("&", "&", shift=_YES, option=_NO)
ASTERISK_KEY = Key("*", "*", shift=_YES, option=_NO)
LEFT_PARENTHESIS_KEY = Key("(", "(", shift=_YES, option=_NO)
RIGHT_PARENTHESIS_KEY = Key(")", ")", shift=_YES, option=_NO)
UNDERSCORE_KEY = Key("_", "_", shift=_YES, option=_NO)
PLUS_KEY = Key("+", "+", shift=_YES, option=_NO)

# Alphabet lowercase
A_LOWER_KEY = Key("a", "a", shift=_NO, option=_NO)
B_LOWER_KEY = Key("b", "b", shift=_NO, option=_NO)
C_LOWER_KEY = Key("c", "c", shift=_NO, option=_NO)
D_LOWER_KEY = Key("d", "d", shift=_NO, option=_NO)
E_LOWER_KEY = Key("e", "e", shift=_NO, option=_NO)
F_LOWER_KEY = Key("f", "f", shift=_NO, option=_NO)
G_LOWER_KEY = Key("g", "g", shift=_NO, option=_NO)
H_LOWER_KEY = Key("h", "h", shift=_NO, option=_NO)
I_LOWER_KEY = Key("i", "i", shift=_NO, option=_NO)
J_LOWER_KEY = Key("j", "j", shift=_NO, option=_NO)
K_LOWER_KEY = Key("k", "k", shift=_NO, option=_NO)
L_LOWER_KEY = Key("l", "l", shift=_NO, option=_NO)
M_LOWER_KEY = Key("m", "m", shift=_NO, option=_NO)
N_LOWER_KEY = Key("n", "n", shift=_NO, option=_NO)
O_LOWER_KEY = Key("o", "o", shift=_NO, option=_NO)
P_LOWER_KEY = Key("p", "p", shift=_NO, option=_NO)
Q_LOWER_KEY = Key("q", "q", shift=_NO, option=_NO)
R_LOWER_KEY = Key("r", "r", shift=_NO, option=_NO)
S_LOWER_KEY = Key("s", "s", shift=_NO, option=_NO)
T_LOWER_KEY = Key("t", "t", shift=_NO, option=_NO)
U_LOWER_KEY = Key("u", "u", shift=_NO, option=_NO)
V_LOWER_KEY = Key("v", "v", shift=_NO, option=_NO)
W_LOWER_KEY = Key("w", "w", shift=_NO, option=_NO)
X_LOWER_KEY = Key("x", "x", shift=_NO, option=_NO)
Y_LOWER_KEY = Key("y", "y", shift=_NO, option=_NO)
Z_LOWER_KEY = Key("z", "z", shift=_NO, option=_NO)

# Alphabet uppercase
A_UPPER_KEY = Key("A", "A", shift=_YES, option=_NO)
B_UPPER_KEY = Key("B", "B", shift=_YES, option=_NO)
C_UPPER_KEY = Key("C", "C", shift=_YES, option=_NO)
D_UPPER_KEY = Key("D", "D", shift=_YES, option=_NO)
E_UPPER_KEY = Key("E", "E", shift=_YES, option=_NO)
F_UPPER_KEY = Key("F", "F", shift=_YES, option=_NO)
G_UPPER_KEY = Key("G", "G", shift=_YES, option=_NO)
H_UPPER_KEY = Key("H", "H", shift=_YES, option=_NO)
I_UPPER_KEY = Key("I", "I", shift=_YES, option=_NO)
J_UPPER_KEY = Key("J", "J", shift=_YES, option=_NO)
K_UPPER_KEY = Key("K", "K", shift=_YES, option=_NO)
L_UPPER_KEY = Key("L", "L", shift=_YES, option=_NO)
M_UPPER_KEY = Key("M", "M", shift=_YES, option=_NO)
N_UPPER_KEY = Key("N", "N", shift=_YES, option=_NO)
O_UPPER_KEY = Key("O", "O", shift=_YES, option=_NO)
P_UPPER_KEY = Key("P", "P", shift=_YES, option=_NO)
Q_UPPER_KEY = Key("Q", "Q", shift=_YES, option=_NO)
R_UPPER_KEY = Key("R", "R", shift=_YES, option=_NO)
S_UPPER_KEY = Key("S", "S", shift=_YES, option=_NO)
T_UPPER_KEY = Key("T", "T", shift=_YES, option=_NO)
U_UPPER_KEY = Key("U", "U", shift=_YES, option=_NO)
V_UPPER_KEY = Key("V", "V", shift=_YES, option=_NO)
W_UPPER_KEY = Key("W", "W", shift=_YES, option=_NO)
X_UPPER_KEY = Key("X", "X", shift=_YES, option=_NO)
Y_UPPER_KEY = Key("Y", "Y", shift=_YES, option=_NO)
Z_UPPER_KEY = Key("Z", "Z", shift=_YES, option=_NO)

# The rest symbols
SPACE_KEY = Key(" ", " ", shift=_NO, option=_NO)
LEFT_BRACKET_KEY = Key("[", "[", shift=_NO, option=_NO)
RIGHT_BRACKET_KEY = Key("]", "]", shift=_NO, option=_NO)
BACKSLASH_KEY = Key("\\", "\\", shift=_NO, option=_NO)
LEFT_CURLY_BRACE_KEY = Key("{", "{", shift=_YES, option=_NO)
RIGHT_CURLY_BRACE_KEY = Key("}", "}", shift=_YES, option=_NO)
PIPE_KEY = Key("|", "|", shift=_YES, option=_NO)
SEMICOLON_KEY = Key(";", ";", shift=_NO, option=_NO)
QUOTE_KEY = Key("'", "'", shift=_NO, option=_NO)
COMMA_KEY = Key(",", ",", shift=_NO, option=_NO)
PERIOD_KEY = Key(".", ".", shift=_NO, option=_NO)
SLASH_KEY = Key("/", "/", shift=_NO, option=_NO)
COLON_KEY = Key(":", ":", shift=_YES, option=_NO)
DOUBLE_QUOTE_KEY = Key('"', '"', shift=_YES, option=_NO)
LESS_THAN_KEY = Key("<", "<", shift=_YES, option=_NO)
GREATER_THAN_KEY = Key(">", ">", shift=_YES, option=_NO)
QUESTION_MARK_KEY = Key("?", "?", shift=_YES, option=_NO)

################################################################
# Controls
################################################################
TERMIOS_SEQUENCE_STARTS = ("\x1b",)
MSVCRT_SEQUENCE_STARTS = ("\xe0", "\x00")

TERMIOS_KEY_MAPPING = {
    "\x1b[A": UP_TERMIOS,
    "\x1b[B": DOWN_TERMIOS,
    "\x1b[C": RIGHT_TERMIOS,
    "\x1b[D": LEFT_TERMIOS,
    "\x1bf": RIGHT_OPTION_TERMIOS,
    "\x1bb": LEFT_OPTION_TERMIOS,
    "\x1b[1;2;C": RIGHT_SHIFT_TERMIOS,
    "\x1b[1;2;D": LEFT_SHIFT_TERMIOS,
    "\x1b[1;5;C": RIGHT_CONTROL_COMMAND_TERMIOS,
    "\x1b[1;2;D": LEFT_CONTROL_COMMAND_TERMIOS,
    "\t": TAB_TERMIOS,
    "\t": TAB_SHIFT_TERMIOS,
    "\x7f": BACKSPACE_TERMIOS,
    "\r": ENTER_TERMIOS,
    "\x1b[3~": DELETE_TERMIOS,
    "\x1b[3;2~": DELETE_SHIFT_TERMIOS,
    "\x1b[3;5~": DELETE_CONTROL_TERMIOS,
    "\x1b": ESCAPE_TERMIOS,
    "\x1bOP": F1_TERMIOS,
    "\x1bOQ": F2_TERMIOS,
    "\x1bOR": F3_TERMIOS,
    "\x1bOS": F4_TERMIOS,
    "\x1b[15~": F5_TERMIOS,
    "\x1b[17~": F6_TERMIOS,
    "\x1b[18~": F7_TERMIOS,
    "\x1b[19~": F8_TERMIOS,
    "\x1b[20~": F9_TERMIOS,
    "\x1b[21~": F10_TERMIOS,
    "\x1b[23~": F11_TERMIOS,
    "\x1b[24~": F12_TERMIOS,
}

MSVCRT_KEY_MAPPING = {
    "\xe0H": UP_MSVCRT,
    "\xe0P": DOWN_MSVCRT,
    "\xe0M": RIGHT_MSVCRT,
    "\xe0K": LEFT_MSVCRT,
    "\xe0\x8d": UP_CONTROL_MSVCRT,
    "\xe0\x91": DOWN_CONTROL_MSVCRT,
    "\xe0t": RIGHT_CONTROL_MSVCRT,
    "\xe0s": LEFT_CONTROL_MSVCRT,
    "\x00\x98": UP_ALT_MSVCRT,
    "\x00\xa0": DOWN_ALT_MSVCRT,
    "\x00\x9d": RIGHT_ALT_MSVCRT,
    "\x00\x9b": LEFT_ALT_MSVCRT,
    "\t": TAB_MSVCRT,
    "\x08": BACKSPACE_MSVCRT,
    "\r": ENTER_MSVCRT,
    "\n": ENTER_CONTROL_MSVCRT,
    "\x00\x1c": ENTER_CONTROL_ALT_MSVCRT,
    "\xe0S": DELETE_MSVCRT,
    "\xe0\x93": DELETE_CONTROL_MSVCRT,
    "\x00\xA3": DELETE_ALT_MSVCRT,
    "\x1b": ESCAPE_MSVCRT,
    "\x00\x3b": F1_MSVCRT,
    "\x00\x3c": F2_MSVCRT,
    "\x00\x3d": F3_MSVCRT,
    "\x00\x3e": F4_MSVCRT,
    "\x00\x3f": F5_MSVCRT,
    "\x00\x40": F6_MSVCRT,
    "\x00\x41": F7_MSVCRT,
    "\x00\x42": F8_MSVCRT,
    "\x00\x43": F9_MSVCRT,
    "\x00\x44": F10_MSVCRT,
    "\xe0\x85": F11_MSVCRT,
    "\xe0\x86": F12_MSVCRT,       
}

ASCII_MAPPING = {
    "`": BACKTICK_KEY,
    "1": ONE_KEY,
    "2": TWO_KEY,
    "3": THREE_KEY,
    "4": FOUR_KEY,
    "5": FIVE_KEY,
    "6": SIX_KEY,
    "7": SEVEN_KEY,
    "8": EIGHT_KEY,
    "9": NINE_KEY,
    "0": ZERO_KEY,
    "-": MINUS_KEY,
    "=": EQUAL_KEY,
    "~": TILDE_KEY,
    "!": EXCLAMATION_KEY,
    "@": AT_KEY,
    "#": HASH_KEY,
    "$": DOLLAR_KEY,
    "%": PERCENT_KEY,
    "^": CARET_KEY,
    "&": AMPERSAND_KEY,
    "*": ASTERISK_KEY,
    "(": LEFT_PARENTHESIS_KEY,
    ")": RIGHT_PARENTHESIS_KEY,
    "_": UNDERSCORE_KEY,
    "+": PLUS_KEY,
    "a": A_LOWER_KEY,
    "b": B_LOWER_KEY,
    "c": C_LOWER_KEY,
    "d": D_LOWER_KEY,
    "e": E_LOWER_KEY,
    "f": F_LOWER_KEY,
    "g": G_LOWER_KEY,
    "h": H_LOWER_KEY,
    "i": I_LOWER_KEY,
    "j": J_LOWER_KEY,
    "k": K_LOWER_KEY,
    "l": L_LOWER_KEY,
    "m": M_LOWER_KEY,
    "n": N_LOWER_KEY,
    "o": O_LOWER_KEY,
    "p": P_LOWER_KEY,
    "q": Q_LOWER_KEY,
    "r": R_LOWER_KEY,
    "s": S_LOWER_KEY,
    "t": T_LOWER_KEY,
    "u": U_LOWER_KEY,
    "v": V_LOWER_KEY,
    "w": W_LOWER_KEY,
    "x": X_LOWER_KEY,
    "y": Y_LOWER_KEY,
    "z": Z_LOWER_KEY,
    "A": A_UPPER_KEY,
    "B": B_UPPER_KEY,
    "C": C_UPPER_KEY,
    "D": D_UPPER_KEY,
    "E": E_UPPER_KEY,
    "F": F_UPPER_KEY,
    "G": G_UPPER_KEY,
    "H": H_UPPER_KEY,
    "I": I_UPPER_KEY,
    "J": J_UPPER_KEY,
    "K": K_UPPER_KEY,
    "L": L_UPPER_KEY,
    "M": M_UPPER_KEY,
    "N": N_UPPER_KEY,
    "O": O_UPPER_KEY,
    "P": P_UPPER_KEY,
    "Q": Q_UPPER_KEY,
    "R": R_UPPER_KEY,
    "S": S_UPPER_KEY,
    "T": T_UPPER_KEY,
    "U": U_UPPER_KEY,
    "V": V_UPPER_KEY,
    "W": W_UPPER_KEY,
    "X": X_UPPER_KEY,
    "Y": Y_UPPER_KEY,
    "Z": Z_UPPER_KEY,
    " ": SPACE_KEY,
    "[": LEFT_BRACKET_KEY,
    "]": RIGHT_BRACKET_KEY,
    "\\": BACKSLASH_KEY,
    "{": LEFT_CURLY_BRACE_KEY,
    "}": RIGHT_CURLY_BRACE_KEY,
    "|": PIPE_KEY,
    ";": SEMICOLON_KEY,
    "'": QUOTE_KEY,
    ",": COMMA_KEY,
    ".": PERIOD_KEY,
    "/": SLASH_KEY,
    ":": COLON_KEY,
    '"': DOUBLE_QUOTE_KEY,
    "<": LESS_THAN_KEY,
    ">": GREATER_THAN_KEY,
    "?": QUESTION_MARK_KEY,
}
