"""Fireflies get transcript node."""

import os
from functools import cached_property
from typing import Literal

import httpx
from overrides import override
from pydantic import Field
from workflow_engine import Context, Data, Node, NodeTypeInfo, Params, StringValue

FIREFLIES_API = "https://api.fireflies.ai/graphql"


class FirefliesGetTranscriptParams(Params):
    pass


class FirefliesGetTranscriptInput(Data):
    transcript_id: StringValue = Field(
        title="Transcript ID",
        description="The Fireflies transcript ID.",
    )


class FirefliesGetTranscriptOutput(Data):
    transcript: StringValue = Field(
        title="Transcript",
        description="The full transcript as a JSON string.",
    )


class FirefliesGetTranscriptNode(
    Node[FirefliesGetTranscriptInput, FirefliesGetTranscriptOutput, FirefliesGetTranscriptParams],
):
    """Fetch a full Fireflies transcript by ID. Requires FIREFLIES_API_KEY environment variable."""

    TYPE_INFO = NodeTypeInfo.from_parameter_type(
        name="FirefliesGetTranscript",
        display_name="Fireflies Get Transcript",
        description="Fetch the full text of a Fireflies.ai meeting transcript.",
        version="1.0.0",
        parameter_type=FirefliesGetTranscriptParams,
    )
    type: Literal["FirefliesGetTranscript"] = "FirefliesGetTranscript"

    @cached_property
    def input_type(self):
        return FirefliesGetTranscriptInput

    @cached_property
    def output_type(self):
        return FirefliesGetTranscriptOutput

    @override
    async def run(
        self, context: Context, input: FirefliesGetTranscriptInput
    ) -> FirefliesGetTranscriptOutput:
        import json

        api_key = os.environ.get("FIREFLIES_API_KEY")
        if not api_key:
            return FirefliesGetTranscriptOutput(
                transcript=StringValue(json.dumps({"error": "FIREFLIES_API_KEY environment variable is required"}))
            )

        query = """
        query Transcript($id: String!) {
            transcript(id: $id) {
                id
                title
                date
                duration
                participants
                sentences {
                    speaker_name
                    text
                    start_time
                    end_time
                }
                summary {
                    overview
                    action_items
                    keywords
                }
            }
        }
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                FIREFLIES_API,
                json={"query": query, "variables": {"id": input.transcript_id.root}},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        transcript = data.get("data", {}).get("transcript", {})
        return FirefliesGetTranscriptOutput(
            transcript=StringValue(json.dumps(transcript, indent=2))
        )
