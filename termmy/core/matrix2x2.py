

from __future__ import annotations

from .vec2 import Vec2, Vec2i, Vec2Rela
from .matrix import Matrix

from collections.abc import Iterable
from typing import Self, Final, overload, override
from math import sin, cos
from numbers import Number

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

    @override
    def __init__(self, data: Iterable[float]) -> None:
        if len(data) != 4:
            raise ValueError(f"`len(data)` must be 4. Got {len(data)}")
        self.a11, self.a12, self.a21, self.a22 = data
        self._dimension = 2
    
    @override
    @classmethod
    def get_identity_matrix(cls) -> Mat2:
        return cls((1, 0,
                    0, 1))
    
    @classmethod
    def rotation(cls, theta: float) -> Mat2:
        """Rotation matrix of angle `theta` (in radians)."""
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        return cls((
            cos_theta, -sin_theta,
            sin_theta, cos_theta,
        ))
    
    @override
    def __eq__(self, mat: Self) -> bool:
        return (
            isinstance(mat, Mat2)
            and self.a11 == mat.a11 and self.a12 == mat.a12
            and self.a21 == mat.a21 and self.a22 == mat.a22
        )

    @override
    def __getitem__(self, position: tuple[int, int]) -> float:
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
        raise IndexError("Invalid position for 2x2 matrix")

    @override
    def __setitem__(self, position: tuple[int, int], value: float) -> None:
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
            raise IndexError("Invalid position for 2x2 matrix")
        
    def __iadd__(self, other: Self) -> Self:
        self.a11 += other.a11
        self.a12 += other.a12
        self.a21 += other.a21
        self.a22 += other.a22
        return self
    
    def __add__(self, other: Self) -> Mat2:
        return Mat2((self.a11 + other.a11, self.a12 + other.a12,
                     self.a21 + other.a21, self.a22 + other.a22))

    def __isub__(self, other: Self) -> Self:
        self.a11 -= other.a11
        self.a12 -= other.a12
        self.a21 -= other.a21
        self.a22 -= other.a22
        return self
    
    def __sub__(self, other: Self) -> Mat2:
        return Mat2((self.a11 - other.a11, self.a12 - other.a12,
                     self.a21 - other.a21, self.a22 - other.a22))    

    @overload
    def __imul__(self, other: Self) -> Self: ...
    @overload
    def __imul__(self, other: Number) -> Self: ...
    def __imul__(self, other: Self | Number) -> Self:
        if isinstance(other, Mat2):
            a11 = self.a11
            a12 = self.a12
            a21 = self.a21
            a22 = self.a22
            self.a11 = a11 * other.a11 + a12 * other.a21
            self.a12 = a11 * other.a12 + a12 * other.a22
            self.a21 = a21 * other.a11 + a22 * other.a21
            self.a22 = a21 * other.a12 + a22 * other.a22
        elif isinstance(other, Number):
            self.a11 *= other
            self.a12 *= other
            self.a21 *= other
            self.a22 *= other
        else:
            raise TypeError("Unsupported operand type for matrix multiplication")
        return self
    
    @overload
    def __mul__(self, other: Self) -> Mat2: ...
    @overload
    def __mul__(self, other: Vec2) -> Vec2: ...
    @overload
    def __mul__(self, other: Number) -> Mat2: ...
    @overload
    def __mul__(self, other: Iterable[Number]) -> tuple[Number]: ...
    @overload
    def __mul__(self, other: Matrix) -> Matrix: ...
    @override
    def __mul__(self, other: Self | Vec2 | Number) -> Mat2 | Vec2:
        if isinstance(other, Mat2):
            return Mat2([self.a11 * other.a11 + self.a12 * other.a21,
                         self.a11 * other.a12 + self.a12 * other.a22,
                         self.a21 * other.a11 + self.a22 * other.a21,
                         self.a21 * other.a12 + self.a22 * other.a22])
        elif isinstance(other, Vec2):
            return Vec2(self.a11 * other.x + self.a12 * other.y,
                        self.a21 * other.x + self.a22 * other.y)
        elif isinstance(other, Number):
            return Mat2((self.a11 * other, self.a12 * other,
                         self.a21 * other, self.a22 * other))
        else:
            return super().__mul__(other)
    
    def iadd_mat2(self, mat: Self) -> Self:
        self.a11 += mat.a11
        self.a12 += mat.a12
        self.a21 += mat.a21
        self.a22 += mat.a22
        return self
    
    def add_mat2(self, mat: Self) -> Mat2:
        return Mat2((self.a11 + mat.a11, self.a12 + mat.a12,
                     self.a21 + mat.a21, self.a22 + mat.a22))

    def isub_mat2(self, mat: Self) -> Self:
        self.a11 -= mat.a11
        self.a12 -= mat.a12
        self.a21 -= mat.a21
        self.a22 -= mat.a22
        return self
    
    def sub_mat2(self, mat: Self) -> Mat2:
        return Mat2((self.a11 - mat.a11, self.a12 - mat.a12,
                     self.a21 - mat.a21, self.a22 - mat.a22))

    def imul_mat2(self, mat: Self) -> Self:
        a11 = self.a11
        a12 = self.a12
        a21 = self.a21
        a22 = self.a22
        self.a11 = a11 * mat.a11 + a12 * mat.a21
        self.a12 = a11 * mat.a12 + a12 * mat.a22
        self.a21 = a21 * mat.a11 + a22 * mat.a21
        self.a22 = a21 * mat.a12 + a22 * mat.a22
        return self
    
    def imul_num(self, number: Number) -> Self:
        self.a11 *= number
        self.a12 *= number
        self.a21 *= number
        self.a22 *= number
        return self
    
    def mul_mat2(self, mat: Self) -> Mat2:
        return Mat2(
            [
                self.a11 * mat.a11 + self.a12 * mat.a21,
                self.a11 * mat.a12 + self.a12 * mat.a22,
                
                self.a21 * mat.a11 + self.a22 * mat.a21,
                self.a21 * mat.a12 + self.a22 * mat.a22,
            ]
        )
    
    def mul_num(self, number: Number) -> Mat2:
        return Mat2((self.a11 * number, self.a12 * number,
                     self.a21 * number, self.a22 * number))
    
    def mul_vec2(self, vec:Vec2) -> Vec2:
        return Vec2(
            self.a11 * vec.x + self.a12 * vec.y,
            self.a21 * vec.x + self.a22 * vec.y,
        )

    @override
    def get_determinant(self) -> float:
        return self.a11 * self.a22 - self.a12 * self.a21
    
    @override
    def get_adjugate(self) -> Mat2:
        return Mat2((self.a22, -self.a12,
                     -self.a21, self.a11))
    
    @override
    def get_inverse(self) -> Mat2:
        """Get the inverse of this 2 dimensional matrix.
        """
        det = self.get_determinant()
        if det == 0.0:
            raise ValueError("The matrix is singular (determinant is 0) "
                             "and does not have an inverse.")
        coef = 1.0 / det
        adjugate = self.get_adjugate()
        return Mat2((
            adjugate.a11 * coef, adjugate.a12 * coef,
            adjugate.a21 * coef, adjugate.a22 * coef,
        ))
    
    @override
    def get_transposed(self) -> Mat2:
        return Mat2((self.a11, self.a21, 
                     self.a12, self.a22))
    