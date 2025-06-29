# import unittest
# import termmy
# from os import system
# from collections.abc import Callable
# from time import time
# def clear(): system("clear")

# @unittest.skip("Refactored")
# class TPerformance_str_ansi_colored(unittest.TestCase):
#     @staticmethod
#     def generate(type:int, width:int, height:int) -> termmy.Frame24:
#             from random import randint
#             frame = termmy.Frame24(width, height)
#             for y in range(height):
#                 y_width = y * width
#                 for x in range(width):
#                     if type == 0:
#                         frame.data[y_width + x] = (x * y % 256, (x + y) % 256, (x - y) % 256)
#                     elif type == 1:
#                         frame.data[y_width + x] = (0,0,0) if (x + y) % 2 else (255, 255, 255)
#                     elif type == 2:
#                         frame.data[y_width + x] = (randint(0, 255), randint(0, 255), randint(0, 255))
#             return frame
    
#     @unittest.skip("Best algorithms found (str_ansi_colored_ChatGPT_4o), some methods used no longer exist")
#     def test_output(self):
#         clear()
#         print(self.generate(0, 96, 54).str_ansi_colored())
#         print(self.generate(0, 96, 54).str_ansi_colored_ChatGPT_4o())
#         print(self.generate(0, 96, 54).str_ansi_colored_fixed_RGB_digits_no_for_loop())
#         print(self.generate(0, 96, 54).str_ansi_colored_fixed_RGB_digits_no_for_loop_no_slicing())
#         print(self.generate(1, 96, 54).str_ansi_colored())
#         print(self.generate(1, 96, 54).str_ansi_colored_ChatGPT_4o())
#         print(self.generate(1, 96, 54).str_ansi_colored_fixed_RGB_digits_no_for_loop())
#         print(self.generate(1, 96, 54).str_ansi_colored_fixed_RGB_digits_no_for_loop_no_slicing())

#     @unittest.skip("Best algorithms found (str_ansi_colored_ChatGPT_4o), some methods used no longer exist")
#     def test_compare(self):
        
        
#         class Test:
#             resolution_lo:tuple[int, int] = (160, 90)
#             resolution_hi:tuple[int, int] = (1920, 1080)
#             n_lo = 10
#             n_hi = 3
#             def __init__(self, method:Callable[[termmy.Frame24], None]) -> None:
#                 self.method = method
#                 self.time_type0_lo:int = -1
#                 self.time_type0_hi:int = -1
#                 self.time_type1_lo:int = -1
#                 self.time_type1_hi:int = -1
#                 self.time_type2_lo:int = -1
#                 self.time_type2_hi:int = -1
#                 print(self.method(TPerformance_str_ansi_colored.generate(1, *Test.resolution_lo)))
#                 print("\033[0m")
            
#             def run(self) -> None:
#                 n_lo = Test.n_lo
#                 n_hi = Test.n_hi
#                 lo_0 = TPerformance_str_ansi_colored.generate(0, *Test.resolution_lo)
#                 start = time()
#                 for _ in range(n_lo):
#                     self.method(lo_0)
#                 self.time_type0_lo = (time() - start) / n_lo
#                 del lo_0
                
#                 lo_1 = TPerformance_str_ansi_colored.generate(1, *Test.resolution_lo)
#                 start = time()
#                 for _ in range(n_lo):
#                     self.method(lo_1)
#                 self.time_type1_lo = (time() - start) / n_lo
#                 del lo_1

#                 lo_2 = TPerformance_str_ansi_colored.generate(2, *Test.resolution_lo)
#                 start = time()
#                 for _ in range(n_lo):
#                     self.method(lo_2)
#                 self.time_type2_lo = (time() - start) / n_lo
#                 del lo_2

#                 hi_0 = TPerformance_str_ansi_colored.generate(0, *Test.resolution_hi)
#                 start = time()
#                 for _ in range(n_hi):
#                     self.method(hi_0)
#                 self.time_type0_hi = (time() - start) / n_hi
#                 del hi_0
                
#                 hi_1 = TPerformance_str_ansi_colored.generate(1, *Test.resolution_hi)
#                 start = time()
#                 for _ in range(n_hi):
#                     self.method(hi_1)
#                 self.time_type1_hi = (time() - start) / n_hi
#                 del hi_1

#                 hi_2 = TPerformance_str_ansi_colored.generate(2, *Test.resolution_hi)
#                 start = time()
#                 for _ in range(n_hi):
#                     self.method(hi_2)
#                 self.time_type2_hi = (time() - start) / n_hi
#                 del hi_2
            
#             def __str__(self) -> str:
#                 LO_COEF = 4 * 10**4
#                 HI_COEF = 3 * 10**2
#                 lo = (self.time_type0_lo + self.time_type1_lo + self.time_type2_lo) / 3
#                 hi = (self.time_type0_hi + self.time_type1_hi + self.time_type2_hi) / 3
#                 return (
#                     f"Lower resolution {Test.resolution_lo}:\n\t"
#                     f"\033[42m{"  "*round(LO_COEF * lo)}\033[0m{lo}\n\t"
#                     f"0: {self.time_type0_lo}\n\t"
#                     f"1: {self.time_type1_lo}\n\t"
#                     f"2: {self.time_type2_lo}\n"
#                     f"Higher resolution {Test.resolution_hi}:\n\t"
#                     f"\033[43m{"  "*round(HI_COEF * hi)}\033[0m{hi}\n\t"
#                     f"0: {self.time_type0_hi}\n\t"
#                     f"1: {self.time_type1_hi}\n\t"
#                     f"2: {self.time_type2_hi}\n"
#                 )
#         clear()
#         algo1 = Test(lambda frame: frame.str_ansi_colored())
#         algo2 = Test(lambda frame: frame.str_ansi_colored_ChatGPT_4o())
#         algo3 = Test(lambda frame: frame.str_ansi_colored_fixed_RGB_digits_no_for_loop())
#         algo4 = Test(lambda frame: frame.str_ansi_colored_fixed_RGB_digits_no_for_loop_no_slicing())
#         algo1.run()
#         algo2.run()
#         algo3.run()
#         algo4.run()
#         clear()

#         print(algo1)
#         print(algo2)
#         print(algo3)
#         print(algo4)

# @unittest.skip("Refactored")
# class TPerformance_nested_frame_vs_flattend_frame(unittest.TestCase):
#     def test_(self):
#         nested = [[(255, 255, 255)] * 480 for _ in range(270)]
#         start = time()
#         for x in range(480):
#             y = x % 270
#             pixel = nested[y][x]
#             nested[y][x] = (pixel[0] - 127, round(pixel[1] * 0.3), 255)
#         print(f"nested 2d list: {time() - start:E}")

#         flattend = [(255, 255, 255)] * (480 * 270)
#         start = time()
#         for x in range(480):
#             pixel = flattend[x % 270 * 480 + x]
#             nested[y][x] = (pixel[0] - 127, round(pixel[1] * 0.3), 255)
#         print(f"flattened 1d list: {time() - start:E}")

        