# Copyright (c) Microsoft. All rights reserved.

from __future__ import annotations

import json
import os
from collections.abc import AsyncGenerator

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from dotenv import load_dotenv
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from agents.hosted_entrypoint import run_certmind_request


load_dotenv()

os.environ.setdefault("AZURE_AI_PROJECT_ENDPOINT", os.getenv("FOUNDRY_PROJECT_ENDPOINT", ""))
os.environ.setdefault("AZURE_AI_MODEL_DEPLOYMENT", os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-5-mini"))
os.environ.setdefault("MICROSOFT_LEARN_MCP_URL", "https://learn.microsoft.com/api/mcp")
os.environ.setdefault("CERTMIND_USE_FOUNDRY_LIVE", "false")

app = InvocationAgentServerHost()


def _run(message: str) -> str:
    result = run_certmind_request(message)
    return json.dumps(result, indent=2)


@app.invoke_handler
async def handle_invoke(request: Request):
    """Handle CertMind hosted-agent invocations."""
    data = await request.json()
    stream = data.get("stream", False)
    user_message = data.get("message")

    if user_message is None:
        error = "Missing 'message' in request"
        if stream:
            return StreamingResponse(content=error, status_code=400)
        return Response(content=error, status_code=400)

    if stream:

        async def stream_response() -> AsyncGenerator[str]:
            yield _run(user_message)

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    return JSONResponse({"response": _run(user_message)})


if __name__ == "__main__":
    app.run()
