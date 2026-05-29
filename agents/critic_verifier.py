"""Critic / Verifier agent for grounded CertMind outputs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.base_agent import AgentConfig, BaseAgent


CATALOG_PATH = PROJECT_ROOT / "synthetic-data" / "certification_catalog.json"


class CriticVerifierAgent(BaseAgent):
    """Validates grounded agent outputs before they reach learners."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config=config)
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        self.valid_certifications = {cert["id"] for cert in catalog["certifications"]}

    def review(self, original_question: str, agent_output: Any) -> dict[str, Any]:
        """Return a structured verdict for another agent's output."""
        output_text = self._to_text(agent_output)
        issues: list[str] = []

        if not self._has_required_citations(agent_output, output_text):
            issues.append("Output contains factual content without required source citations.")

        if not self._addresses_question(original_question, output_text):
            issues.append("Output does not clearly address the original question.")

        hallucinated = self._hallucinated_certifications(output_text)
        if hallucinated:
            issues.append(f"Unknown certification code(s): {', '.join(sorted(hallucinated))}.")

        if not self._is_work_appropriate(output_text):
            issues.append("Output contains language that is not appropriate for a work context.")

        approved = not issues
        return {
            "approved": approved,
            "issues": issues,
            "revised_output": agent_output if approved else self._revise_output(agent_output, issues),
        }

    def _has_required_citations(self, agent_output: Any, output_text: str) -> bool:
        if isinstance(agent_output, dict) and "questions" in agent_output:
            return all("[source:" in question.get("citation", "").lower() for question in agent_output["questions"])
        return "[source:" in output_text.lower()

    @staticmethod
    def _addresses_question(original_question: str, output_text: str) -> bool:
        terms = {
            term
            for term in re.findall(r"[a-z0-9-]+", original_question.lower())
            if len(term) >= 4
        }
        if not terms:
            return True
        lowered = output_text.lower()
        return any(term in lowered for term in terms)

    def _hallucinated_certifications(self, output_text: str) -> set[str]:
        seen_codes = set(re.findall(r"\b[A-Z]{2}-\d{3}\b", output_text))
        return {code for code in seen_codes if code not in self.valid_certifications}

    @staticmethod
    def _is_work_appropriate(output_text: str) -> bool:
        blocked_terms = {"lazy", "stupid", "failure", "worthless", "punish"}
        lowered = output_text.lower()
        return not any(term in lowered for term in blocked_terms)

    @staticmethod
    def _revise_output(agent_output: Any, issues: list[str]) -> dict[str, Any]:
        return {
            "blocked": True,
            "issues": issues,
            "original_output": agent_output,
            "message": "Output requires revision before it is shown to the learner.",
        }

    @staticmethod
    def _to_text(agent_output: Any) -> str:
        if isinstance(agent_output, str):
            return agent_output
        return json.dumps(agent_output, ensure_ascii=True, sort_keys=True)


def verify_response(response: dict) -> dict:
    """Compatibility wrapper for earlier placeholder callers."""
    return CriticVerifierAgent().review(original_question="Verify agent response", agent_output=response)


if __name__ == "__main__":
    sample = {
        "certification_id": "AZ-204",
        "summary": "Use cited AZ-204 practice questions. [source: cert_guide.md]",
    }
    print(json.dumps(CriticVerifierAgent().review("Prepare for AZ-204", sample), indent=2))
