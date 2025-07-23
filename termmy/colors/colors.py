

from .color import Color

from random import random
from random import seed as seed_
from typing import final

@final
class Colors:
    @staticmethod
    def ice() -> Color:
        return Color.from_ints(156, 220, 255)
    
    @staticmethod
    def black() -> Color:
        return Color(0.0, 0.0, 0.0)
    @staticmethod
    def white() -> Color:
        return Color(1.0, 1.0, 1.0)
    @staticmethod
    def gray() -> Color:
        return Color(0.5, 0.5, 0.5)

    @staticmethod
    def red() -> Color:
        return Color(1.0, 0.0, 0.0)
    @staticmethod
    def green() -> Color:
        return Color(0.0, 1.0, 0.0)
    @staticmethod
    def blue() -> Color:
        return Color(0.0, 0.0, 1.0)

    @staticmethod
    def yellow() -> Color:
        return Color(0.707, 0.707, 0.0)
    @staticmethod
    def magenta() -> Color:
        return Color(0.707, 0.0, 0.707)
    @staticmethod
    def cyan() -> Color:
        return Color(0.0, 0.707, 0.707)
    
    @staticmethod
    def orange() -> Color:
        return Color(1.0, 0.667, 0.0)
    @staticmethod
    def lemon() -> Color:
        return Color(1.0, 1.0, 0.0)
    @staticmethod
    def lime() -> Color:
        return Color.from_ints(137, 243, 54)

    @staticmethod
    def pink() -> Color:
        return Color(1.0, 0.5, 0.5)
    @staticmethod
    def salmon() -> Color:
        return Color(1.0, 0.5, 0.4)
    @staticmethod
    def purple() -> Color:
        return Color(0.5, 0.0, 0.5)
    @staticmethod
    def violet() -> Color:
        return Color(0.5, 0.0, 1.0)
    
    @staticmethod
    def indigo() -> Color:
        return Color(0.0, 0.0, 0.5)
    @staticmethod
    def navy() -> Color:
        return Color(0.0, 0.0, 0.25)
    @staticmethod
    def lapis_lazuli() -> Color:
        return Color.from_ints(38, 97, 156)
    @staticmethod
    def sky_blue() -> Color:
        return Color.from_ints(135, 206, 235)

    @staticmethod
    def random_color(
        seed: int | float | str | bytes | bytearray | None = None
    ) -> Color:
        seed_(seed)
        return Color(random(), random(), random())

