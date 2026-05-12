"""Fireflies.ai transcript nodes for AceTeam."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .get_transcript import FirefliesGetTranscriptNode
from .list_transcripts import FirefliesListTranscriptsNode
from .search_transcripts import FirefliesSearchTranscriptsNode

if TYPE_CHECKING:
    from workflow_engine.core.node import EagerNodeRegistryBuilder


def register_nodes(builder: EagerNodeRegistryBuilder) -> None:
    builder.register_node_class(FirefliesListTranscriptsNode)
    builder.register_node_class(FirefliesGetTranscriptNode)
    builder.register_node_class(FirefliesSearchTranscriptsNode)


__all__ = [
    "FirefliesGetTranscriptNode",
    "FirefliesListTranscriptsNode",
    "FirefliesSearchTranscriptsNode",
    "register_nodes",
]
