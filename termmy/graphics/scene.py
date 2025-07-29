

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Iterator

from .node import Node
from ..buffers import ColorBuffer
from ..buffers.text_tag import TextTag

@dataclass(slots=True)
class Scene:
    # In the rendering output, base may be streched to the size of the output.
    base: ColorBuffer
    # Hidden to maintain its order.
    _nodes: list[Node] = field(default_factory=list)
    text_tags: list[TextTag] = field(default_factory=list)

    def add_node(self, node: Node) -> Scene:
        """Add a new node. Returns itself for chaining."""
        self._nodes.append(node)
        self._nodes.sort(key=lambda node: node.z)
        return self
    
    def remove_node(self, node: Node) -> Scene:
        """Remove a node from this node.

        Returns:
            Scene: Returns itself for chaining.

        Raises:
            ValueError: If `node` is not a node of this scene.
        """
        self._nodes.remove(node)
        return self
    
    def nodes(self) -> Iterator[Node]:
        """Return an iterator over the nodes in the scene."""
        return iter(self._nodes)
