"""Fireflies search transcripts node."""

import os
from functools import cached_property
from typing import Literal

import httpx
from overrides import override
from pydantic import Field
from workflow_engine import Context, Data, Node, NodeTypeInfo, Params, StringValue

FIREFLIES_API = "https://api.fireflies.ai/graphql"


class FirefliesSearchTranscriptsParams(Params):
    limit: StringValue = Field(
        title="Limit",
        default=StringValue("10"),
        description="The maximum number of results to return.",
    )


class FirefliesSearchTranscriptsInput(Data):
    query: StringValue = Field(
        title="Query",
        description="The search keyword or phrase.",
    )


class FirefliesSearchTranscriptsOutput(Data):
    results: StringValue = Field(
        title="Results",
        description="The matching transcripts as a JSON string.",
    )


class FirefliesSearchTranscriptsNode(
    Node[FirefliesSearchTranscriptsInput, FirefliesSearchTranscriptsOutput, FirefliesSearchTranscriptsParams],
):
    """Search Fireflies transcripts by keyword. Requires FIREFLIES_API_KEY environment variable."""

    TYPE_INFO = NodeTypeInfo.from_parameter_type(
        name="FirefliesSearchTranscripts",
        display_name="Fireflies Search Transcripts",
        description="Search Fireflies.ai meeting transcripts by keyword.",
        version="1.0.0",
        parameter_type=FirefliesSearchTranscriptsParams,
    )
    type: Literal["FirefliesSearchTranscripts"] = "FirefliesSearchTranscripts"

    @cached_property
    def input_type(self):
        return FirefliesSearchTranscriptsInput

    @cached_property
    def output_type(self):
        return FirefliesSearchTranscriptsOutput

    @override
    async def run(
        self, context: Context, input: FirefliesSearchTranscriptsInput
    ) -> FirefliesSearchTranscriptsOutput:
        import json

        api_key = os.environ.get("FIREFLIES_API_KEY")
        if not api_key:
            return FirefliesSearchTranscriptsOutput(
                results=StringValue(json.dumps({"error": "FIREFLIES_API_KEY environment variable is required"}))
            )

        limit = int(self.params.limit.root)
        query = """
        query Transcripts($limit: Int) {
            transcripts(limit: $limit) {
                id
                title
                date
                duration
                participants
                sentences {
                    speaker_name
                    text
                }
            }
        }
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                FIREFLIES_API,
                json={"query": query, "variables": {"limit": 50}},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        search_term = input.query.root.lower()
        results = []
        for t in data.get("data", {}).get("transcripts", []):
            text_blob = " ".join(
                s.get("text", "") for s in t.get("sentences", [])
            ).lower()
            if search_term in text_blob or search_term in t.get("title", "").lower():
                results.append({
                    "id": t["id"],
                    "title": t.get("title"),
                    "date": t.get("date"),
                    "duration": t.get("duration"),
                })
                if len(results) >= limit:
                    break

        return FirefliesSearchTranscriptsOutput(
            results=StringValue(json.dumps(results, indent=2))
        )
