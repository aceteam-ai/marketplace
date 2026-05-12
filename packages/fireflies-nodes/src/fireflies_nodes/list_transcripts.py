"""Fireflies list transcripts node."""

import os
from functools import cached_property
from typing import Literal

import httpx
from overrides import override
from pydantic import Field
from workflow_engine import Context, Data, Node, NodeTypeInfo, Params, StringValue

FIREFLIES_API = "https://api.fireflies.ai/graphql"


class FirefliesListTranscriptsParams(Params):
    limit: StringValue = Field(
        title="Limit",
        default=StringValue("20"),
        description="The maximum number of transcripts to return.",
    )


class FirefliesListTranscriptsInput(Data):
    pass


class FirefliesListTranscriptsOutput(Data):
    transcripts: StringValue = Field(
        title="Transcripts",
        description="The list of transcripts as a JSON string.",
    )


class FirefliesListTranscriptsNode(
    Node[FirefliesListTranscriptsInput, FirefliesListTranscriptsOutput, FirefliesListTranscriptsParams],
):
    """List recent Fireflies transcripts. Requires FIREFLIES_API_KEY environment variable."""

    TYPE_INFO = NodeTypeInfo.from_parameter_type(
        name="FirefliesListTranscripts",
        display_name="Fireflies List Transcripts",
        description="List recent meeting transcripts from Fireflies.ai.",
        version="1.0.0",
        parameter_type=FirefliesListTranscriptsParams,
    )
    type: Literal["FirefliesListTranscripts"] = "FirefliesListTranscripts"

    @cached_property
    def input_type(self):
        return FirefliesListTranscriptsInput

    @cached_property
    def output_type(self):
        return FirefliesListTranscriptsOutput

    @override
    async def run(
        self, context: Context, input: FirefliesListTranscriptsInput
    ) -> FirefliesListTranscriptsOutput:
        import json

        api_key = os.environ.get("FIREFLIES_API_KEY")
        if not api_key:
            return FirefliesListTranscriptsOutput(
                transcripts=StringValue(json.dumps({"error": "FIREFLIES_API_KEY environment variable is required"}))
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
            }
        }
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                FIREFLIES_API,
                json={"query": query, "variables": {"limit": limit}},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        transcripts = data.get("data", {}).get("transcripts", [])
        return FirefliesListTranscriptsOutput(
            transcripts=StringValue(json.dumps(transcripts, indent=2))
        )
