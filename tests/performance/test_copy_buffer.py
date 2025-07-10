from termmy import Color
from unittest import TestCase
from random import random
from timeit import timeit

        
class TPerformance_copy_color_buffer(TestCase):
    @staticmethod
    def copy(data1: tuple[Color], data2: tuple[Color]):
        # assuming the dimensions of the two 2d buffers are the same
        for color1, color2 in zip(data1, data2):
            color2.r = color1.r
            color2.g = color1.g
            color2.b = color1.b
            color2.a = color1.a

    def test_performance(self):
        number = 10**4
        copy = TPerformance_copy_color_buffer.copy
        data2 = tuple(Color() for _ in range(80 * 60))
        data1 = tuple(Color(random(), random(), random(), random()) for _ in range(80 * 60))
        print(timeit("copy(data1, data2)", "", number=number, globals=locals()) * 1000 / number, "ms")

        number = 4*10**3
        data2 = tuple(Color() for _ in range(240 * 144))
        data1 = tuple(Color(random(), random(), random(), random()) for _ in range(240 * 144))
        print(timeit("copy(data1, data2)", "", number=number, globals=locals()) * 1000 / number, "ms")
