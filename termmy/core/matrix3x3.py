

from .vec3 import Vec3
from .matrix import Matrix

from collections.abc import Iterable
from typing import Self
from math import sin, cos

class Matrix3x3(Matrix):
    __slots__ = ["a11", "a12", "a13", "a21", "a22", "a23", "a31", "a32", "a33"]

    def __init__(self, data=Iterable) -> None:
        if len(data) != 9:
            raise ValueError(f"`len(data)` must be 9. Got {len(data)}")
        self.a11, self.a12, self.a13, self.a21, self.a22, self.a23, self.a31, self.a32, self.a33 = data
    
    def __eq__(self, mat: Self) -> bool:
        # Compare all individual attributes one by one
        return (
            self.a11 == mat.a11 and self.a12 == mat.a12 and self.a13 == mat.a13 and
            self.a21 == mat.a21 and self.a22 == mat.a22 and self.a23 == mat.a23 and
            self.a31 == mat.a31 and self.a32 == mat.a32 and self.a33 == mat.a33
        )
    
    @classmethod
    def get_identity_matrix(cls) -> Self:
        return cls(
            (
                1, 0, 0,
                0, 1, 0,
                0, 0, 1,
            )
        )

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
        
    def __imul__(self, mat: Self) -> Self:
        self.a11 = self.a11 * mat.a11 + self.a12 * mat.a21 + self.a13 * mat.a31
        self.a12 = self.a11 * mat.a12 + self.a12 * mat.a22 + self.a13 * mat.a32
        self.a13 = self.a11 * mat.a13 + self.a12 * mat.a23 + self.a13 * mat.a33
        
        self.a21 = self.a21 * mat.a11 + self.a22 * mat.a21 + self.a23 * mat.a31
        self.a22 = self.a21 * mat.a12 + self.a22 * mat.a22 + self.a23 * mat.a32
        self.a23 = self.a21 * mat.a13 + self.a22 * mat.a23 + self.a23 * mat.a33
        
        self.a31 = self.a31 * mat.a11 + self.a32 * mat.a21 + self.a33 * mat.a31
        self.a32 = self.a31 * mat.a12 + self.a32 * mat.a22 + self.a33 * mat.a32
        self.a33 = self.a31 * mat.a13 + self.a32 * mat.a23 + self.a33 * mat.a33
        return self
    
    def __mul__(self, mat: Self) -> Self:
        return Matrix3x3(
            [
                self.a11 * mat.a11 + self.a12 * mat.a21 + self.a13 * mat.a31,
                self.a11 * mat.a12 + self.a12 * mat.a22 + self.a13 * mat.a32,
                self.a11 * mat.a13 + self.a12 * mat.a23 + self.a13 * mat.a33,
                
                self.a21 * mat.a11 + self.a22 * mat.a21 + self.a23 * mat.a31,
                self.a21 * mat.a12 + self.a22 * mat.a22 + self.a23 * mat.a32,
                self.a21 * mat.a13 + self.a22 * mat.a23 + self.a23 * mat.a33,
                
                self.a31 * mat.a11 + self.a32 * mat.a21 + self.a33 * mat.a31,
                self.a31 * mat.a12 + self.a32 * mat.a22 + self.a33 * mat.a32,
                self.a31 * mat.a13 + self.a32 * mat.a23 + self.a33 * mat.a33,
            ]
        )
    
    def mul_vector(self, vec:Vec3) -> Vec3:
        return Vec3(
            self.a11 * vec.x + self.a12 * vec.y + self.a13 * vec.z,
            self.a21 * vec.x + self.a22 * vec.y + self.a23 * vec.z,
            self.a31 * vec.x + self.a32 * vec.y + self.a33 * vec.z,
        )

    def get_determinant(self) -> float:
        """Calculate the determinant of the 3x3 matrix."""
        return (
            self.a11 * (self.a22 * self.a33 - self.a23 * self.a32)
            - self.a12 * (self.a21 * self.a33 - self.a23 * self.a31)
            + self.a13 * (self.a21 * self.a32 - self.a22 * self.a31)
        )
    
    def get_adjugate(self) -> Self:
        """Calculate the adjugate (adjoint) of the 3x3 matrix."""
        return Matrix3x3([
            (self.a22 * self.a33 - self.a23 * self.a32), 
            -(self.a12 * self.a33 - self.a13 * self.a32),
            (self.a12 * self.a23 - self.a13 * self.a22), 
            
            -(self.a21 * self.a33 - self.a23 * self.a31),
            (self.a11 * self.a33 - self.a13 * self.a31), 
            -(self.a11 * self.a23 - self.a13 * self.a21),
            
            (self.a21 * self.a32 - self.a22 * self.a31), 
            -(self.a11 * self.a32 - self.a12 * self.a31),
            (self.a11 * self.a22 - self.a12 * self.a21), 
        ])
    
    def get_inverse(self) -> Self:
        """Calculate the inverse of the 3x3 matrix."""
        det = self.get_determinant()
        if det == 0:
            raise ValueError("The matrix is singular (determinant is 0) and does not have an inverse.")
        coef = 1 / det
        adjugate = self.get_adjugate()
        return Matrix3x3(
            adjugate.a11 * coef, adjugate.a12 * coef, adjugate.a13 * coef,
            adjugate.a21 * coef, adjugate.a22 * coef, adjugate.a23 * coef,
            adjugate.a31 * coef, adjugate.a32 * coef, adjugate.a33 * coef,
        )
    
    @staticmethod
    def rotationX(theta: float) -> Self:
        """Rotate the matrix around the X-axis by angle `theta` (in radians)."""
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        return Matrix3x3([
            1, 0, 0,
            0, cos_theta, -sin_theta,
            0, sin_theta, cos_theta,
        ])
    @staticmethod
    def rotationY(theta: float) -> Self:
        """Rotate the matrix around the Y-axis by angle `theta` (in radians)."""
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        return Matrix3x3([
            cos_theta, 0, sin_theta,
            0, 1, 0,
            -sin_theta, 0, cos_theta,
        ])
    @staticmethod
    def rotationZ(theta: float) -> Self:
        """Rotate the matrix around the Z-axis by angle `theta` (in radians)."""
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        return Matrix3x3([
            cos_theta, -sin_theta, 0,
            sin_theta, cos_theta, 0,
            0, 0, 1,
        ])
