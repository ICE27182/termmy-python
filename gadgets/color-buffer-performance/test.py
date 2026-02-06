"""
TLNR use list[Color]
"""

import timeit
import random
from dataclasses import dataclass

# --- Constants ---
WIDTH = 300
HEIGHT = 100 
N_PIXELS = WIDTH * HEIGHT
N_OPS = 100_000  # Number of random operations

# --- 1. Slotted Class Setup ---
@dataclass(slots=True)
class ColorSlot:
    r: int
    g: int
    b: int
    a: int = 255

# --- Setup Buffers ---
# A: List of Objects
buf_obj = [ColorSlot(0, 0, 0) for _ in range(N_PIXELS)]

# B: List of Packed Integers (0xAARRGGBB)
buf_int = [0xFF000000] * N_PIXELS

# C: Flat Float List (Stride 3 - RGB)
buf_float_3 = [0.0] * (N_PIXELS * 3)

# D: Flat Float List (Stride 4 - RGBA)
buf_float_4 = [0.0] * (N_PIXELS * 4)

# Pre-calculate random indices to avoid benchmarking the RNG
rand_indices = [random.randint(0, N_PIXELS - 1) for _ in range(N_OPS)]
rand_coords = [(random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)) for _ in range(N_OPS)]

# --- Benchmarks ---

def test_obj_random_write():
    # Simulate: Drawing pixels at random spots
    for i in rand_indices:
        c = buf_obj[i]
        c.r = 255
        c.g = 128
        c.b = 64

def test_int_random_write():
    # Simulate: Packing and writing integer
    # New Color: R=255, G=128, B=64, A=255 -> 0xFFFF8040
    val = 0xFFFF8040 
    a = (val >> 24) & 0xFF
    r = (val >> 16) & 0xFF
    g = (val >> 8) & 0xFF
    b = val & 0xFF
    for i in rand_indices:
        buf_int[i] = (a << 24) | (r << 16) | (g << 8) | b

def test_obj_sequential_read():
    # Simulate: Post-process (brighten) or rendering to string
    total = 0
    for p in buf_obj:
        total += p.r  # Access attribute

def test_int_sequential_read():
    # Simulate: Unpacking for render
    total = 0
    for p in buf_int:
        total += (p >> 16) & 0xFF  # Extract Red

# --- Float Stride Comparison (RGB vs RGBA) ---

def test_float_rgb_write():
    # Stride 3: Requires multiplication
    w = WIDTH
    for x, y in rand_coords:
        idx = (y * w + x) * 3
        buf_float_3[idx] = 1.0     # R
        buf_float_3[idx+1] = 0.5   # G
        buf_float_3[idx+2] = 0.25  # B

def test_float_rgba_write():
    # Stride 4: Can use bit shift (idx << 2)
    w = WIDTH
    for x, y in rand_coords:
        idx = (y * w + x) << 2
        buf_float_4[idx] = 1.0     # R
        buf_float_4[idx+1] = 0.5   # G
        buf_float_4[idx+2] = 0.25  # B

# --- Execution ---
print(f"--- Benchmark: {N_PIXELS} pixels, {N_OPS} random ops ---")

t_obj_w = timeit.timeit(test_obj_random_write, number=100)
print(f"Object Random Write:      {t_obj_w:.4f} s")

t_int_w = timeit.timeit(test_int_random_write, number=100)
print(f"Integer Random Write:     {t_int_w:.4f} s")

print("-" * 20)

t_obj_r = timeit.timeit(test_obj_sequential_read, number=100)
print(f"Object Seq Read:          {t_obj_r:.4f} s")

t_int_r = timeit.timeit(test_int_sequential_read, number=100)
print(f"Integer Seq Read:         {t_int_r:.4f} s")

print("-" * 20)
print("--- Float Stride Optimization ---")

t_f3 = timeit.timeit(test_float_rgb_write, number=100)
print(f"Float RGB (*3):           {t_f3:.4f} s")

t_f4 = timeit.timeit(test_float_rgba_write, number=100)
print(f"Float RGBA (<<2):         {t_f4:.4f} s")