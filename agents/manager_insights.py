"""Manager Insights Agent for privacy-safe team readiness summaries."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.base_agent import AgentConfig, BaseAgent
from agents.study_plan_generator import StudyPlanGeneratorAgent


DATA_DIR = PROJECT_ROOT / "synthetic-data"


class ManagerInsightsAgent(BaseAgent):
    """Produces aggregate team certification insights without exposing individual scores."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config=config)
        self.learners = self._load_json(DATA_DIR / "learner_profiles.json")
        self.work_signals = self._load_json(DATA_DIR / "work_signals.json")
        self.planner = StudyPlanGeneratorAgent(config=config)

    def run(self, employee_ids: list[str] | None = None) -> dict[str, Any]:  # type: ignore[override]
        """Return a privacy-safe manager dashboard summary."""
        selected = self._selected_learners(employee_ids)
        plans = [self.planner.run(learner_id=learner["learner_id"]) for learner in selected]
        signals_by_employee = {signal["employee_id"]: signal for signal in self.work_signals}

        readiness_scores = [plan["readiness"]["score"] for plan in plans]
        certified_count = sum(1 for learner in selected if learner.get("exam_outcome") == "Pass")
        attempted_count = sum(1 for learner in selected if learner.get("exam_outcome") is not None)
        capacity_constrained = [
            learner["employee_id"]
            for learner in selected
            if signals_by_employee[learner["employee_id"]]["meeting_hours_per_week"] > 20
        ]

        return {
            "team_size": len(selected),
            "privacy": "Aggregate team metrics only; individual readiness scores are not shown.",
            "source_citations": [
                "[source: learner_profiles.json]",
                "[source: work_signals.json]",
                "[source: docs/fabric_iq_ontology.json]",
            ],
            "summary": {
                "average_readiness_score": round(mean(readiness_scores), 1) if readiness_scores else 0,
                "certifications_attempted": attempted_count,
                "certifications_passed": certified_count,
                "pass_rate": round((certified_count / attempted_count) * 100, 1) if attempted_count else 0,
                "capacity_constrained_count": len(capacity_constrained),
            },
            "certification_risk": self._certification_risk(plans),
            "capacity_risk": {
                "threshold": ">20 meeting hours/week",
                "count": len(capacity_constrained),
                "recommendation": self._capacity_recommendation(len(capacity_constrained), len(selected)),
            },
            "recommended_manager_actions": self._manager_actions(plans, len(capacity_constrained)),
        }

    @staticmethod
    def _load_json(path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def _selected_learners(self, employee_ids: list[str] | None) -> list[dict[str, Any]]:
        if not employee_ids:
            return self.learners
        wanted = set(employee_ids)
        selected = [
            learner
            for learner in self.learners
            if learner["employee_id"] in wanted or learner["learner_id"] in wanted
        ]
        if not selected:
            raise ValueError("No matching learners found for manager insights.")
        return selected

    @staticmethod
    def _certification_risk(plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
        scores_by_cert: dict[str, list[float]] = defaultdict(list)
        for plan in plans:
            scores_by_cert[plan["certification"]["id"]].append(plan["readiness"]["score"])

        risks = []
        for cert_id, scores in sorted(scores_by_cert.items()):
            average_score = round(mean(scores), 1)
            single_learner_group = len(scores) < 2
            risks.append(
                {
                    "certification_id": cert_id,
                    "learner_count": len(scores),
                    "average_readiness_score": None if single_learner_group else average_score,
                    "score_privacy_note": "Hidden for groups smaller than 2 learners." if single_learner_group else None,
                    "risk_level": "at_risk" if average_score < 70 else "watch" if average_score < 75 else "on_track",
                }
            )
        return risks

    @staticmethod
    def _capacity_recommendation(constrained_count: int, team_size: int) -> str:
        if constrained_count == 0:
            return "No workload intervention needed this week."
        ratio = constrained_count / max(team_size, 1)
        if ratio >= 0.3:
            return "Protect focus blocks before increasing certification targets."
        return "Monitor high-meeting learners and keep nudges lightweight."

    @staticmethod
    def _manager_actions(plans: list[dict[str, Any]], constrained_count: int) -> list[str]:
        actions = ["Review certification groups with average readiness below 70%."]
        if constrained_count:
            actions.append("Protect low-meeting study windows for capacity-constrained learners.")
        if any(plan["readiness"]["classification"] == "ready" for plan in plans):
            actions.append("Schedule final readiness reviews for on-track certification groups.")
        actions.append("Keep reporting aggregate-only to avoid exposing individual learner scores.")
        return actions


def summarize_team_readiness(team_id: str) -> dict[str, Any]:
    """Compatibility wrapper for earlier placeholder callers."""
    return {
        "team_id": team_id,
        "readiness_summary": ManagerInsightsAgent().run(),
    }


if __name__ == "__main__":
    print(json.dumps(ManagerInsightsAgent().run(), indent=2))
