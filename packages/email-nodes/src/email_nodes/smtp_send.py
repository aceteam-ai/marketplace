"""SMTP email send node."""

import asyncio
import os
import smtplib
from email.mime.text import MIMEText
from functools import cached_property
from typing import Literal

from overrides import override
from pydantic import Field
from workflow_engine import BooleanValue, Context, Data, Node, NodeTypeInfo, Params, StringValue


class SmtpSendParams(Params):
    smtp_host: StringValue = Field(
        title="SMTP Host",
        default=StringValue("smtp.gmail.com"),
        description="The SMTP server hostname.",
    )
    smtp_port: StringValue = Field(
        title="SMTP Port",
        default=StringValue("587"),
        description="The SMTP server port.",
    )


class SmtpSendInput(Data):
    to: StringValue = Field(title="To", description="The recipient email address.")
    subject: StringValue = Field(title="Subject", description="The email subject line.")
    body: StringValue = Field(title="Body", description="The email body text.")


class SmtpSendOutput(Data):
    success: BooleanValue = Field(title="Success", description="Whether the email was sent.")
    message: StringValue = Field(title="Message", description="The status message.")


class SmtpSendNode(Node[SmtpSendInput, SmtpSendOutput, SmtpSendParams]):
    """Send an email via SMTP. Requires SMTP_USERNAME and SMTP_PASSWORD environment variables."""

    TYPE_INFO = NodeTypeInfo.from_parameter_type(
        name="SmtpSend",
        display_name="SMTP Send",
        description="Send an email via SMTP.",
        version="1.0.0",
        parameter_type=SmtpSendParams,
    )
    type: Literal["SmtpSend"] = "SmtpSend"

    @cached_property
    def input_type(self):
        return SmtpSendInput

    @cached_property
    def output_type(self):
        return SmtpSendOutput

    @override
    async def run(self, context: Context, input: SmtpSendInput) -> SmtpSendOutput:
        username = os.environ.get("SMTP_USERNAME")
        password = os.environ.get("SMTP_PASSWORD")
        if not username or not password:
            return SmtpSendOutput(
                success=BooleanValue(False),
                message=StringValue("SMTP_USERNAME and SMTP_PASSWORD environment variables are required"),
            )

        msg = MIMEText(input.body.root)
        msg["Subject"] = input.subject.root
        msg["From"] = username
        msg["To"] = input.to.root

        host = self.params.smtp_host.root
        port = int(self.params.smtp_port.root)

        def _send():
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

        await asyncio.to_thread(_send)
        return SmtpSendOutput(
            success=BooleanValue(True),
            message=StringValue(f"Email sent to {input.to.root}"),
        )
