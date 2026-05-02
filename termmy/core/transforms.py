

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .vec import Vec3, Vec3f
from .linear_algebra import Matrix4dTuple, mat4t_mul, identity_mat4t
from .linear_algebra import rot_mat_z, rot_mat_y, rot_mat_x


class LinearTransform(Protocol):
    """
    A protocol for linear transforms in the form of a 4x4 matrix.
    
    Methods:
        get_matrix() -> Matrix4dTuple: 
            Returns the 4x4 matrix representation of the linear transform.
    """
    def get_matrix(self) -> Matrix4dTuple: ...
    

@dataclass(slots=True, frozen=False)
class Transform:
    """
    Simple linear transform. It follows the `LinearTransform` protocol.
    
    Apply the transforms in the order of **scale**, **rotation**, and **translation**.
    """
    translation_vec: Vec3f
    rotation_mat: Matrix4dTuple
    scale_vec: Vec3f
    
    def get_matrix(self) -> Matrix4dTuple:
        (r11, r12, r13, _,
         r21, r22, r23, _,
         r31, r32, r33, _,
         _, _, _, _) = self.rotation_mat
        s, t = self.scale_vec, self.translation_vec
        return (
            s.x * r11, s.x * r12, s.x * r13, t.x,
            s.y * r21, s.y * r22, s.y * r23, t.y,
            s.z * r31, s.z * r32, s.z * r33, t.z,
            0.0, 0.0, 0.0, 1.0
        )
    
    ###############################################################
    # Constructors
    ###############################################################
    @classmethod
    def identity(cls) -> Transform:
        return cls(Vec3f.one(), identity_mat4t(), Vec3f.zero())
    
    @classmethod
    def translation(cls, x: float, y: float, z: float) -> Transform:
        return cls(Vec3f(x, y, z), identity_mat4t(), Vec3f.one())
        
    @classmethod
    def scaling(cls, x: float, y: float, z: float) -> Transform:
        return cls(Vec3f.zero(), identity_mat4t(), Vec3f(x, y, z))
    
    @classmethod
    def rotation_z(cls, radians: float) -> Transform:
        return cls(Vec3f.zero(), rot_mat_z(radians), Vec3f.one())
    @classmethod
    def rotation_y(cls, radians: float) -> Transform:
        return cls(Vec3f.zero(), rot_mat_y(radians), Vec3f.one())
    @classmethod
    def rotation_x(cls, radians: float) -> Transform:
        return cls(Vec3f.zero(), rot_mat_x(radians), Vec3f.one())
    
    ###############################################################
    # Inplace modifiers
    ###############################################################
    def translate_by(self, x: float, y: float, z: float) -> Transform:
        """Inplace modifies the transform and returns itself"""
        t = self.translation_vec
        t.x, t.y, t.z = t.x + x, t.y + y, t.z + z
        return self
    def translate_to(self, x: float, y: float, z: float) -> Transform:
        """Inplace modifies the transform and returns itself"""
        t = self.translation_vec
        t.x, t.y, t.z = x, y, z
        return self
    
    def scale_by(self, x: float, y: float, z: float) -> Transform:
        """Inplace modifies the transform and returns itself"""
        s = self.scale_vec
        s.x, s.y, s.z = s.x * x, s.y * y, s.z * z
        return self
    def scale_to(self, x: float, y: float, z: float) -> Transform:
        """Inplace modifies the transform and returns itself"""
        s = self.scale_vec
        s.x, s.y, s.z = x, y, z
        return self

    def rotate_z_by(self, radians: float) -> Transform:
        """Inplace modifies the transform and returns itself"""
        self.rotation_mat = mat4t_mul(self.rotation_mat, rot_mat_z(radians))
        return self
    def rotate_y_by(self, radians: float) -> Transform:
        """Inplace modifies the transform and returns itself"""
        self.rotation_mat = mat4t_mul(self.rotation_mat, rot_mat_y(radians))
        return self
    def rotate_x_by(self, radians: float) -> Transform:
        """Inplace modifies the transform and returns itself"""
        self.rotation_mat = mat4t_mul(self.rotation_mat, rot_mat_x(radians))
        return self
    
    def reset_rotation(self) -> Transform:
        """Inplace modifies the transform and returns itself"""
        self.rotation_mat = identity_mat4t()
        return self
    
    ###############################################################
    # Non-inplace modifiers
    ###############################################################
    def translated_by(self, x: float, y: float, z: float) -> Transform:
        """Returns a new transform with the translation modified."""
        return Transform(
            Vec3f(self.translation_vec.x + x, self.translation_vec.y + y, self.translation_vec.z + z),
            self.rotation_mat,
            self.scale_vec
        )
    def translated_to(self, x: float, y: float, z: float) -> Transform:
        """Returns a new transform with the translation modified."""
        return Transform(
            Vec3f(x, y, z),
            self.rotation_mat,
            self.scale_vec
        )
    
    def scaled_by(self, x: float, y: float, z: float) -> Transform:
        """Returns a new transform with the scale modified."""
        return Transform(
            self.translation_vec,
            self.rotation_mat,
            Vec3f(self.scale_vec.x * x, self.scale_vec.y * y, self.scale_vec.z * z)
        )
    def scaled_to(self, x: float, y: float, z: float) -> Transform:
        """Returns a new transform with the scale modified."""
        return Transform(
            self.translation_vec,
            self.rotation_mat,
            Vec3f(x, y, z)
        )
    
    def rotated_z_by(self, radians: float) -> Transform:
        """Returns a new transform with the rotation modified."""
        return Transform(
            self.translation_vec,
            mat4t_mul(self.rotation_mat, rot_mat_z(radians)),
            self.scale_vec
        )
    def rotated_y_by(self, radians: float) -> Transform:
        """Returns a new transform with the rotation modified."""
        return Transform(
            self.translation_vec,
            mat4t_mul(self.rotation_mat, rot_mat_y(radians)),
            self.scale_vec
        )
    def rotated_x_by(self, radians: float) -> Transform:
        """Returns a new transform with the rotation modified."""
        return Transform(
            self.translation_vec,
            mat4t_mul(self.rotation_mat, rot_mat_x(radians)),
            self.scale_vec
        )
    
    def with_rotation_reset(self) -> Transform:
        """Returns a new transform with the rotation reset."""
        return Transform(
            self.translation_vec,
            identity_mat4t(),
            self.scale_vec
        )
