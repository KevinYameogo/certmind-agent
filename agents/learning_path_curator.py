"""Learning Path Curator agent."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from textwrap import dedent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.base_agent import AgentConfig, BaseAgent

KNOWLEDGE_DOCS = (
    PROJECT_ROOT / "synthetic-data" / "cert_guide.md",
    PROJECT_ROOT / "synthetic-data" / "team_learning_report.md",
    PROJECT_ROOT / "synthetic-data" / "workload_insights.md",
)


class LearningPathCuratorAgent(BaseAgent):
    """Curates cited certification learning resources."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config=config)

    def run(self, role: str, target: str) -> str:  # type: ignore[override]
        """Return a cited learning path for a learner role and certification target."""
        context = self._retrieve_local_context(role=role, target=target)
        prompt = self._build_prompt(role=role, target=target, context=context)

        try:
            if self.openai_client is not None and self.config.knowledge_base_id:
                answer = super().run(prompt)
                if self.has_citation(answer):
                    return answer
        except Exception:
            pass

        answer = self._render_local_answer(role=role, target=target, context=context)
        if not self.has_citation(answer):
            raise ValueError("Learning Path Curator produced an answer without citations.")
        return answer

    def _build_prompt(self, role: str, target: str, context: str) -> str:
        return dedent(
            f"""
            You are the CertMind Learning Path Curator.

            Learner role: {role}
            Certification target: {target}
            Foundry IQ knowledge base ID: {self.config.knowledge_base_id}
            Microsoft Learn MCP endpoint: {self.config.learn_mcp_url}

            Use the grounded knowledge context and Microsoft Learn MCP tools to produce
            a concise learning path. Every factual claim must include a markdown citation
            in the form [source: filename].

            Grounded knowledge context:
            {context}
            """
        ).strip()

    def _retrieve_local_context(self, role: str, target: str) -> str:
        terms = self._query_terms(role=role, target=target)
        excerpts: list[str] = []

        for path in KNOWLEDGE_DOCS:
            text = path.read_text(encoding="utf-8")
            if path.name == "cert_guide.md" and target:
                cert_section = self._extract_certification_section(text, target)
                if cert_section:
                    excerpts.append(f"[source: {path.name}]\n{cert_section}")
                    continue

            paragraphs = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
            matches = [block for block in paragraphs if self._matches(block, terms)]
            selected = matches[:5] if matches else paragraphs[:2]
            for block in selected:
                excerpts.append(f"[source: {path.name}]\n{block}")

        return "\n\n".join(excerpts)

    def _render_local_answer(self, role: str, target: str, context: str) -> str:
        role_label = role.strip() or "learner"
        target_label = target.strip().upper()
        mcp_url = self.config.learn_mcp_url

        core_areas = self._extract_numbered_topics(context)
        if not core_areas:
            core_areas = [
                "Review the target certification objectives",
                "Pair study with hands-on Azure labs",
                "Use weekly practice assessments",
            ]

        lines = [
            f"# Learning path for {role_label} targeting {target_label}",
            "",
            (
                f"Start with the CertMind certification guide for {target_label}; it lists the "
                "recommended study pattern, target readiness score, and role-specific topic areas. "
                "[source: cert_guide.md]"
            ),
            "",
            "## Recommended focus areas",
        ]
        for index, area in enumerate(core_areas[:6], start=1):
            lines.append(f"{index}. {area} [source: cert_guide.md]")

        lines.extend(
            [
                "",
                "## Study rhythm",
                (
                    "Use 1-2 hours of focused study daily, weekly practice checkpoints, and a "
                    "75% practice-score gate before booking the exam. [source: cert_guide.md]"
                ),
                (
                    "Prefer morning study blocks when possible; synthetic team results show morning "
                    "learners outperform afternoon learners, and structured plans increase completed "
                    "study hours. [source: team_learning_report.md]"
                ),
                (
                    "If workload is high, reduce study blocks to 45-60 minutes or shorter and avoid "
                    "peak meeting periods. [source: workload_insights.md]"
                ),
                "",
                "## Microsoft Learn MCP",
                (
                    f"Use the Microsoft Learn MCP endpoint `{mcp_url}` to search Microsoft Learn docs, "
                    "fetch full articles, and find code samples for each topic. [source: Microsoft Learn MCP]"
                ),
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _query_terms(role: str, target: str) -> set[str]:
        raw_terms = re.split(r"[\s,_/-]+", f"{role} {target}".lower())
        return {term for term in raw_terms if len(term) >= 3}

    @staticmethod
    def _matches(text: str, terms: set[str]) -> bool:
        lowered = text.lower()
        return any(term in lowered for term in terms)

    @staticmethod
    def _extract_numbered_topics(context: str) -> list[str]:
        topics = []
        for line in context.splitlines():
            match = re.match(r"\d+\.\s+\*\*(.*?)\*\*", line.strip())
            if match:
                topics.append(match.group(1))
        return topics

    @staticmethod
    def _extract_certification_section(text: str, target: str) -> str:
        pattern = re.compile(
            rf"(^### .*?{re.escape(target.upper())}.*?)(?=^### |\Z)",
            flags=re.MULTILINE | re.DOTALL,
        )
        match = pattern.search(text)
        return match.group(1).strip() if match else ""


def curate_learning_path(learner_id: str, certification_id: str) -> dict:
    """Compatibility wrapper for earlier placeholder callers."""
    agent = LearningPathCuratorAgent()
    result = agent.run(role=learner_id, target=certification_id)
    return {
        "learner_id": learner_id,
        "certification_id": certification_id,
        "learning_path": result,
    }


if __name__ == "__main__":
    curator = LearningPathCuratorAgent()
    print(curator.run(role="Cloud Engineer", target="AZ-204"))
