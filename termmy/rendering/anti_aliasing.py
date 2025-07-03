

from typing import overload

from ..buffers import Buffer2D, ColorBuffer
from ..colors import Color

type SSAA = int
SSAAoff = 0
SSAAx2 = 2
SSAAx4 = 4

type SamplePattern = tuple[tuple[float, float], ...]
type MSAA = SamplePattern
type AAA = SamplePattern

MSAAoff = tuple()
MSAAx2 = ((-0.25, -0.25), (0.25, 0.25))
MSAAx4 = ((-0.375, -0.125), (0.125, -0.375), 
          (0.375, 0.125), (-0.125, 0.375))
MSAAx8 = ((-0.4375, -0.3125), (-0.3125, -0.4375), 
          (-0.0625, -0.4375), (0.1875, -0.4375),
          (0.4375, -0.3125), (0.4375, -0.0625), 
          (0.4375, 0.1875), (0.3125, 0.4375))
MSAAx16 = ((-0.5625, -0.4375), (-0.4375, -0.5625), 
           (-0.3125, -0.3125), (-0.1875, -0.6875),
           (-0.0625, -0.4375), ( 0.0625, -0.8125), 
           ( 0.1875, -0.1875), ( 0.3125, -0.6875),
           ( 0.4375, -0.3125), ( 0.5625, -0.0625), 
           ( 0.6875, -0.5625), ( 0.8125, -0.3125),
           (-0.8125,  0.1875), (-0.6875,  0.4375), 
           (-0.4375,  0.8125), (-0.3125,  0.6875))

AAAoff = MSAAoff
AAAx2 = MSAAx2
AAAx4 = MSAAx4
AAAx8 = MSAAx8
AAAx16 = MSAAx16

@overload
def apply_fxaa_to(buffer: Buffer2D) -> Buffer2D:
    """Apply FXAA to the provided 2D buffer. 

    It is more efficient to apply FXAA directly to a ColorBuffer 
    than a Buffer2D object.
    
    Returns:
        Buffer2D: The buffer itself with FXAA applied.
    """
@overload
def apply_fxaa_to(buffer: ColorBuffer) -> ColorBuffer:
    """Apply FXAA to the provided color buffer. 

    It is more efficient to apply FXAA directly to a ColorBuffer 
    than a Buffer2D object.
    
    Returns:
        ColorBuffer: The buffer itself with FXAA applied.
    """
def apply_fxaa_to(buffer: Buffer2D | ColorBuffer) -> Buffer2D | ColorBuffer:
    raise NotImplementedError

