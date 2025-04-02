

from typing import Any
def validate_height(height:Any) -> None:
    if not isinstance(height, int) or height <= 0:
        raise ValueError(f"height must be a integer larger than 0. Got {height}")

def validate_width(width:Any) -> None:
    if not isinstance(width, int) or width <= 0:
            raise ValueError(f"width must be a integer larger than 0. Got {width}")
    
