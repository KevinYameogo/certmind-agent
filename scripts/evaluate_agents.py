"""Evaluation harness for CertMind agents."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.assessment_agent import AssessmentAgent
from agents.critic_verifier import CriticVerifierAgent
from agents.engagement_agent import EngagementAgent
from agents.learning_path_curator import LearningPathCuratorAgent
from agents.manager_insights import ManagerInsightsAgent
from agents.orchestrator import OrchestratorAgent
from agents.study_plan_generator import StudyPlanGeneratorAgent


DATA_DIR = PROJECT_ROOT / "synthetic-data"


class EvaluationHarness:
    """Runs deterministic quality checks across synthetic learner scenarios."""

    def __init__(self) -> None:
        self.learners = self._load_json(DATA_DIR / "learner_profiles.json")
        self.catalog = self._load_json(DATA_DIR / "certification_catalog.json")
        self.valid_certifications = {cert["id"] for cert in self.catalog["certifications"]}
        self.curator = LearningPathCuratorAgent()
        self.planner = StudyPlanGeneratorAgent()
        self.engagement = EngagementAgent()
        self.assessment = AssessmentAgent()
        self.manager = ManagerInsightsAgent()
        self.orchestrator = OrchestratorAgent()
        self.critic = CriticVerifierAgent()

    def run(self) -> dict[str, Any]:
        """Run all checks and return a scorecard."""
        checks = []
        for learner in self.learners:
            checks.extend(self._evaluate_learner(learner))

        checks.extend(self._evaluate_manager())
        checks.extend(self._evaluate_orchestrator_guardrails())
        checks.extend(self._evaluate_critic_negative_case())

        passed = sum(1 for check in checks if check["passed"])
        score = round((passed / len(checks)) * 100, 1) if checks else 0
        return {
            "score": score,
            "passed": passed,
            "total": len(checks),
            "checks": checks,
        }

    def _evaluate_learner(self, learner: dict[str, Any]) -> list[dict[str, Any]]:
        role = learner["role"]
        cert = learner["certification_target"]
        learner_id = learner["learner_id"]
        employee_id = learner["employee_id"]

        learning_path = self.curator.run(role=role, target=cert)
        study_plan = self.planner.run(learner_id=learner_id, certification=cert)
        engagement = self.engagement.run(employee_id=employee_id)
        assessment = self.assessment.run(learner_id=learner_id, certification=cert)

        return [
            self._check(
                f"{learner_id}: curator citations",
                lambda: "[source:" in learning_path.lower(),
                "Learning path should include grounded citations.",
            ),
            self._check(
                f"{learner_id}: planner structure",
                lambda: bool(study_plan["weekly_plan"]) and "readiness" in study_plan and "skill_gap" in study_plan,
                "Study plan should expose weekly plan, readiness, and skill-gap reasoning.",
            ),
            self._check(
                f"{learner_id}: engagement timing",
                lambda: bool(engagement["suggested_study_slots"]) and bool(engagement["avoid_windows"]),
                "Engagement should include suggested slots and peak-meeting avoid windows.",
            ),
            self._check(
                f"{learner_id}: assessment citations",
                lambda: len(assessment["questions"]) == 5
                and all("[source:" in question["citation"].lower() for question in assessment["questions"]),
                "Assessment should generate five cited questions.",
            ),
            self._check(
                f"{learner_id}: no hallucinated cert codes",
                lambda: not self._hallucinated_codes([learning_path, study_plan, engagement, assessment]),
                "Outputs should not contain unknown certification codes.",
            ),
            self._check(
                f"{learner_id}: critic approved assessment",
                lambda: assessment["critic_verdict"]["approved"] is True,
                "Assessment output should pass critic gating.",
            ),
        ]

    def _evaluate_manager(self) -> list[dict[str, Any]]:
        insights = self.manager.run()
        return [
            self._check(
                "manager: aggregate-only privacy",
                lambda: all(item["average_readiness_score"] is None for item in insights["certification_risk"]),
                "Single-learner certification groups should hide readiness scores.",
            ),
            self._check(
                "manager: source citations",
                lambda: all("[source:" in citation for citation in insights["source_citations"]),
                "Manager insights should cite the synthetic data sources used.",
            ),
        ]

    def _evaluate_orchestrator_guardrails(self) -> list[dict[str, Any]]:
        normal = self.orchestrator.run("I'm a Cloud Engineer and I want to get AZ-204 certified")
        blocked = OrchestratorAgent().run("Help jane@example.com get AZ-204 certified")
        return [
            self._check(
                "orchestrator: end-to-end trace",
                lambda: normal["critic_approved"] is True and len(normal["trace"]) >= 5,
                "Orchestrator should emit trace entries for the end-to-end workflow.",
            ),
            self._check(
                "orchestrator: feedback loop",
                lambda: normal["result"]["feedback_loop"]["triggered"] is True,
                "Assessment below threshold should loop back to study planning.",
            ),
            self._check(
                "orchestrator: PII guardrail",
                lambda: blocked["result"]["blocked"] is True and "Email" in blocked["critic_issues"][0],
                "Orchestrator should reject PII in input.",
            ),
        ]

    def _evaluate_critic_negative_case(self) -> list[dict[str, Any]]:
        verdict = self.critic.review("Prepare for AZ-204", "Study FA-999. You are lazy.")
        return [
            self._check(
                "critic: blocks bad output",
                lambda: verdict["approved"] is False and len(verdict["issues"]) >= 3,
                "Critic should block missing citations, fake cert codes, and inappropriate language.",
            )
        ]

    def _hallucinated_codes(self, outputs: list[Any]) -> set[str]:
        text = json.dumps(outputs, ensure_ascii=True, default=str)
        seen = set(re.findall(r"\b[A-Z]{2}-\d{3}\b", text))
        return {code for code in seen if code not in self.valid_certifications}

    @staticmethod
    def _check(name: str, predicate: Callable[[], bool], description: str) -> dict[str, Any]:
        try:
            passed = bool(predicate())
            error = None
        except Exception as exc:
            passed = False
            error = str(exc)
        return {
            "name": name,
            "passed": passed,
            "description": description,
            "error": error,
        }

    @staticmethod
    def _load_json(path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    """Run the evaluation harness and print a scorecard."""
    scorecard = EvaluationHarness().run()
    print(json.dumps(scorecard, indent=2))
    if scorecard["score"] < 100:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
