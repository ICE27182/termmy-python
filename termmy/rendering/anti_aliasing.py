

from __future__ import annotations

from ..colors import Color
from ..buffers import ColorBuffer

from typing import overload
from dataclasses import dataclass
from abc import ABC
from math import log2


@dataclass(slots=True, frozen=True)
class AntiAliasing(ABC): pass

@dataclass(slots=True, frozen=True)
class SSAA(AntiAliasing):
    level: int
    def __bool__(self): return self.level > 1

@dataclass(slots=True, frozen=True)
class MSAA(AntiAliasing):
    pattern: tuple[tuple[float, float]]
    _level: int | None

    @classmethod
    def from_pattern(cls, pattern: tuple[tuple[float, float]]) -> MSAA:
        length = len(pattern)
        level = int(log2(length)) if length else None
        if 2 ** level != length:
            raise ValueError("The number of samples in the pattern "
                             "must be a power of two. "
                             f"Got {length} samples.")
        return cls(pattern, level)
        
    def __bool__(self): return not not self.pattern

@dataclass(slots=True, frozen=True)
class AAA(AntiAliasing):
    pattern: tuple[tuple[float, float]]
    _level: int | None

    @classmethod
    def from_pattern(cls, pattern: tuple[tuple[float, float]]) -> AAA:
        length = len(pattern)
        level = int(log2(length)) if length else None
        if 2 ** level != length:
            raise ValueError("The number of samples in the pattern "
                             "must be a power of two. "
                             f"Got {length} samples.")
        return cls(pattern, level)
    
    def __bool__(self): return not not self.pattern

@dataclass(slots=True, frozen=True)
class FXAA(AntiAliasing):
    threshold: float = 0.15
    @overload
    def apply_fxaa_to(self, buffer: ColorBuffer,
                      scratch_buffer: ColorBuffer 
                                      | None = None) -> ColorBuffer:
        """Apply FXAA to the provided color buffer. The alpha channel
        should be discarded after this function.

        It is more efficient to pass in a scratch buffer.
        
        Returns:
            ColorBuffer: The buffer itself with FXAA applied.
        
        Raises:
            ValueError: If `scratch_buffer` is provided but its demension does 
                not match the buffer's dimension.
        """
    @overload
    def apply_fxaa_to(self, buffer: ColorBuffer, 
                      scratch_buffer: ColorBuffer) -> ColorBuffer:
        """Apply FXAA to the provided color buffer. The alpha channel
        should be discarded after this function.
        
        Returns:
            ColorBuffer: The buffer itself with FXAA applied.

        Raises:
            ValueError: If `scratch_buffer` is provided but its demension does 
                not match the buffer's dimension.
        """
    def apply_fxaa_to(self, buffer: ColorBuffer, 
                      scratch_buffer: ColorBuffer 
                                      | None = None) -> ColorBuffer:
        return apply_fxaa_to(buffer, scratch_buffer, self.threshold)

@overload
def apply_fxaa_to(buffer: ColorBuffer,
                scratch_buffer: ColorBuffer | None = None,
                threshold: float = 0.15) -> ColorBuffer:
    """Apply FXAA to the provided color buffer. The alpha channel
    should be discarded after this function.

    It is more efficient to pass in a scratch buffer.
    
    Returns:
        ColorBuffer: The buffer itself with FXAA applied.
    
    Raises:
        ValueError: If `scratch_buffer` is provided but its demension does 
            not match the buffer's dimension.
    """

@overload
def apply_fxaa_to(buffer: ColorBuffer, scratch_buffer: ColorBuffer, 
                threshold: float = 0.15) -> ColorBuffer:
    """Apply FXAA to the provided color buffer. The alpha channel
    should be discarded after this function.
    
    Returns:
        ColorBuffer: The buffer itself with FXAA applied.

    Raises:
        ValueError: If `scratch_buffer` is provided but its demension does 
            not match the buffer's dimension.
    """

def apply_fxaa_to(buffer: ColorBuffer, 
                scratch_buffer: ColorBuffer | None = None,
                threshold: float = 0.15) -> ColorBuffer:
    width, height = buffer.width, buffer.height
    if scratch_buffer is None:
        scratch_buffer = ColorBuffer(width, height) 
    elif scratch_buffer.width != width or scratch_buffer.height != height:
        raise ValueError("`scratch_buffer` is provided but its demension "
                        f"{scratch_buffer.width}x{scratch_buffer.height} "
                        "does not match the buffer's dimension "
                        f"{width}x{height}.")
    # Write the FXAA processed buffer to scratch_buffer
    data = buffer.data
    scratch_data = scratch_buffer.data
    luminance_map = [0.299 * c.r + 0.587 * c.g + 0.114 * c.b for c in data]
    for row_starting in range(width, width * (height - 1), width):
        last_row_starting = row_starting - width
        next_row_starting = row_starting + width
        for x in range(1, width - 1):
            # Calculate the indices for buffer.data and luminance_map
            current = row_starting + x
            north = last_row_starting + x
            south = next_row_starting + x
            west = current - 1
            east = current + 1
            nw = north - 1
            ne = north + 1
            sw = south - 1
            se = south + 1
            # Edge & direction detection
            to_be_blended: list[Color] = [data[current]]
            if abs(luminance_map[north] - luminance_map[south]) > threshold:
                to_be_blended.extend((data[north], data[south]))
            if abs(luminance_map[west] - luminance_map[east]) > threshold:
                to_be_blended.extend((data[west], data[east]))
            if abs(luminance_map[nw] - luminance_map[se]) > threshold:
                to_be_blended.extend((data[nw], data[se]))
            if abs(luminance_map[ne] - luminance_map[sw]) > threshold:
                to_be_blended.extend((data[ne], data[sw]))
            # Blending
            coef = 1 / len(to_be_blended)
            color = scratch_data[current]
            color.r = sum(color.r for color in to_be_blended) * coef
            color.g = sum(color.g for color in to_be_blended) * coef
            color.b = sum(color.b for color in to_be_blended) * coef
    # Copy the first row, last row, first column and last column
    for i in range(width):
        # Top
        target_color_top = scratch_data[i]
        original_color_top = data[i]
        target_color_top.r = original_color_top.r
        target_color_top.g = original_color_top.g
        target_color_top.b = original_color_top.b
        # Bottom
        target_color_bottom = scratch_data[i + last_row_starting]
        original_color_bottom = data[i + last_row_starting]
        target_color_bottom.r = original_color_bottom.r
        target_color_bottom.g = original_color_bottom.g
        target_color_bottom.b = original_color_bottom.b
    last_x = width - 1
    for row_starting in range(0, width * height, width):
        # Left
        target_color_left = scratch_data[row_starting]
        original_color_left = data[row_starting]
        target_color_left.r = original_color_left.r
        target_color_left.g = original_color_left.g
        target_color_left.b = original_color_left.b
        # Right
        target_color_right = scratch_data[row_starting + last_x]
        original_color_right = data[row_starting + last_x]
        target_color_right.r = original_color_right.r
        target_color_right.g = original_color_right.g
        target_color_right.b = original_color_right.b
    # Swap the data in `scratch_buffer` and `buffer`
    scratch_buffer.data, buffer.data = buffer.data, scratch_buffer.data
    return buffer

SSAAoff = SSAA(0)
SSAAx2 = SSAA(2)
SSAAx4 = SSAA(4)

_SAMPLES_0 = tuple()
_SAMPLES_2 = ((-0.25, -0.25), (0.25, 0.25))
_SAMPLES_4 = ((-0.375, -0.125), ( 0.125, -0.375), 
              ( 0.375,  0.125), (-0.125,  0.375))
_SAMPLES_8 = ((-0.4375, -0.3125), (-0.3125, -0.4375), 
              (-0.0625, -0.4375), ( 0.1875, -0.4375),
              ( 0.4375, -0.3125), ( 0.4375, -0.0625), 
              ( 0.4375,  0.1875), ( 0.3125,  0.4375))
_SAMPLES_16 = ((-0.5625, -0.4375), (-0.4375, -0.5625), 
               (-0.3125, -0.3125), (-0.1875, -0.6875),
               (-0.0625, -0.4375), ( 0.0625, -0.8125), 
               ( 0.1875, -0.1875), ( 0.3125, -0.6875),
               ( 0.4375, -0.3125), ( 0.5625, -0.0625), 
               ( 0.6875, -0.5625), ( 0.8125, -0.3125),
               (-0.8125,  0.1875), (-0.6875,  0.4375), 
               (-0.4375,  0.8125), (-0.3125,  0.6875))

MSAAoff = MSAA(_SAMPLES_0, None)
MSAAx2 = MSAA(_SAMPLES_2, 1)
MSAAx4 = MSAA(_SAMPLES_4, 2)
MSAAx8 = MSAA(_SAMPLES_8, 3)
MSAAx16 = MSAA(_SAMPLES_16, 4)

AAAoff = AAA(_SAMPLES_0, None)
AAAx2 = AAA(_SAMPLES_2, 1)
AAAx4 = AAA(_SAMPLES_4, 2)
AAAx8 = AAA(_SAMPLES_8, 3)
AAAx16 = AAA(_SAMPLES_16, 4)

FXAAon = FXAA()
FXAAoff = False
