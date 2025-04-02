



from collections.abc import Sequence
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .type_aliases import Pixel, Pixel24, Pixel32

def is_pixel(value: Any) -> bool:
    """Check if `value` is of type `Pixel`"""
    from .type_aliases import Pixel24, Pixel32
    if isinstance(value, (Pixel24, Pixel32)):
        return True
    if isinstance(value, Sequence):
        pass

def is_pos(value: Any, 
           strict_tuple:bool = True, 
           strict_int:bool = True, 
           check_non_negative:bool = False) -> bool:
    return (
            (
                strict_tuple and isinstance(value, tuple) or
                isinstance(value, Sequence)
            )
            and len(value) == 2
            and all(
                        (
                            isinstance(value[i], int)
                            or not strict_int and 
                                isinstance(value[i], float) and 
                                value[i].is_integer()
                        )
                        for i in range(2)
                )
            and (not check_non_negative or all(value[i] for i in range(2)))
    )
            
