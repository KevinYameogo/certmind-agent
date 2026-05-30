"""Smoke test a deployed CertMind hosted agent endpoint."""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from azure.identity import DefaultAzureCredential


def main() -> None:
    endpoint = os.getenv("CERTMIND_HOSTED_AGENT_ENDPOINT")
    if not endpoint:
        raise SystemExit("Set CERTMIND_HOSTED_AGENT_ENDPOINT to the hosted agent endpoint URL.")

    payload = {
        "message": "I'm a Cloud Engineer and I want to get AZ-204 certified",
    }
    print("Getting authentication token...")
    credential = DefaultAzureCredential()
    token = credential.get_token("https://ml.azure.com/.default").token

    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Foundry-Features": "HostedAgents=V1Preview",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        raise SystemExit(f"Hosted agent returned HTTP {exc.code}: {exc.read().decode('utf-8')}") from exc
    except URLError as exc:
        raise SystemExit(f"Could not reach hosted agent endpoint: {exc}") from exc

    print(body)
    if "AZ-204" not in body:
        raise SystemExit("Hosted agent response did not include expected AZ-204 content.")


if __name__ == "__main__":
    main()
