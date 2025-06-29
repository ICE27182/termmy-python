import unittest
import termmy
from termmy.buffers.color_buffer import _ColorBuffer_Array, ColorBuffer
from random import sample
from time import time
from timeit import timeit
from array import array
from termmy.colors import Color

_ColorBuffer_ListOfColor = ColorBuffer

class TPerformance_list_vs_array(unittest.TestCase):
    @staticmethod
    def _read(width, height, number = 1000):
        lc = _ColorBuffer_ListOfColor(width, height)
        af = _ColorBuffer_Array(width, height)

        l: list[Color] = lc.data
        a: array[float] = af.data
        reading_list = sample(tuple(range(width*height)), width*height//5)
        
        t_l = timeit("tuple((c.r, c.g, c.b, c.a) for i in reading_list if (c := l[i]))", globals=locals(), number=number)
        t_a = timeit("tuple((a[s+0], a[s+1], a[s+2], a[s+3]) for i in reading_list if (s := i << 2))", globals=locals(), number=number)
        print(f"Random Read {width}x{height}: \n\tlist[Color]: {t_l}\n\tarray('f'): {t_a}")

        t_l = timeit("tuple((c.r, c.g, c.b, c.a) for c in lc.data)", globals=locals(), number=number)
        t_a = timeit("tuple((a[i+0], a[i+1], a[i+2], a[i+3]) for i in range(0, width*height<<2, 4))", globals=locals(), number=number)
        print(f"Sequential Read {width}x{height}: \n\tlist[Color]: {t_l}\n\tarray('f'): {t_a}")

    def test_read(self):
        # Low resolution
        TPerformance_list_vs_array._read(128, 80, 5000)
        # Render performance
        TPerformance_list_vs_array._read(240, 180, 1000)
        # Reading from an image
        TPerformance_list_vs_array._read(1920, 1080, 10)

        """
        Random Read 128x80: 
                list[Color]: 0.5288902089960175
                array('f'): 1.564541832995019
        Sequential Read 128x80: 
                list[Color]: 1.8934305409929948
                array('f'): 7.021749624997028
        Random Read 240x180: 
                list[Color]: 0.5272623330092756
                array('f'): 1.3298458330100402
        Sequential Read 240x180: 
                list[Color]: 1.686654917008127
                array('f'): 6.2909102919948054
        Random Read 1920x1080: 
                list[Color]: 0.9774700419948203
                array('f'): 1.021761374999187
        Sequential Read 1920x1080: 
                list[Color]: 0.9212598750018515
                array('f'): 3.325803083003848
        """
        
