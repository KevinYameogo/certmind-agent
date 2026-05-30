"""Hosted-agent bridge for Microsoft Foundry Toolkit scaffolds."""

from __future__ import annotations

from typing import Any

from agents.orchestrator import OrchestratorAgent


def run_certmind_request(message: str) -> dict[str, Any]:
    """Run a CertMind request through the orchestrator.

    Use this function from the Foundry Toolkit-generated hosted-agent handler.
    Keep the Toolkit scaffold's generated protocol files intact and delegate
    request handling here.
    """
    return OrchestratorAgent().run(message)
