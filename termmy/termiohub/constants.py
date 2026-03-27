from enum import Enum

from .input_event import KeyboardInput
from .input_parser import State

_T = KeyboardInput.ModifierState.YES
_F = KeyboardInput.ModifierState.NO
_U = KeyboardInput.ModifierState.UNKNOWN

class PredefinedKeys(Enum):
    """Collection of predefined keyboard inputs."""
    
    # Blow I used a few `if True:` in order to fold them as groups in vscode
    
    ################################################################
    # Directions
    ################################################################
    if True:
        UP = KeyboardInput("up", b"\x1b[A", shift=_F, ctrl=_F, alt=_F)
        DOWN = KeyboardInput("down", b"\x1b[B", shift=_F, ctrl=_F, alt=_F)
        RIGHT = KeyboardInput("right", b"\x1b[C", shift=_F, ctrl=_F, alt=_F)
        LEFT = KeyboardInput("left", b"\x1b[D", shift=_F, ctrl=_F, alt=_F)

        UP_SHIFT = KeyboardInput("up", b"\x1b[1;2A", shift=_T, ctrl=_F, alt=_F)
        DOWN_SHIFT = KeyboardInput("down", b"\x1b[1;2B", shift=_T, ctrl=_F, alt=_F)
        RIGHT_SHIFT = KeyboardInput("right", b"\x1b[1;2C", shift=_T, ctrl=_F, alt=_F)
        LEFT_SHIFT = KeyboardInput("left", b"\x1b[1;2D", shift=_T, ctrl=_F, alt=_F)

        UP_ALT = KeyboardInput("up", b"\x1b[1;3A", shift=_F, ctrl=_F, alt=_T)
        DOWN_ALT = KeyboardInput("down", b"\x1b[1;3B", shift=_F, ctrl=_F, alt=_T)
        RIGHT_ALT = KeyboardInput("right", b"\x1b[1;3C", shift=_F, ctrl=_F, alt=_T)
        LEFT_ALT = KeyboardInput("left", b"\x1b[1;3D", shift=_F, ctrl=_F, alt=_T)

        UP_ALT_SHIFT = KeyboardInput("up", b"\x1b[1;4A", shift=_T, ctrl=_F, alt=_T)
        DOWN_ALT_SHIFT = KeyboardInput("down", b"\x1b[1;4B", shift=_T, ctrl=_F, alt=_T)
        RIGHT_ALT_SHIFT = KeyboardInput("right", b"\x1b[1;4C", shift=_T, ctrl=_F, alt=_T)
        LEFT_ALT_SHIFT = KeyboardInput("left", b"\x1b[1;4D", shift=_T, ctrl=_F, alt=_T)

        UP_CTRL = KeyboardInput("up", b"\x1b[1;5A", shift=_F, ctrl=_T, alt=_F)
        DOWN_CTRL = KeyboardInput("down", b"\x1b[1;5B", shift=_F, ctrl=_T, alt=_F)
        RIGHT_CTRL = KeyboardInput("right", b"\x1b[1;5C", shift=_F, ctrl=_T, alt=_F)
        LEFT_CTRL = KeyboardInput("left", b"\x1b[1;5D", shift=_F, ctrl=_T, alt=_F)

        UP_CTRL_SHIFT = KeyboardInput("up", b"\x1b[1;6A", shift=_T, ctrl=_T, alt=_F)
        DOWN_CTRL_SHIFT = KeyboardInput("down", b"\x1b[1;6B", shift=_T, ctrl=_T, alt=_F)
        RIGHT_CTRL_SHIFT = KeyboardInput("right", b"\x1b[1;6C", shift=_T, ctrl=_T, alt=_F)
        LEFT_CTRL_SHIFT = KeyboardInput("left", b"\x1b[1;6D", shift=_T, ctrl=_T, alt=_F)

        UP_ALT_CTRL = KeyboardInput("up", b"\x1b[1;7A", shift=_F, ctrl=_T, alt=_T)
        DOWN_ALT_CTRL = KeyboardInput("down", b"\x1b[1;7B", shift=_F, ctrl=_T, alt=_T)
        RIGHT_ALT_CTRL = KeyboardInput("right", b"\x1b[1;7C", shift=_F, ctrl=_T, alt=_T)
        LEFT_ALT_CTRL = KeyboardInput("left", b"\x1b[1;7D", shift=_F, ctrl=_T, alt=_T)

        UP_ALT_CTRL_SHIFT = KeyboardInput("up", b"\x1b[1;8A", shift=_T, ctrl=_T, alt=_T)
        DOWN_ALT_CTRL_SHIFT = KeyboardInput("down", b"\x1b[1;8B", shift=_T, ctrl=_T, alt=_T)
        RIGHT_ALT_CTRL_SHIFT = KeyboardInput("right", b"\x1b[1;8C", shift=_T, ctrl=_T, alt=_T)
        LEFT_ALT_CTRL_SHIFT = KeyboardInput("left", b"\x1b[1;8D", shift=_T, ctrl=_T, alt=_T)

    ################################################################
    # Tab / Backspace / Enter / Delete / ESCAPE
    ################################################################
    if True:
        # control + i will also be \t and there is no way to tell
        TAB = KeyboardInput("tab", b"\t", shift=_F, ctrl=_U, alt=_U)
        TAB_SHIFT = KeyboardInput("tab", b"\x1b[Z", shift=_T, ctrl=_U, alt=_U)

        # TODO option + shift also gives \x07f
        # BACKSPACE = KeyboardInput("backspace", b"\x7f", shift=_U, ctrl=_F, alt=_F)
        # TODO control + option + shift also gives \x08
        # BACKSPACE_CTRL = KeyboardInput("backspace", b"\x08", shift=_U, ctrl=_T, alt=_F)
        BACKSPACE_ALT = KeyboardInput("backspace", b"\x1b\x7f", shift=_U, ctrl=_F, alt=_T)

        DELETE = KeyboardInput("delete", b"\x1b[3~", alt=_F, shift=_F, ctrl=_F)
        DELETE_SHIFT = KeyboardInput("delete", b"\x1b[3;2~", alt=_F, ctrl=_F, shift=_T)
        DELETE_ALT = KeyboardInput("delete", b"\x1b[3;3~", alt=_T, ctrl=_F, shift=_F)
        DELETE_ALT_SHIFT = KeyboardInput("delete", b"\x1b[3;4~", alt=_T, ctrl=_F, shift=_T)
        DELETE_CONTROL = KeyboardInput("delete", b"\x1b[3;5~", alt=_F, ctrl=_T, shift=_F)
        DELETE_CTRL_SHIFT = KeyboardInput("delete", b"\x1b[3;6~", alt=_F, ctrl=_T, shift=_T)
        DELETE_ALT_CTRL = KeyboardInput("delete", b"\x1b[3;7~", alt=_T, ctrl=_T, shift=_F)
        DELETE_ALT_CTRL_SHIFT = KeyboardInput("delete", b"\x1b[3;8~", alt=_T, ctrl=_T, shift=_T)

        # control + j will also be \n and there is no way to tell
        ENTER = KeyboardInput("enter", b"\r", shift=_U, ctrl=_U, alt=_U)

        ESCAPE = KeyboardInput("escape", b"\x1b", shift=_U, ctrl=_U, alt=_U)

    ################################################################
    # Fn keys
    ################################################################
    if True:
        F1 = KeyboardInput("f1", b"\x1bOP", shift=_F, ctrl=_F, alt=_F)
        F2 = KeyboardInput("f2", b"\x1bOQ", shift=_F, ctrl=_F, alt=_F)
        F3 = KeyboardInput("f3", b"\x1bOR", shift=_F, ctrl=_F, alt=_F)
        F4 = KeyboardInput("f4", b"\x1bOS", shift=_F, ctrl=_F, alt=_F)
        F5 = KeyboardInput("f5", b"\x1b[15~", shift=_F, ctrl=_F, alt=_F)
        F6 = KeyboardInput("f6", b"\x1b[17~", shift=_F, ctrl=_F, alt=_F)
        F7 = KeyboardInput("f7", b"\x1b[18~", shift=_F, ctrl=_F, alt=_F)
        F8 = KeyboardInput("f8", b"\x1b[19~", shift=_F, ctrl=_F, alt=_F)
        F9 = KeyboardInput("f9", b"\x1b[20~", shift=_F, ctrl=_F, alt=_F)
        F10 = KeyboardInput("f10", b"\x1b[21~", shift=_F, ctrl=_F, alt=_F)
        F11 = KeyboardInput("f11", b"\x1b[23~", shift=_F, ctrl=_F, alt=_F)
        F12 = KeyboardInput("f12", b"\x1b[24~", shift=_F, ctrl=_F, alt=_F)

        F1_SHIFT = KeyboardInput("f1", b"\x1b[1;2P", shift=_T, ctrl=_F, alt=_F)
        F2_SHIFT = KeyboardInput("f2", b"\x1b[1;2Q", shift=_T, ctrl=_F, alt=_F)
        F3_SHIFT = KeyboardInput("f3", b"\x1b[1;2R", shift=_T, ctrl=_F, alt=_F)
        F4_SHIFT = KeyboardInput("f4", b"\x1b[1;2S", shift=_T, ctrl=_F, alt=_F)
        F5_SHIFT = KeyboardInput("f5", b"\x1b[15;2~", shift=_T, ctrl=_F, alt=_F)
        F6_SHIFT = KeyboardInput("f6", b"\x1b[17;2~", shift=_T, ctrl=_F, alt=_F)
        F7_SHIFT = KeyboardInput("f7", b"\x1b[18;2~", shift=_T, ctrl=_F, alt=_F)
        F8_SHIFT = KeyboardInput("f8", b"\x1b[19;2~", shift=_T, ctrl=_F, alt=_F)
        F9_SHIFT = KeyboardInput("f9", b"\x1b[20;2~", shift=_T, ctrl=_F, alt=_F)
        F10_SHIFT = KeyboardInput("f10", b"\x1b[21;2~", shift=_T, ctrl=_F, alt=_F)
        F11_SHIFT = KeyboardInput("f11", b"\x1b[23;2~", shift=_T, ctrl=_F, alt=_F)
        F12_SHIFT = KeyboardInput("f12", b"\x1b[24;2~", shift=_T, ctrl=_F, alt=_F)

        F1_ALT = KeyboardInput("f1", b"\x1b[1;3P", shift=_F, ctrl=_F, alt=_T)
        F2_ALT = KeyboardInput("f2", b"\x1b[1;3Q", shift=_F, ctrl=_F, alt=_T)
        F3_ALT = KeyboardInput("f3", b"\x1b[1;3R", shift=_F, ctrl=_F, alt=_T)
        F4_ALT = KeyboardInput("f4", b"\x1b[1;3S", shift=_F, ctrl=_F, alt=_T)
        F5_ALT = KeyboardInput("f5", b"\x1b[15;3~", shift=_F, ctrl=_F, alt=_T)
        F6_ALT = KeyboardInput("f6", b"\x1b[17;3~", shift=_F, ctrl=_F, alt=_T)
        F7_ALT = KeyboardInput("f7", b"\x1b[18;3~", shift=_F, ctrl=_F, alt=_T)
        F8_ALT = KeyboardInput("f8", b"\x1b[19;3~", shift=_F, ctrl=_F, alt=_T)
        F9_ALT = KeyboardInput("f9", b"\x1b[20;3~", shift=_F, ctrl=_F, alt=_T)
        F10_ALT = KeyboardInput("f10", b"\x1b[21;3~", shift=_F, ctrl=_F, alt=_T)
        F11_ALT = KeyboardInput("f11", b"\x1b[23;3~", shift=_F, ctrl=_F, alt=_T)
        F12_ALT = KeyboardInput("f12", b"\x1b[24;3~", shift=_F, ctrl=_F, alt=_T)

        F1_ALT_SHIFT = KeyboardInput("f1", b"\x1b[1;4P", shift=_T, ctrl=_F, alt=_T)
        F2_ALT_SHIFT = KeyboardInput("f2", b"\x1b[1;4Q", shift=_T, ctrl=_F, alt=_T)
        F3_ALT_SHIFT = KeyboardInput("f3", b"\x1b[1;4R", shift=_T, ctrl=_F, alt=_T)
        F4_ALT_SHIFT = KeyboardInput("f4", b"\x1b[1;4S", shift=_T, ctrl=_F, alt=_T)
        F5_ALT_SHIFT = KeyboardInput("f5", b"\x1b[15;4~", shift=_T, ctrl=_F, alt=_T)
        F6_ALT_SHIFT = KeyboardInput("f6", b"\x1b[17;4~", shift=_T, ctrl=_F, alt=_T)
        F7_ALT_SHIFT = KeyboardInput("f7", b"\x1b[18;4~", shift=_T, ctrl=_F, alt=_T)
        F8_ALT_SHIFT = KeyboardInput("f8", b"\x1b[19;4~", shift=_T, ctrl=_F, alt=_T)
        F9_ALT_SHIFT = KeyboardInput("f9", b"\x1b[20;4~", shift=_T, ctrl=_F, alt=_T)
        F10_ALT_SHIFT = KeyboardInput("f10", b"\x1b[21;4~", shift=_T, ctrl=_F, alt=_T)
        F11_ALT_SHIFT = KeyboardInput("f11", b"\x1b[23;4~", shift=_T, ctrl=_F, alt=_T)
        F12_ALT_SHIFT = KeyboardInput("f12", b"\x1b[24;4~", shift=_T, ctrl=_F, alt=_T)

        F1_CTRL = KeyboardInput("f1", b"\x1b[1;5P", shift=_F, ctrl=_T, alt=_F)
        F2_CTRL = KeyboardInput("f2", b"\x1b[1;5Q", shift=_F, ctrl=_T, alt=_F)
        F3_CTRL = KeyboardInput("f3", b"\x1b[1;5R", shift=_F, ctrl=_T, alt=_F)
        F4_CTRL = KeyboardInput("f4", b"\x1b[1;5S", shift=_F, ctrl=_T, alt=_F)
        F5_CTRL = KeyboardInput("f5", b"\x1b[15;5~", shift=_F, ctrl=_T, alt=_F)
        F6_CTRL = KeyboardInput("f6", b"\x1b[17;5~", shift=_F, ctrl=_T, alt=_F)
        F7_CTRL = KeyboardInput("f7", b"\x1b[18;5~", shift=_F, ctrl=_T, alt=_F)
        F8_CTRL = KeyboardInput("f8", b"\x1b[19;5~", shift=_F, ctrl=_T, alt=_F)
        F9_CTRL = KeyboardInput("f9", b"\x1b[20;5~", shift=_F, ctrl=_T, alt=_F)
        F10_CTRL = KeyboardInput("f10", b"\x1b[21;5~", shift=_F, ctrl=_T, alt=_F)
        F11_CTRL = KeyboardInput("f11", b"\x1b[23;5~", shift=_F, ctrl=_T, alt=_F)
        F12_CTRL = KeyboardInput("f12", b"\x1b[24;5~", shift=_F, ctrl=_T, alt=_F)

        F1_CTRL_SHIFT = KeyboardInput("f1", b"\x1b[1;6P", shift=_T, ctrl=_T, alt=_F)
        F2_CTRL_SHIFT = KeyboardInput("f2", b"\x1b[1;6Q", shift=_T, ctrl=_T, alt=_F)
        F3_CTRL_SHIFT = KeyboardInput("f3", b"\x1b[1;6R", shift=_T, ctrl=_T, alt=_F)
        F4_CTRL_SHIFT = KeyboardInput("f4", b"\x1b[1;6S", shift=_T, ctrl=_T, alt=_F)
        F5_CTRL_SHIFT = KeyboardInput("f5", b"\x1b[15;6~", shift=_T, ctrl=_T, alt=_F)
        F6_CTRL_SHIFT = KeyboardInput("f6", b"\x1b[17;6~", shift=_T, ctrl=_T, alt=_F)
        F7_CTRL_SHIFT = KeyboardInput("f7", b"\x1b[18;6~", shift=_T, ctrl=_T, alt=_F)
        F8_CTRL_SHIFT = KeyboardInput("f8", b"\x1b[19;6~", shift=_T, ctrl=_T, alt=_F)
        F9_CTRL_SHIFT = KeyboardInput("f9", b"\x1b[20;6~", shift=_T, ctrl=_T, alt=_F)
        F10_CTRL_SHIFT = KeyboardInput("f10", b"\x1b[21;6~", shift=_T, ctrl=_T, alt=_F)
        F11_CTRL_SHIFT = KeyboardInput("f11", b"\x1b[23;6~", shift=_T, ctrl=_T, alt=_F)
        F12_CTRL_SHIFT = KeyboardInput("f12", b"\x1b[24;6~", shift=_T, ctrl=_T, alt=_F)

        F1_ALT_CTRL = KeyboardInput("f1", b"\x1b[1;7P", shift=_F, ctrl=_T, alt=_T)
        F2_ALT_CTRL = KeyboardInput("f2", b"\x1b[1;7Q", shift=_F, ctrl=_T, alt=_T)
        F3_ALT_CTRL = KeyboardInput("f3", b"\x1b[1;7R", shift=_F, ctrl=_T, alt=_T)
        F4_ALT_CTRL = KeyboardInput("f4", b"\x1b[1;7S", shift=_F, ctrl=_T, alt=_T)
        F5_ALT_CTRL = KeyboardInput("f5", b"\x1b[15;7~", shift=_F, ctrl=_T, alt=_T)
        F6_ALT_CTRL = KeyboardInput("f6", b"\x1b[17;7~", shift=_F, ctrl=_T, alt=_T)
        F7_ALT_CTRL = KeyboardInput("f7", b"\x1b[18;7~", shift=_F, ctrl=_T, alt=_T)
        F8_ALT_CTRL = KeyboardInput("f8", b"\x1b[19;7~", shift=_F, ctrl=_T, alt=_T)
        F9_ALT_CTRL = KeyboardInput("f9", b"\x1b[20;7~", shift=_F, ctrl=_T, alt=_T)
        F10_ALT_CTRL = KeyboardInput("f10", b"\x1b[21;7~", shift=_F, ctrl=_T, alt=_T)
        F11_ALT_CTRL = KeyboardInput("f11", b"\x1b[23;7~", shift=_F, ctrl=_T, alt=_T)
        F12_ALT_CTRL = KeyboardInput("f12", b"\x1b[24;7~", shift=_F, ctrl=_T, alt=_T)

        F1_ALT_CTRL_SHIFT = KeyboardInput("f1", b"\x1b[1;8P", shift=_T, ctrl=_T, alt=_T)
        F2_ALT_CTRL_SHIFT = KeyboardInput("f2", b"\x1b[1;8Q", shift=_T, ctrl=_T, alt=_T)
        F3_ALT_CTRL_SHIFT = KeyboardInput("f3", b"\x1b[1;8R", shift=_T, ctrl=_T, alt=_T)
        F4_ALT_CTRL_SHIFT = KeyboardInput("f4", b"\x1b[1;8S", shift=_T, ctrl=_T, alt=_T)
        F5_ALT_CTRL_SHIFT = KeyboardInput("f5", b"\x1b[15;8~", shift=_T, ctrl=_T, alt=_T)
        F6_ALT_CTRL_SHIFT = KeyboardInput("f6", b"\x1b[17;8~", shift=_T, ctrl=_T, alt=_T)
        F7_ALT_CTRL_SHIFT = KeyboardInput("f7", b"\x1b[18;8~", shift=_T, ctrl=_T, alt=_T)
        F8_ALT_CTRL_SHIFT = KeyboardInput("f8", b"\x1b[19;8~", shift=_T, ctrl=_T, alt=_T)
        F9_ALT_CTRL_SHIFT = KeyboardInput("f9", b"\x1b[20;8~", shift=_T, ctrl=_T, alt=_T)
        F10_ALT_CTRL_SHIFT = KeyboardInput("f10", b"\x1b[21;8~", shift=_T, ctrl=_T, alt=_T)
        F11_ALT_CTRL_SHIFT = KeyboardInput("f11", b"\x1b[23;8~", shift=_T, ctrl=_T, alt=_T)
        F12_ALT_CTRL_SHIFT = KeyboardInput("f12", b"\x1b[24;8~", shift=_T, ctrl=_T, alt=_T)

    ################################################################
    # Non-alpha Ascii
    ################################################################
    if True:
        # Second Row on the keyboard
        BACKTICK_KEY = KeyboardInput("`", b"`", shift=_F)
        ONE_KEY = KeyboardInput("1", b"1", shift=_F)
        TWO_KEY = KeyboardInput("2", b"2", shift=_F)
        THREE_KEY = KeyboardInput("3", b"3", shift=_F)
        FOUR_KEY = KeyboardInput("4", b"4", shift=_F)
        FIVE_KEY = KeyboardInput("5", b"5", shift=_F)
        SIX_KEY = KeyboardInput("6", b"6", shift=_F)
        SEVEN_KEY = KeyboardInput("7", b"7", shift=_F)
        EIGHT_KEY = KeyboardInput("8", b"8", shift=_F)
        NINE_KEY = KeyboardInput("9", b"9", shift=_F)
        ZERO_KEY = KeyboardInput("0", b"0", shift=_F)
        MINUS_KEY = KeyboardInput("-", b"-", shift=_F)
        EQUAL_KEY = KeyboardInput("=", b"=", shift=_F)

        # Second Row on the keyboard with shift
        TILDE_KEY = KeyboardInput("~", b"~", shift=_T)
        EXCLAMATION_KEY = KeyboardInput("!", b"!", shift=_T)
        AT_KEY = KeyboardInput("@", b"@", shift=_T)
        HASH_KEY = KeyboardInput("#", b"#", shift=_T)
        DOLLAR_KEY = KeyboardInput("$", b"$", shift=_T)
        PERCENT_KEY = KeyboardInput("%", b"%", shift=_T)
        CARET_KEY = KeyboardInput("^", b"^", shift=_T)
        AMPERSAND_KEY = KeyboardInput("&", b"&", shift=_T)
        ASTERISK_KEY = KeyboardInput("*", b"*", shift=_T)
        LEFT_PARENTHESIS_KEY = KeyboardInput("(", b"(", shift=_T)
        RIGHT_PARENTHESIS_KEY = KeyboardInput(")", b")", shift=_T)
        UNDERSCORE_KEY = KeyboardInput("_", b"_", shift=_T)
        PLUS_KEY = KeyboardInput("+", b"+", shift=_T)

        # The rest symbols
        SPACE_KEY = KeyboardInput(" ", b" ", shift=_F)
        LEFT_BRACKET_KEY = KeyboardInput("[", b"[", shift=_F)
        RIGHT_BRACKET_KEY = KeyboardInput("]", b"]", shift=_F)
        BACKSLASH_KEY = KeyboardInput("\\", b"\\", shift=_F)
        LEFT_CURLY_BRACE_KEY = KeyboardInput("{", b"{", shift=_T)
        RIGHT_CURLY_BRACE_KEY = KeyboardInput("}", b"}", shift=_T)
        PIPE_KEY = KeyboardInput("|", b"|", shift=_T)
        SEMICOLON_KEY = KeyboardInput(";", b";", shift=_F)
        QUOTE_KEY = KeyboardInput("'", b"'", shift=_F)
        COMMA_KEY = KeyboardInput(",", b",", shift=_F)
        PERIOD_KEY = KeyboardInput(".", b".", shift=_F)
        SLASH_KEY = KeyboardInput("/", b"/", shift=_F)
        COLON_KEY = KeyboardInput(":", b":", shift=_T)
        DOUBLE_QUOTE_KEY = KeyboardInput('"', b'"', shift=_T)
        LESS_THAN_KEY = KeyboardInput("<", b"<", shift=_T)
        GREATER_THAN_KEY = KeyboardInput(">", b">", shift=_T)
        QUESTION_MARK_KEY = KeyboardInput("?", b"?", shift=_T)
    
    ################################################################
    # Alpha Ascii
    ################################################################
    if True:
        # Alphabet lowercase
        A_LOWER_KEY = KeyboardInput("a", b"a", shift=_F)
        B_LOWER_KEY = KeyboardInput("b", b"b", shift=_F)
        C_LOWER_KEY = KeyboardInput("c", b"c", shift=_F)
        D_LOWER_KEY = KeyboardInput("d", b"d", shift=_F)
        E_LOWER_KEY = KeyboardInput("e", b"e", shift=_F)
        F_LOWER_KEY = KeyboardInput("f", b"f", shift=_F)
        G_LOWER_KEY = KeyboardInput("g", b"g", shift=_F)
        H_LOWER_KEY = KeyboardInput("h", b"h", shift=_F)
        I_LOWER_KEY = KeyboardInput("i", b"i", shift=_F)
        J_LOWER_KEY = KeyboardInput("j", b"j", shift=_F)
        K_LOWER_KEY = KeyboardInput("k", b"k", shift=_F)
        L_LOWER_KEY = KeyboardInput("l", b"l", shift=_F)
        M_LOWER_KEY = KeyboardInput("m", b"m", shift=_F)
        N_LOWER_KEY = KeyboardInput("n", b"n", shift=_F)
        O_LOWER_KEY = KeyboardInput("o", b"o", shift=_F)
        P_LOWER_KEY = KeyboardInput("p", b"p", shift=_F)
        Q_LOWER_KEY = KeyboardInput("q", b"q", shift=_F)
        R_LOWER_KEY = KeyboardInput("r", b"r", shift=_F)
        S_LOWER_KEY = KeyboardInput("s", b"s", shift=_F)
        T_LOWER_KEY = KeyboardInput("t", b"t", shift=_F)
        U_LOWER_KEY = KeyboardInput("u", b"u", shift=_F)
        V_LOWER_KEY = KeyboardInput("v", b"v", shift=_F)
        W_LOWER_KEY = KeyboardInput("w", b"w", shift=_F)
        X_LOWER_KEY = KeyboardInput("x", b"x", shift=_F)
        Y_LOWER_KEY = KeyboardInput("y", b"y", shift=_F)
        Z_LOWER_KEY = KeyboardInput("z", b"z", shift=_F)

        # Alphabet uppercase
        A_UPPER_KEY = KeyboardInput("A", b"A", shift=_T)
        B_UPPER_KEY = KeyboardInput("B", b"B", shift=_T)
        C_UPPER_KEY = KeyboardInput("C", b"C", shift=_T)
        D_UPPER_KEY = KeyboardInput("D", b"D", shift=_T)
        E_UPPER_KEY = KeyboardInput("E", b"E", shift=_T)
        F_UPPER_KEY = KeyboardInput("F", b"F", shift=_T)
        G_UPPER_KEY = KeyboardInput("G", b"G", shift=_T)
        H_UPPER_KEY = KeyboardInput("H", b"H", shift=_T)
        I_UPPER_KEY = KeyboardInput("I", b"I", shift=_T)
        J_UPPER_KEY = KeyboardInput("J", b"J", shift=_T)
        K_UPPER_KEY = KeyboardInput("K", b"K", shift=_T)
        L_UPPER_KEY = KeyboardInput("L", b"L", shift=_T)
        M_UPPER_KEY = KeyboardInput("M", b"M", shift=_T)
        N_UPPER_KEY = KeyboardInput("N", b"N", shift=_T)
        O_UPPER_KEY = KeyboardInput("O", b"O", shift=_T)
        P_UPPER_KEY = KeyboardInput("P", b"P", shift=_T)
        Q_UPPER_KEY = KeyboardInput("Q", b"Q", shift=_T)
        R_UPPER_KEY = KeyboardInput("R", b"R", shift=_T)
        S_UPPER_KEY = KeyboardInput("S", b"S", shift=_T)
        T_UPPER_KEY = KeyboardInput("T", b"T", shift=_T)
        U_UPPER_KEY = KeyboardInput("U", b"U", shift=_T)
        V_UPPER_KEY = KeyboardInput("V", b"V", shift=_T)
        W_UPPER_KEY = KeyboardInput("W", b"W", shift=_T)
        X_UPPER_KEY = KeyboardInput("X", b"X", shift=_T)
        Y_UPPER_KEY = KeyboardInput("Y", b"Y", shift=_T)
        Z_UPPER_KEY = KeyboardInput("Z", b"Z", shift=_T)

        A_ALT = KeyboardInput("a", b"\x1ba", shift=_F, ctrl=_F, alt=_T)
        B_ALT = KeyboardInput("b", b"\x1bb", shift=_F, ctrl=_F, alt=_T)
        C_ALT = KeyboardInput("c", b"\x1bc", shift=_F, ctrl=_F, alt=_T)
        D_ALT = KeyboardInput("d", b"\x1bd", shift=_F, ctrl=_F, alt=_T)
        E_ALT = KeyboardInput("e", b"\x1be", shift=_F, ctrl=_F, alt=_T)
        F_ALT = KeyboardInput("f", b"\x1bf", shift=_F, ctrl=_F, alt=_T)
        G_ALT = KeyboardInput("g", b"\x1bg", shift=_F, ctrl=_F, alt=_T)
        H_ALT = KeyboardInput("h", b"\x1bh", shift=_F, ctrl=_F, alt=_T)
        I_ALT = KeyboardInput("i", b"\x1bi", shift=_F, ctrl=_F, alt=_T)
        J_ALT = KeyboardInput("j", b"\x1bj", shift=_F, ctrl=_F, alt=_T)
        K_ALT = KeyboardInput("k", b"\x1bk", shift=_F, ctrl=_F, alt=_T)
        L_ALT = KeyboardInput("l", b"\x1bl", shift=_F, ctrl=_F, alt=_T)
        M_ALT = KeyboardInput("m", b"\x1bm", shift=_F, ctrl=_F, alt=_T)
        N_ALT = KeyboardInput("n", b"\x1bn", shift=_F, ctrl=_F, alt=_T)
        O_ALT = KeyboardInput("o", b"\x1bo", shift=_F, ctrl=_F, alt=_T)
        P_ALT = KeyboardInput("p", b"\x1bp", shift=_F, ctrl=_F, alt=_T)
        Q_ALT = KeyboardInput("q", b"\x1bq", shift=_F, ctrl=_F, alt=_T)
        R_ALT = KeyboardInput("r", b"\x1br", shift=_F, ctrl=_F, alt=_T)
        S_ALT = KeyboardInput("s", b"\x1bs", shift=_F, ctrl=_F, alt=_T)
        T_ALT = KeyboardInput("t", b"\x1bt", shift=_F, ctrl=_F, alt=_T)
        U_ALT = KeyboardInput("u", b"\x1bu", shift=_F, ctrl=_F, alt=_T)
        V_ALT = KeyboardInput("v", b"\x1bv", shift=_F, ctrl=_F, alt=_T)
        W_ALT = KeyboardInput("w", b"\x1bw", shift=_F, ctrl=_F, alt=_T)
        X_ALT = KeyboardInput("x", b"\x1bx", shift=_F, ctrl=_F, alt=_T)
        Y_ALT = KeyboardInput("y", b"\x1by", shift=_F, ctrl=_F, alt=_T)
        Z_ALT = KeyboardInput("z", b"\x1bz", shift=_F, ctrl=_F, alt=_T)

        A_ALT_SHIFT = KeyboardInput("a", b"\x1bA", shift=_T, ctrl=_F, alt=_T)
        B_ALT_SHIFT = KeyboardInput("b", b"\x1bB", shift=_T, ctrl=_F, alt=_T)
        C_ALT_SHIFT = KeyboardInput("c", b"\x1bC", shift=_T, ctrl=_F, alt=_T)
        D_ALT_SHIFT = KeyboardInput("d", b"\x1bD", shift=_T, ctrl=_F, alt=_T)
        E_ALT_SHIFT = KeyboardInput("e", b"\x1bE", shift=_T, ctrl=_F, alt=_T)
        F_ALT_SHIFT = KeyboardInput("f", b"\x1bF", shift=_T, ctrl=_F, alt=_T)
        G_ALT_SHIFT = KeyboardInput("g", b"\x1bG", shift=_T, ctrl=_F, alt=_T)
        H_ALT_SHIFT = KeyboardInput("h", b"\x1bH", shift=_T, ctrl=_F, alt=_T)
        I_ALT_SHIFT = KeyboardInput("i", b"\x1bI", shift=_T, ctrl=_F, alt=_T)
        J_ALT_SHIFT = KeyboardInput("j", b"\x1bJ", shift=_T, ctrl=_F, alt=_T)
        K_ALT_SHIFT = KeyboardInput("k", b"\x1bK", shift=_T, ctrl=_F, alt=_T)
        L_ALT_SHIFT = KeyboardInput("l", b"\x1bL", shift=_T, ctrl=_F, alt=_T)
        M_ALT_SHIFT = KeyboardInput("m", b"\x1bM", shift=_T, ctrl=_F, alt=_T)
        N_ALT_SHIFT = KeyboardInput("n", b"\x1bN", shift=_T, ctrl=_F, alt=_T)
        O_ALT_SHIFT = KeyboardInput("o", b"\x1bO", shift=_T, ctrl=_F, alt=_T)
        P_ALT_SHIFT = KeyboardInput("p", b"\x1bP", shift=_T, ctrl=_F, alt=_T)
        Q_ALT_SHIFT = KeyboardInput("q", b"\x1bQ", shift=_T, ctrl=_F, alt=_T)
        R_ALT_SHIFT = KeyboardInput("r", b"\x1bR", shift=_T, ctrl=_F, alt=_T)
        S_ALT_SHIFT = KeyboardInput("s", b"\x1bS", shift=_T, ctrl=_F, alt=_T)
        T_ALT_SHIFT = KeyboardInput("t", b"\x1bT", shift=_T, ctrl=_F, alt=_T)
        U_ALT_SHIFT = KeyboardInput("u", b"\x1bU", shift=_T, ctrl=_F, alt=_T)
        V_ALT_SHIFT = KeyboardInput("v", b"\x1bV", shift=_T, ctrl=_F, alt=_T)
        W_ALT_SHIFT = KeyboardInput("w", b"\x1bW", shift=_T, ctrl=_F, alt=_T)
        X_ALT_SHIFT = KeyboardInput("x", b"\x1bX", shift=_T, ctrl=_F, alt=_T)
        Y_ALT_SHIFT = KeyboardInput("y", b"\x1bY", shift=_T, ctrl=_F, alt=_T)
        Z_ALT_SHIFT = KeyboardInput("z", b"\x1bZ", shift=_T, ctrl=_F, alt=_T)

        A_CTRL = KeyboardInput("a", b"\x01", shift=_U, ctrl=_T, alt=_F)
        B_CTRL = KeyboardInput("b", b"\x02", shift=_U, ctrl=_T, alt=_F)
        C_CTRL = KeyboardInput("c", b"\x03", shift=_U, ctrl=_T, alt=_F)
        D_CTRL = KeyboardInput("d", b"\x04", shift=_U, ctrl=_T, alt=_F)
        E_CTRL = KeyboardInput("e", b"\x05", shift=_U, ctrl=_T, alt=_F)
        F_CTRL = KeyboardInput("f", b"\x06", shift=_U, ctrl=_T, alt=_F)
        G_CTRL = KeyboardInput("g", b"\x07", shift=_U, ctrl=_T, alt=_F)
        H_CTRL = KeyboardInput("h", b"\x08", shift=_U, ctrl=_T, alt=_F)
        I_CTRL = KeyboardInput("i", b"\t", shift=_U, ctrl=_T, alt=_F)
        J_CTRL = KeyboardInput("j", b"\n", shift=_U, ctrl=_T, alt=_F)
        K_CTRL = KeyboardInput("k", b"\x0b", shift=_U, ctrl=_T, alt=_F)
        L_CTRL = KeyboardInput("l", b"\x0c", shift=_U, ctrl=_T, alt=_F)
        M_CTRL = KeyboardInput("m", b"\r", shift=_U, ctrl=_T, alt=_F)
        N_CTRL = KeyboardInput("n", b"\x0e", shift=_U, ctrl=_T, alt=_F)
        O_CTRL = KeyboardInput("o", b"\x0f", shift=_U, ctrl=_T, alt=_F)
        P_CTRL = KeyboardInput("p", b"\x10", shift=_U, ctrl=_T, alt=_F)
        Q_CTRL = KeyboardInput("q", b"\x11", shift=_U, ctrl=_T, alt=_F)
        R_CTRL = KeyboardInput("r", b"\x12", shift=_U, ctrl=_T, alt=_F)
        S_CTRL = KeyboardInput("s", b"\x13", shift=_U, ctrl=_T, alt=_F)
        T_CTRL = KeyboardInput("t", b"\x14", shift=_U, ctrl=_T, alt=_F)
        U_CTRL = KeyboardInput("u", b"\x15", shift=_U, ctrl=_T, alt=_F)
        V_CTRL = KeyboardInput("v", b"\x16", shift=_U, ctrl=_T, alt=_F)
        W_CTRL = KeyboardInput("w", b"\x17", shift=_U, ctrl=_T, alt=_F)
        X_CTRL = KeyboardInput("x", b"\x18", shift=_U, ctrl=_T, alt=_F)
        Y_CTRL = KeyboardInput("y", b"\x19", shift=_U, ctrl=_T, alt=_F)
        Z_CTRL = KeyboardInput("z", b"\x1a", shift=_U, ctrl=_T, alt=_F)

        A_ALT_CTRL = KeyboardInput("a", b"\x1b\x01", shift=_U, ctrl=_T, alt=_T)
        B_ALT_CTRL = KeyboardInput("b", b"\x1b\x02", shift=_U, ctrl=_T, alt=_T)
        C_ALT_CTRL = KeyboardInput("c", b"\x1b\x03", shift=_U, ctrl=_T, alt=_T)
        D_ALT_CTRL = KeyboardInput("d", b"\x1b\x04", shift=_U, ctrl=_T, alt=_T)
        E_ALT_CTRL = KeyboardInput("e", b"\x1b\x05", shift=_U, ctrl=_T, alt=_T)
        F_ALT_CTRL = KeyboardInput("f", b"\x1b\x06", shift=_U, ctrl=_T, alt=_T)
        G_ALT_CTRL = KeyboardInput("g", b"\x1b\x07", shift=_U, ctrl=_T, alt=_T)
        H_ALT_CTRL = KeyboardInput("h", b"\x1b\x08", shift=_U, ctrl=_T, alt=_T)
        I_ALT_CTRL = KeyboardInput("i", b"\x1b\t", shift=_U, ctrl=_T, alt=_T)
        J_ALT_CTRL = KeyboardInput("j", b"\x1b\n", shift=_U, ctrl=_T, alt=_T)
        K_ALT_CTRL = KeyboardInput("k", b"\x1b\x0b", shift=_U, ctrl=_T, alt=_T)
        L_ALT_CTRL = KeyboardInput("l", b"\x1b\x0c", shift=_U, ctrl=_T, alt=_T)
        M_ALT_CTRL = KeyboardInput("m", b"\x1b\r", shift=_U, ctrl=_T, alt=_T)
        N_ALT_CTRL = KeyboardInput("n", b"\x1b\x0e", shift=_U, ctrl=_T, alt=_T)
        O_ALT_CTRL = KeyboardInput("o", b"\x1b\x0f", shift=_U, ctrl=_T, alt=_T)
        P_ALT_CTRL = KeyboardInput("p", b"\x1b\x10", shift=_U, ctrl=_T, alt=_T)
        Q_ALT_CTRL = KeyboardInput("q", b"\x1b\x11", shift=_U, ctrl=_T, alt=_T)
        R_ALT_CTRL = KeyboardInput("r", b"\x1b\x12", shift=_U, ctrl=_T, alt=_T)
        S_ALT_CTRL = KeyboardInput("s", b"\x1b\x13", shift=_U, ctrl=_T, alt=_T)
        T_ALT_CTRL = KeyboardInput("t", b"\x1b\x14", shift=_U, ctrl=_T, alt=_T)
        U_ALT_CTRL = KeyboardInput("u", b"\x1b\x15", shift=_U, ctrl=_T, alt=_T)
        V_ALT_CTRL = KeyboardInput("v", b"\x1b\x16", shift=_U, ctrl=_T, alt=_T)
        W_ALT_CTRL = KeyboardInput("w", b"\x1b\x17", shift=_U, ctrl=_T, alt=_T)
        X_ALT_CTRL = KeyboardInput("x", b"\x1b\x18", shift=_U, ctrl=_T, alt=_T)
        Y_ALT_CTRL = KeyboardInput("y", b"\x1b\x19", shift=_U, ctrl=_T, alt=_T)
        Z_ALT_CTRL = KeyboardInput("z", b"\x1b\x1a", shift=_U, ctrl=_T, alt=_T)

################################################################
# Out
################################################################

KEY_MAPPING = {k.value.raw: k.value for k in PredefinedKeys}

_DFA_KEYBOARD = State.accepts(KEY_MAPPING.keys())

_DFA_MOUSE = State.from_constructor_list(
    [b"\x1b[<", State.numbers, b";", State.numbers, b";", State.numbers],
    is_final=False,
)
_DFA_MOUSE.multi_transit_(b"\x1b[<0;0;0").link(ord('m'), 
                                              State({}, is_final=True))
_DFA_MOUSE.multi_transit_(b"\x1b[<0;0;0").link(ord('M'), 
                                              State({}, is_final=True))

DFA = State.merge(_DFA_KEYBOARD, _DFA_MOUSE)
