

from __future__ import annotations

from .vec3 import Vec3
from .matrix import Matrix

from collections.abc import Iterable
from typing import Self, Final, overload, override
from math import sin, cos
from numbers import Number

class Mat3(Matrix):
    __slots__ = ["a11", "a12", "a13", "a21", "a22", "a23", "a31", "a32", "a33"]
    _dimension: Final[int] = 3
    a11: float
    a12: float
    a13: float
    a21: float
    a22: float
    a23: float
    a31: float
    a32: float
    a33: float
    @override
    def __init__(self, data: Iterable[float]) -> None:
        if len(data) != 9:
            raise ValueError(f"`len(data)` must be 9. Got {len(data)}")
        self.a11, self.a12, self.a13, self.a21, self.a22, self.a23, self.a31, self.a32, self.a33 = data
    @override    
    def __eq__(self, mat: Self) -> bool:
        # Compare all individual attributes one by one
        return (
            self.a11 == mat.a11 and self.a12 == mat.a12 and self.a13 == mat.a13 and
            self.a21 == mat.a21 and self.a22 == mat.a22 and self.a23 == mat.a23 and
            self.a31 == mat.a31 and self.a32 == mat.a32 and self.a33 == mat.a33
        )
    
    @property
    def _data(self) -> list[float]:
        return [self.a11, self.a12, self.a13,
                self.a21, self.a22, self.a23,
                self.a31, self.a32, self.a33]
    
    @override
    @classmethod
    def get_identity_matrix(cls) -> Mat3:
        return cls((1, 0, 0,
                    0, 1, 0,
                    0, 0, 1))
    
    @classmethod
    def rotationX(cls, theta: float) -> Mat3:
        """Rotation matrix around the X-axis of angle `theta` (in radians)."""
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        return cls((
            1, 0, 0,
            0, cos_theta, -sin_theta,
            0, sin_theta, cos_theta,
        ))
    @classmethod
    def rotationY(cls, theta: float) -> Mat3:
        """Rotation matrix around the Y-axis of angle `theta` (in radians)."""
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        return cls((
            cos_theta, 0, sin_theta,
            0, 1, 0,
            -sin_theta, 0, cos_theta,
        ))
    @classmethod
    def rotationZ(cls, theta: float) -> Mat3:
        """Rotation matrix around the Z-axis of angle `theta` (in radians)."""
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        return cls((
            cos_theta, -sin_theta, 0,
            sin_theta, cos_theta, 0,
            0, 0, 1,
        ))

    @override
    def __getitem__(self, position: tuple[int, int]) -> int | float:
        # Access individual attributes directly
        if position[0] == 0:
            if position[1] == 0:
                return self.a11
            elif position[1] == 1:
                return self.a12
            elif position[1] == 2:
                return self.a13
        elif position[0] == 1:
            if position[1] == 0:
                return self.a21
            elif position[1] == 1:
                return self.a22
            elif position[1] == 2:
                return self.a23
        elif position[0] == 2:
            if position[1] == 0:
                return self.a31
            elif position[1] == 1:
                return self.a32
            elif position[1] == 2:
                return self.a33
        raise IndexError("Invalid position for 3x3 matrix")

    @override
    def __setitem__(self, position: tuple[int, int], value: int | float) -> None:
        # Update individual attributes directly
        if position[0] == 0:
            if position[1] == 0:
                self.a11 = value
            elif position[1] == 1:
                self.a12 = value
            elif position[1] == 2:
                self.a13 = value
        elif position[0] == 1:
            if position[1] == 0:
                self.a21 = value
            elif position[1] == 1:
                self.a22 = value
            elif position[1] == 2:
                self.a23 = value
        elif position[0] == 2:
            if position[1] == 0:
                self.a31 = value
            elif position[1] == 1:
                self.a32 = value
            elif position[1] == 2:
                self.a33 = value
        else:
            raise IndexError("Invalid position for 3x3 matrix")
        
    @overload
    def __imul__(self, other: Self) -> Self: ...
    @overload
    def __imul__(self, other: Number) -> Self: ...
    @override
    def  __imul__(self, other: Self | Number) -> Self:
        if isinstance(other, Mat3):
            a11 = self.a11
            a12 = self.a12
            a13 = self.a13
            a21 = self.a21
            a22 = self.a22
            a23 = self.a23
            a31 = self.a31
            a32 = self.a32
            a33 = self.a33
            self.a11 = a11 * other.a11 + a12 * other.a21 + a13 * other.a31
            self.a12 = a11 * other.a12 + a12 * other.a22 + a13 * other.a32
            self.a13 = a11 * other.a13 + a12 * other.a23 + a13 * other.a33
            self.a21 = a21 * other.a11 + a22 * other.a21 + a23 * other.a31
            self.a22 = a21 * other.a12 + a22 * other.a22 + a23 * other.a32
            self.a23 = a21 * other.a13 + a22 * other.a23 + a23 * other.a33
            self.a31 = a31 * other.a11 + a32 * other.a21 + a33 * other.a31
            self.a32 = a31 * other.a12 + a32 * other.a22 + a33 * other.a32
            self.a33 = a31 * other.a13 + a32 * other.a23 + a33 * other.a33
        elif isinstance(other, Number):
            self.a11 *= other
            self.a12 *= other
            self.a13 *= other
            
            self.a21 *= other
            self.a22 *= other
            self.a23 *= other
            
            self.a31 *= other
            self.a32 *= other
            self.a33 *= other
        else:
            raise TypeError("Unsupported operand type for matrix multiplication")
        return self
    
    def __iadd__(self, other: Self) -> Self:
        self.a11 += other.a11
        self.a12 += other.a12
        self.a13 += other.a13
        self.a21 += other.a21
        self.a22 += other.a22
        self.a23 += other.a23
        self.a31 += other.a31
        self.a32 += other.a32
        self.a33 += other.a33
        return self
    
    def __add__(self, other: Self) -> Mat3:
        return Mat3((
            self.a11 + other.a11, self.a12 + other.a12, self.a13 + other.a13,
            self.a21 + other.a21, self.a22 + other.a22, self.a23 + other.a23,
            self.a31 + other.a31, self.a32 + other.a32, self.a33 + other.a33,
        ))

    def __isub__(self, other: Self) -> Self:
        self.a11 -= other.a11
        self.a12 -= other.a12
        self.a13 -= other.a13
        self.a21 -= other.a21
        self.a22 -= other.a22
        self.a23 -= other.a23
        self.a31 -= other.a31
        self.a32 -= other.a32
        self.a33 -= other.a33
        return self
    
    def __sub__(self, other: Self) -> Mat3:
        return Mat3((
            self.a11 - other.a11, self.a12 - other.a12, self.a13 - other.a13,
            self.a21 - other.a21, self.a22 - other.a22, self.a23 - other.a23,
            self.a31 - other.a31, self.a32 - other.a32, self.a33 - other.a33,
        ))

    @overload
    def __mul__(self, other: Self) -> Mat3: ...
    @overload
    def __mul__(self, other: Vec3) -> Vec3: ...
    @overload
    def __mul__(self, other: Number) -> Mat3: ...
    @overload
    def __mul__(self, other: Iterable[Number]) -> tuple[Number]: ...
    @overload
    def __mul__(self, other: Matrix) -> Matrix: ...
    @override
    def __mul__(self, other: Self | Vec3 | Number) -> Mat3 | Vec3:
        if isinstance(other, Mat3):
            return Mat3((
                self.a11*other.a11 + self.a12*other.a21 + self.a13*other.a31,
                self.a11*other.a12 + self.a12*other.a22 + self.a13*other.a32,
                self.a11*other.a13 + self.a12*other.a23 + self.a13*other.a33,
                
                self.a21*other.a11 + self.a22*other.a21 + self.a23*other.a31,
                self.a21*other.a12 + self.a22*other.a22 + self.a23*other.a32,
                self.a21*other.a13 + self.a22*other.a23 + self.a23*other.a33,
                
                self.a31*other.a11 + self.a32*other.a21 + self.a33*other.a31,
                self.a31*other.a12 + self.a32*other.a22 + self.a33*other.a32,
                self.a31*other.a13 + self.a32*other.a23 + self.a33*other.a33,
            ))
        elif isinstance(other, Vec3):
            return Vec3(
                self.a11 * other.x + self.a12 * other.y + self.a13 * other.z,
                self.a21 * other.x + self.a22 * other.y + self.a23 * other.z,
                self.a31 * other.x + self.a32 * other.y + self.a33 * other.z,
            )
        elif isinstance(other, Number):
            return Mat3((
                self.a11 * other, self.a12 * other, self.a13 * other,
                self.a21 * other, self.a22 * other, self.a23 * other,
                self.a31 * other, self.a32 * other, self.a33 * other,
            ))
        else:
            return super().__mul__(other)

    def iadd_mat3(self, mat: Self) -> Self:
        self.a11 += mat.a11
        self.a12 += mat.a12
        self.a13 += mat.a13
        self.a21 += mat.a21
        self.a22 += mat.a22
        self.a23 += mat.a23
        self.a31 += mat.a31
        self.a32 += mat.a32
        self.a33 += mat.a33
        return self
    
    def add_mat3(self, mat: Self) -> Mat3:
        return Mat3((
            self.a11 + mat.a11, self.a12 + mat.a12, self.a13 + mat.a13,
            self.a21 + mat.a21, self.a22 + mat.a22, self.a23 + mat.a23,
            self.a31 + mat.a31, self.a32 + mat.a32, self.a33 + mat.a33,
        ))

    def isub_mat3(self, mat: Self) -> Self:
        self.a11 -= mat.a11
        self.a12 -= mat.a12
        self.a13 -= mat.a13
        self.a21 -= mat.a21
        self.a22 -= mat.a22
        self.a23 -= mat.a23
        self.a31 -= mat.a31
        self.a32 -= mat.a32
        self.a33 -= mat.a33
        return self
    
    def sub_mat3(self, mat: Self) -> Mat3:
        return Mat3((
            self.a11 - mat.a11, self.a12 - mat.a12, self.a13 - mat.a13,
            self.a21 - mat.a21, self.a22 - mat.a22, self.a23 - mat.a23,
            self.a31 - mat.a31, self.a32 - mat.a32, self.a33 - mat.a33,
        ))
    
    def imul_mat3(self, mat: Self) -> Self:
        a11 = self.a11
        a12 = self.a12
        a13 = self.a13
        a21 = self.a21
        a22 = self.a22
        a23 = self.a23
        a31 = self.a31
        a32 = self.a32
        a33 = self.a33
        self.a11 = a11 * mat.a11 + a12 * mat.a21 + a13 * mat.a31
        self.a12 = a11 * mat.a12 + a12 * mat.a22 + a13 * mat.a32
        self.a13 = a11 * mat.a13 + a12 * mat.a23 + a13 * mat.a33
        self.a21 = a21 * mat.a11 + a22 * mat.a21 + a23 * mat.a31
        self.a22 = a21 * mat.a12 + a22 * mat.a22 + a23 * mat.a32
        self.a23 = a21 * mat.a13 + a22 * mat.a23 + a23 * mat.a33
        self.a31 = a31 * mat.a11 + a32 * mat.a21 + a33 * mat.a31
        self.a32 = a31 * mat.a12 + a32 * mat.a22 + a33 * mat.a32
        self.a33 = a31 * mat.a13 + a32 * mat.a23 + a33 * mat.a33
        return self
    
    def imul_num(self, number: Number) -> Self:
        self.a11 *= number
        self.a12 *= number
        self.a13 *= number
        
        self.a21 *= number
        self.a22 *= number
        self.a23 *= number
        
        self.a31 *= number
        self.a32 *= number
        self.a33 *= number
        return self
    
    def mul_mat3(self, mat: Self) -> Mat3:
        return Mat3(
            (
                self.a11 * mat.a11 + self.a12 * mat.a21 + self.a13 * mat.a31,
                self.a11 * mat.a12 + self.a12 * mat.a22 + self.a13 * mat.a32,
                self.a11 * mat.a13 + self.a12 * mat.a23 + self.a13 * mat.a33,
                
                self.a21 * mat.a11 + self.a22 * mat.a21 + self.a23 * mat.a31,
                self.a21 * mat.a12 + self.a22 * mat.a22 + self.a23 * mat.a32,
                self.a21 * mat.a13 + self.a22 * mat.a23 + self.a23 * mat.a33,
                
                self.a31 * mat.a11 + self.a32 * mat.a21 + self.a33 * mat.a31,
                self.a31 * mat.a12 + self.a32 * mat.a22 + self.a33 * mat.a32,
                self.a31 * mat.a13 + self.a32 * mat.a23 + self.a33 * mat.a33,
            )
        )
    
    def mul_num(self, number: Number) -> Mat3:
        return Mat3(
            (
                self.a11 * number, self.a12 * number, self.a13 * number,
                self.a21 * number, self.a22 * number, self.a23 * number,
                self.a31 * number, self.a32 * number, self.a33 * number,
            )
        )

    def mul_vec3(self, vec:Vec3) -> Vec3:
        return Vec3(
            self.a11 * vec.x + self.a12 * vec.y + self.a13 * vec.z,
            self.a21 * vec.x + self.a22 * vec.y + self.a23 * vec.z,
            self.a31 * vec.x + self.a32 * vec.y + self.a33 * vec.z,
        )

    @override
    def get_determinant(self) -> float:
        """Calculate the determinant of the 3x3 matrix."""
        return (
            self.a11 * (self.a22 * self.a33 - self.a23 * self.a32)
            - self.a12 * (self.a21 * self.a33 - self.a23 * self.a31)
            + self.a13 * (self.a21 * self.a32 - self.a22 * self.a31)
        )
    
    @override
    def get_adjugate(self) -> Mat3:
        """Calculate the adjugate (adjoint) of the 3x3 matrix."""
        return Mat3((
            (self.a22 * self.a33 - self.a23 * self.a32), 
            -(self.a12 * self.a33 - self.a13 * self.a32),
            (self.a12 * self.a23 - self.a13 * self.a22), 
            
            -(self.a21 * self.a33 - self.a23 * self.a31),
            (self.a11 * self.a33 - self.a13 * self.a31), 
            -(self.a11 * self.a23 - self.a13 * self.a21),
            
            (self.a21 * self.a32 - self.a22 * self.a31), 
            -(self.a11 * self.a32 - self.a12 * self.a31),
            (self.a11 * self.a22 - self.a12 * self.a21), 
        ))
    
    @override
    def get_inverse(self) -> Mat3:
        """Calculate the inverse of the 3x3 matrix."""
        det = self.get_determinant()
        if det == 0:
            raise ValueError("The matrix is singular (determinant is 0) and does not have an inverse.")
        coef = 1 / det
        adjugate = self.get_adjugate()
        return Mat3((
            adjugate.a11 * coef, adjugate.a12 * coef, adjugate.a13 * coef,
            adjugate.a21 * coef, adjugate.a22 * coef, adjugate.a23 * coef,
            adjugate.a31 * coef, adjugate.a32 * coef, adjugate.a33 * coef,
        ))
