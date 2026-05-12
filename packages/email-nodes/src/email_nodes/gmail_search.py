"""Gmail search node via Google API."""

import os
from functools import cached_property
from typing import Literal

import httpx
from overrides import override
from pydantic import Field
from workflow_engine import Context, Data, Node, NodeTypeInfo, Params, StringValue


class GmailSearchParams(Params):
    max_results: StringValue = Field(
        title="Max Results",
        default=StringValue("10"),
        description="The maximum number of results to return.",
    )


class GmailSearchInput(Data):
    query: StringValue = Field(
        title="Query",
        description="The Gmail search query (same syntax as Gmail search bar).",
    )


class GmailSearchOutput(Data):
    results: StringValue = Field(
        title="Results",
        description="The search results as a JSON string.",
    )


class GmailSearchNode(Node[GmailSearchInput, GmailSearchOutput, GmailSearchParams]):
    """Search Gmail messages. Requires GMAIL_ACCESS_TOKEN environment variable."""

    TYPE_INFO = NodeTypeInfo.from_parameter_type(
        name="GmailSearch",
        display_name="Gmail Search",
        description="Search Gmail messages using the Gmail API.",
        version="1.0.0",
        parameter_type=GmailSearchParams,
    )
    type: Literal["GmailSearch"] = "GmailSearch"

    @cached_property
    def input_type(self):
        return GmailSearchInput

    @cached_property
    def output_type(self):
        return GmailSearchOutput

    @override
    async def run(self, context: Context, input: GmailSearchInput) -> GmailSearchOutput:
        import json

        token = os.environ.get("GMAIL_ACCESS_TOKEN")
        if not token:
            return GmailSearchOutput(
                results=StringValue(json.dumps({"error": "GMAIL_ACCESS_TOKEN environment variable is required"}))
            )

        max_results = int(self.params.max_results.root)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                params={"q": input.query.root, "maxResults": max_results},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        messages = []
        async with httpx.AsyncClient() as client:
            for msg in data.get("messages", []):
                detail = await client.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}",
                    params={"format": "metadata", "metadataHeaders": ["Subject", "From", "Date"]},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30,
                )
                if detail.status_code == 200:
                    headers = {
                        h["name"]: h["value"]
                        for h in detail.json().get("payload", {}).get("headers", [])
                    }
                    messages.append({
                        "id": msg["id"],
                        "subject": headers.get("Subject", ""),
                        "from": headers.get("From", ""),
                        "date": headers.get("Date", ""),
                        "snippet": detail.json().get("snippet", ""),
                    })

        return GmailSearchOutput(results=StringValue(json.dumps(messages, indent=2)))
