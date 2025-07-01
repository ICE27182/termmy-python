

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Iterator

from ..colors import Color
from ..core import NormFloat

@dataclass(slots=True, kw_only=True)
class Node:
    x: NormFloat = 0.0
    y: NormFloat = 0.0
    z: float = 0.0
    # Hidden to encourage the user to use `add_child` instead of directly 
    # manipulating `_children`, which may lead to a node is a (grand)parent
    # of itself. Also to maintain order.
    _children: list[Node] = field(default_factory=list)
    
    def add_child(self, child: Node) -> Node:
        """Add a new child.

        Returns:
            Node: It returns itself for method chaining.
        
        Raises:
           ValueError: If the parent/ancestor of the node or the node itself 
                       cannot be added as a child. 
        """
        if child is self or child.is_parent_of(self):
            raise ValueError("The parent/ancestor of the node or the node "
                             "itself cannot be added as a child.")
        else:
            self._children.append(child)
            self._children.sort(key=lambda node: node.z)
        return self
    
    def remove_child(self, child: Node) -> Node:
        """Remove a child from this node.

        Returns:
            Node: It returns itself for method chaining.

        Raises:
            ValueError: If `child` is not a child of this node.
        """
        self._children.remove(child)
        return self
    
    def __contains__(self, node: Node) -> bool:
        return self.is_parent_of(node)
        
    def is_parent_of(self, node: Node) -> bool:
        """Return True if `node` is a child or a descendant of this node.

        Returns:
            bool: True if `node` is a child or a descendant of this node, 
                False otherwise. Whether the two nodes are the same node is
                not considered.
        """
        # TODO Can be optimized since since _children is ordered
        return (node in self._children
                or any(child.is_parent_of(node) 
                       for child in self._children))
    
    def is_direct_parent_of(self, node: Node) -> bool:
        """Return True if `node` is a direct child of this node.

        Returns:
            bool: True if `node` is a direct child of this node, 
                False otherwise.
                Whether the two nodes are the same node is not considered.
        """
        # TODO Can be optimized to O(log n) since _children is ordered
        return node in self._children
    
    def children(self) -> Iterator[Node]:
        """Return an iterator over the children of this node."""
        return iter(self._children)

    def _render(
        self, 
        width: int, 
        height: int, 
        x_offset: NormFloat,
        y_offset: NormFloat,
        out: dict[int, Color],
    ) -> dict[int, Color]:
        """
        Returns:
            dict[int, Color]: A dictionary mapping from pixel indices to 
                colors.It is expected that the indices are smaller than
                `width * height`.
        """
        for child in self._children:
            child._render(width, height, 
                          x_offset + self.x, 
                          y_offset + self.y, 
                          out)
        return out