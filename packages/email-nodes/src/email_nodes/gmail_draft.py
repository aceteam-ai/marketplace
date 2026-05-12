"""Gmail draft creation node via Google API."""

import base64
import os
from email.mime.text import MIMEText
from functools import cached_property
from typing import Literal

import httpx
from overrides import override
from pydantic import Field
from workflow_engine import Context, Data, Node, NodeTypeInfo, Params, StringValue


class GmailDraftParams(Params):
    pass


class GmailDraftInput(Data):
    to: StringValue = Field(title="To", description="The recipient email address.")
    subject: StringValue = Field(title="Subject", description="The email subject line.")
    body: StringValue = Field(title="Body", description="The email body text.")


class GmailDraftOutput(Data):
    draft_id: StringValue = Field(title="Draft ID", description="The Gmail draft ID.")
    message: StringValue = Field(title="Message", description="The status message.")


class GmailDraftNode(Node[GmailDraftInput, GmailDraftOutput, GmailDraftParams]):
    """Create a Gmail draft. Requires GMAIL_ACCESS_TOKEN environment variable."""

    TYPE_INFO = NodeTypeInfo.from_parameter_type(
        name="GmailDraft",
        display_name="Gmail Draft",
        description="Create a draft email in Gmail.",
        version="1.0.0",
        parameter_type=GmailDraftParams,
    )
    type: Literal["GmailDraft"] = "GmailDraft"

    @cached_property
    def input_type(self):
        return GmailDraftInput

    @cached_property
    def output_type(self):
        return GmailDraftOutput

    @override
    async def run(self, context: Context, input: GmailDraftInput) -> GmailDraftOutput:
        import json

        token = os.environ.get("GMAIL_ACCESS_TOKEN")
        if not token:
            return GmailDraftOutput(
                draft_id=StringValue(""),
                message=StringValue("GMAIL_ACCESS_TOKEN environment variable is required"),
            )

        msg = MIMEText(input.body.root)
        msg["To"] = input.to.root
        msg["Subject"] = input.subject.root
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://gmail.googleapis.com/gmail/v1/users/me/drafts",
                json={"message": {"raw": raw}},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        return GmailDraftOutput(
            draft_id=StringValue(data.get("id", "")),
            message=StringValue(f"Draft created for {input.to.root}"),
        )
