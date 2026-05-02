"""
Type Aliases:
    - AbsoFloat: Absolute Float, a non-negative float 
        used for magnitudes, distances, etc.
    - NormFloat: Normalized Float, a float in the range [0.0, 1.0]

Vectors:
    - UV: Texture coordinates, a 2D vector with normalized 
        float components (u, v).
    - Vec2: A 2D vector protocol
    - Vec2i: A 2D vector with integer components (x, y).
    - Vec2f: A 2D vector with float components (x, y).
    - Vec2fNorm: A 2D vector with normalized float components (x, y).
    - Vec3: A 3D vector protocol
    - Vec3f: A 3D vector with float components (x, y, z).
    - Vec3fNorm: A 3D vector with normalized float components (x, y, z).
    
linear_algebra:
    A module containing functions for linear algebra operations.
    
Transforms:
    - Transform: A class for basic 3D/2D transformations 
        (translation, rotation, scaling).
    - LinearTransform: A protocol for linear transformations 
        that can be represented by a 4x4 matrix.
"""

from .type_aliases import AbsoFloat, NormFloat
from .vec import UV, Vec2, Vec2i, Vec2f, Vec2fNorm
from .vec import Vec3, Vec3f, Vec3fNorm
from .transforms import Transform, LinearTransform
from .clear_screen import clear_screen
