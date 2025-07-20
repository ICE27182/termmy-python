

from __future__ import annotations

from .vec2 import Vec2
from .matrix2x2 import Mat2

from dataclasses import dataclass, field

@dataclass(slots=True)
class Transform2D:
    translate: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    pivot: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    _scale: float = 1.0
    _rotation_radians: float = 0.0
    _mat: Mat2 = field(default_factory=Mat2.get_identity_matrix)
    _parent: Transform2D | None = None

    def __post_init__(self) -> None:
        self._mat = Mat2.rotation(self._rotation_radians) * self._scale
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

    def apply(self, vec: Vec2) -> Vec2:
        """Apply this transform and all its parent transforms to the provided
        vector. The `vec` passed in will not be mutated.
        
        Returns:
            Vec2: A new Vec2 object.
        """
        current = self
        while current is not None:
            vec = (
                current._mat * (vec - current.pivot)
                + current.pivot + current.translate
            )
            current = current._parent
        return vec
    
    def unapply(self, vec: Vec2) -> Vec2:
        """Unapply this transform and all its parent transforms to the provided
        vector. The `vec` passed in will not be mutated.

        Returns:
            Vec2: A new Vec2 object.
        """
        parents_and_self: list[Transform2D] = []
        current = self
        while current is not None:
            parents_and_self.append(current)
            current = current._parent
        for parent in reversed(parents_and_self):
            vec = (
                parent._mat.get_inverse()
                * (vec - parent.translate - parent.pivot)
                + parent.pivot
            )
        return vec
    
    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, value: float) -> None:
        self._scale = value
        self._mat = Mat2.rotation(self._rotation_radians) * value
    
    @property
    def rotation_radians(self) -> float:
        return self._rotation_radians

    @rotation_radians.setter
    def rotation_radians(self, value: float) -> None:
        self._rotation_radians = value
        self._mat = Mat2.rotation(value) * self._scale
    
    @property
    def parent(self) -> Transform2D | None:
        return self._parent

    @parent.setter
    def parent(self, value: Transform2D | None) -> None:
        self._parent = value
        if self._parent and self.check_for_self_parenting():
            raise ValueError("Transform cannot be a child or descendant "
                             "of itself.")
