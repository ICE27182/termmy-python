

from .color import Color

from random import random
from random import seed as seed_
from typing import final

@final
class Colors:
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
    def random_color(
        seed: int | float | str | bytes | bytearray | None = None
    ) -> Color:
        seed_(seed)
        return Color(random(), random(), random())

    @staticmethod
    def ice() -> Color:
        return Color.from_ints(156, 220, 255)
