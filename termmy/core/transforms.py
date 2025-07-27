

from __future__ import annotations

from .vec2 import Vec2
from .vertices import Vertex2
from .matrix2x2 import Mat2

from dataclasses import dataclass, field
from enum import IntFlag
from typing import overload
from copy import copy


class TransformInheritance(IntFlag):
    TRANSLATE = 1
    ROTATE = 2
    SCALE = 4
    ALL = TRANSLATE | ROTATE | SCALE
    NONE = 0
    ROTATE_SCALE = ROTATE | SCALE

@dataclass(slots=True)
class Transform2D:
    translate: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    pivot: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    inheritance: TransformInheritance = TransformInheritance.ALL
    scale: float = 1.0
    _rotation_radians: float = 0.0
    _rot_mat: Mat2 = field(default_factory=Mat2.get_identity_matrix)
    _parent: Transform2D | None = None

    def __post_init__(self) -> None:
        self._rot_mat = Mat2.rotation(self._rotation_radians)
        if self._parent and self.check_for_self_parenting():
            raise ValueError("Transform cannot be a child or descendant "
                             "of itself.")
    
    def check_for_self_parenting(self) -> bool:
        current = self._parent
        while current is not None:
            if current == self:
                return True
            current = current._parent
        return False

    @overload
    def apply(self, vertex: Vertex2) -> Vertex2:
        """Apply this transform and all its parent transforms to the provided
        vector. The `vertex` passed in will not be mutated. Its uv coordinates
        will remain the same.
        
        Returns:
            Vertex2: A new `Vertex2` object.
        """
    @overload
    def apply(self, vec2: Vec2) -> Vec2:
        """Apply this transform and all its parent transforms to the provided
        vector. The `vec2` passed in will not be mutated.
        
        Returns:
            Vec2: A new `Vec2` object.
        """
    def apply(self, v: Vec2 | Vertex2) -> Vec2 | Vertex2:
        current = self
        inherit = TransformInheritance.ALL
        new_v = copy(v)
        while current is not None:
            new_v -= current.pivot
            if inherit & TransformInheritance.SCALE:
                new_v *= current.scale
            if inherit & TransformInheritance.ROTATE:
                new_v = current._rot_mat * new_v
            new_v += current.pivot
            if inherit & TransformInheritance.TRANSLATE:
                new_v += current.translate
            inherit = current.inheritance
            current = current._parent
        return new_v
    
    @overload
    def unapply(self, vertex: Vertex2) -> Vertex2:
        """Unapply this transform and all its parent transforms to the provided
        vertex. The `vertex` passed in will not be mutated.

        Returns:
            Vertex2: A new Vertex2 object.
        """
    @overload
    def unapply(self, vec: Vec2) -> Vec2:
        """Unapply this transform and all its parent transforms to the provided
        vector. The `vec` passed in will not be mutated.

        Returns:
            Vec2: A new Vec2 object.
        """
    def unapply(self, value: Vertex2 | Vec2) -> Vertex2 | Vec2:
        parents_and_self: list[Transform2D] = []
        inherits: list[TransformInheritance] = [TransformInheritance.ALL]
        current = self
        new_value = copy(value)
        while current is not None:
            parents_and_self.append(current)
            inherits.append(current.inheritance)
            current = current._parent
        inherits.pop()
        for parent, inherit in zip(reversed(parents_and_self), reversed(inherits)):
            new_value -= parent.pivot
            if inherit & TransformInheritance.TRANSLATE:
                new_value -= parent.translate
            if inherit & TransformInheritance.ROTATE:
                # The transpose is the same as the inverse for rotation matrices
                new_value = parent._rot_mat.get_transposed() * new_value
            if inherit & TransformInheritance.SCALE:
                new_value *= 1.0 / parent.scale
            new_value += parent.pivot
        return new_value

    def get_scale_factor(self) -> float:
        current = self
        inherit = TransformInheritance.SCALE
        v = 1.0
        while current is not None:
            if inherit & TransformInheritance.SCALE:
                v *= current.scale
            inherit = current.inheritance
            current = current._parent
        return v

    def apply_rotation(self, vec: Vec2) -> Vec2:
        """Apply only the rotation of this transform
        and all its parent transforms.
        
        The `vec` passed in will not be mutated.

        Returns:
            Vec2: A new Vec2 object.
        """
        current = self
        inherit = TransformInheritance.ROTATE
        new_vec = Vec2(vec.x, vec.y)
        while current is not None:
            if inherit & TransformInheritance.ROTATE:
                new_vec -= current.pivot
                new_vec = current._rot_mat * new_vec
                new_vec += current.pivot
            inherit = current.inheritance
            current = current._parent
        return new_vec
    
    @property
    def rotation_radians(self) -> float:
        return self._rotation_radians

    @rotation_radians.setter
    def rotation_radians(self, value: float) -> None:
        self._rotation_radians = value
        self._rot_mat = Mat2.rotation(value)
    
    @property
    def parent(self) -> Transform2D | None:
        return self._parent

    @parent.setter
    def parent(self, value: Transform2D | None) -> None:
        self._parent = value
        if self._parent and self.check_for_self_parenting():
            raise ValueError("Transform cannot be a child or descendant "
                             "of itself.")
