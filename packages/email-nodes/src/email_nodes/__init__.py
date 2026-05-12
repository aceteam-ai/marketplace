"""Email workflow nodes for AceTeam."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .gmail_draft import GmailDraftNode
from .gmail_search import GmailSearchNode
from .smtp_send import SmtpSendNode

if TYPE_CHECKING:
    from workflow_engine.core.node import EagerNodeRegistryBuilder


def register_nodes(builder: EagerNodeRegistryBuilder) -> None:
    builder.register_node_class(SmtpSendNode)
    builder.register_node_class(GmailSearchNode)
    builder.register_node_class(GmailDraftNode)


__all__ = [
    "GmailDraftNode",
    "GmailSearchNode",
    "SmtpSendNode",
    "register_nodes",
]
