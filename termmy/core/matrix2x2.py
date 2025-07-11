

from .vec2 import Vec2, Vec2i, Vec2Rela
from .matrix import Matrix

from collections.abc import Iterable
from typing import Self, Final
from math import sin, cos

class Mat2(Matrix):
    __slots__ = ("a11", "a12", "a21", "a22")
    _dimension: Final[int] = 2
    a11: float
    a12: float
    a21: float
    a22: float

    @property
    def _data(self) -> list[float]:
        return [self.a11, self.a12, self.a21, self.a22]


    def __init__(self, data: Iterable[float]) -> None:
        if len(data) != 4:
            raise ValueError(f"`len(data)` must be 4. Got {len(data)}")
        self.a11, self.a12, self.a21, self.a22 = data
        self._dimension = 2
    
    def __eq__(self, mat: Self) -> bool:
        # Compare all individual attributes one by one
        return (
            self.a11 == mat.a11 and self.a12 == mat.a12
             and self.a21 == mat.a21 and self.a22 == mat.a22
        )
    
    @classmethod
    def get_identity_matrix(cls) -> Self:
        return cls(
            [
                1, 0,
                0, 1,
            ]
        )
    
    @classmethod
    def rotation(cls, theta: float) -> Self:
        """Rotation matrix of angle `theta` (in radians)."""
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        return cls([
            cos_theta, -sin_theta,
            sin_theta, cos_theta,
        ])

    def __getitem__(self, position: tuple[int, int]) -> int | float:
        # Access individual attributes directly
        if position[0] == 0:
            if position[1] == 0:
                return self.a11
            elif position[1] == 1:
                return self.a12
        elif position[0] == 1:
            if position[1] == 0:
                return self.a21
            elif position[1] == 1:
                return self.a22
        raise IndexError("Invalid position for 3x3 matrix")

    def __setitem__(self, position: tuple[int, int], value: int | float) -> None:
        # Update individual attributes directly
        if position[0] == 0:
            if position[1] == 0:
                self.a11 = value
            elif position[1] == 1:
                self.a12 = value
        elif position[0] == 1:
            if position[1] == 0:
                self.a21 = value
            elif position[1] == 1:
                self.a22 = value
        else:
            raise IndexError("Invalid position for 3x3 matrix")
        
    def __imul__(self, mat: Self) -> Self:
        self.a11 = self.a11 * mat.a11 + self.a12 * mat.a21
        self.a12 = self.a11 * mat.a12 + self.a12 * mat.a22

        self.a21 = self.a21 * mat.a11 + self.a22 * mat.a21
        self.a22 = self.a21 * mat.a12 + self.a22 * mat.a22
        return self
    
    def mul_mat2(self, mat: Self) -> Self:
        return Mat2(
            [
                self.a11 * mat.a11 + self.a12 * mat.a21,
                self.a11 * mat.a12 + self.a12 * mat.a22,
                
                self.a21 * mat.a11 + self.a22 * mat.a21,
                self.a21 * mat.a12 + self.a22 * mat.a22,
            ]
        )
    
    def mul_vec2(self, vec:Vec2) -> Vec2:
        return Vec2(
            self.a11 * vec.x + self.a12 * vec.y,
            self.a21 * vec.x + self.a22 * vec.y,
        )

    def get_determinant(self) -> float:
        return self.a11 * self.a22 - self.a12 * self.a21
    
    def get_adjugate(self) -> Self:
        return Mat2([self.a22, -self.a21,
                     -self.a12, self.a11])
    
    def get_inverse(self) -> Self:
        det = self.get_determinant()
        if det == 0:
            raise ValueError("The matrix is singular (determinant is 0) and does not have an inverse.")
        coef = 1 / det
        adjugate = self.get_adjugate()
        return Mat2([
            adjugate.a11 * coef, adjugate.a12 * coef,
            adjugate.a21 * coef, adjugate.a22 * coef,
        ])
    