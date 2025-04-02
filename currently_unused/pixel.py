

from .constants import DEFAULT_ALPHA
from .type_aliases import Pixel

from typing import Self, Iterable
from abc import ABC, abstractmethod
import operator

class PixelBaseClass(ABC):
    @abstractmethod
    def __len__(self) -> int:
        pass
    @abstractmethod
    def __iter__(self) -> Iterable:
        pass

    def r(self) -> int:
        return tuple(self)[0]

    def g(self) -> int:
        return tuple(self)[1]
    
    def b(self) -> int:
        return tuple(self)[2]

    def __str__(self) -> str:
        return f"\033[48;2;{self.r()};{self.g()};{self.b()}m  "
    
    def __getitem__(self, index) -> int:
        return tuple(self)[index]
    
    @abstractmethod
    def __setitem__(self, index:int, value) -> None:
        pass
    
    def gray_scale_value(self) -> int:
        return int(0.299 * self.r() + 0.587 * self.g() + 0.114 * self.b())
    
    def _operator_fallbacks(monomorphic_operator, fallback_operator):
        """
        Copied from fractions.py with a little modification
        """
        def forward(a, b):
            if isinstance(b, Pixel32):
                return monomorphic_operator(a, b)
            elif isinstance(b, int):
                return monomorphic_operator(a, Pixel32(b, b, b, a.a))
            elif isinstance(b, tuple):
                return NotImplemented
            else:
                return NotImplemented
        forward.__name__ = '__' + fallback_operator.__name__ + '__'
        forward.__doc__ = monomorphic_operator.__doc__

        def reverse(b, a):
            match a:
                case Pixel32():
                    return monomorphic_operator(a, b)
                case int():
                    return monomorphic_operator(a, Pixel32(b, b, b, a.a))
                case _:
                    return NotImplemented
        reverse.__name__ = '__r' + fallback_operator.__name__ + '__'
        reverse.__doc__ = monomorphic_operator.__doc__

        return forward, reverse

    def _add(a, b):
        return Pixel32(
            r if 0 <= (r := a.r + b.r) <= 255 else 255,
            g if 0 <= (g := a.g + b.g) <= 255 else 255,
            b if 0 <= (b := a.b + b.b) <= 255 else 255,
        )
    __add__, __radd__ = _operator_fallbacks(_add, operator.add)
    
    def _sub(a, b):
        return Pixel32(
            r if 0 <= (r := a.r - b.r) <= 255 else 0,
            g if 0 <= (g := a.g - b.g) <= 255 else 0,
            b if 0 <= (b := a.b - b.b) <= 255 else 0,
        )
    __sub__, __rsub__ = _operator_fallbacks(_sub, operator.sub)

    def _mul(a, b):
        return Pixel32(
            r if 0 <= (r := a.r * b.r) <= 255 else 255,
            g if 0 <= (g := a.g * b.g) <= 255 else 255,
            b if 0 <= (b := a.b * b.b) <= 255 else 255,
        )
    __mul__, __rmul__ = _operator_fallbacks(_mul, operator.mul)

    def _truediv(a, b):
        return Pixel32(
            255 * a.r // b.r,
            255 * a.g // b.g,
            255 * a.b // b.b,
        )
    __truediv__, __rtruediv__ = _operator_fallbacks(_truediv, operator.truediv)

    def _mod(a, b):
        return Pixel32(
            a.r % b.r,
            a.g % b.g,
            a.b % b.b,
        )
    __mod__, __rmod__ = _operator_fallbacks(_mod, operator.mod)

    def __eq__(self, other:Self) -> bool:
        match other:
            case Pixel32():
                return (
                    self.r == other.r and
                    self.g == other.g and
                    self.b == other.b and
                    self.a == other.a
                )
            case _:
                return NotImplemented 
    

class Pixel32(PixelBaseClass):
    __slots__ = ['r', 'g', 'b', 'a']
    def __init__(self, r=0, g=0, b=0, a=DEFAULT_ALPHA) -> None:
        self.r = r 
        self.g = g 
        self.b = b 
        self.a = a
    
    def __iter__(self) -> Iterable:
        return iter((self.r, self.g, self.b, self.a))

    def __len__(self):
        return 4
    
    def __setitem__(self, index, value):
        if isinstance(value, float):
            value = round(value * 255)
        elif isinstance(value, int):
            pass
        else:
            raise TypeError("Value can only be a float or an int")
        if value < 0 or value > 255:
            raise ValueError("Value must be a float in [0, 1] or an int in [0, 255]")
        elif not isinstance(index, int):
            raise TypeError(f"Index must be an integer, not {type(index)}")
        elif index < -4 or index > 3:
            raise IndexError("Index out of range")
        if index < 0:
            index += 4
        if index == 0: self.r = value
        elif index == 1: self.g = value
        elif index == 2: self.b = value
        elif index == 3: self.a = value
    
            
class Pixel24(PixelBaseClass):
    __slots__ = ['r', 'g', 'b']
    def __init__(self, r=0, g=0, b=0) -> None:
        self.r = r 
        self.g = g 
        self.b = b
    
    def __iter__(self) -> Iterable:
        return iter((self.r, self.g, self.b))

    def __len__(self):
        return 4
    
    def __setitem__(self, index, value):
        if isinstance(value, float):
            value = round(value * 255)
        elif isinstance(value, int):
            pass
        else:
            raise TypeError("Value can only be a float or an int")
        if value < 0 or value > 255:
            raise ValueError("Value must be a float in [0, 1] or an int in [0, 255]")
        elif not isinstance(index, int):
            raise TypeError(f"Index must be an integer, not {type(index)}")
        elif index < -4 or index > 3:
            raise IndexError("Index out of range")
        if index < 0:
            index += 4
        if index == 0: self.r = value
        elif index == 1: self.g = value
        elif index == 2: self.b = value
        elif index == 3: self.a = value
    
