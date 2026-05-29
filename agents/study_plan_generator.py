"""Study Plan Generator agent."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.base_agent import AgentConfig, BaseAgent


DATA_DIR = PROJECT_ROOT / "synthetic-data"
ONTOLOGY_PATH = PROJECT_ROOT / "docs" / "fabric_iq_ontology.json"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


class StudyPlanGeneratorAgent(BaseAgent):
    """Generates capacity-aware certification study plans from semantic data."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config=config)
        self.learners = self._load_json(DATA_DIR / "learner_profiles.json")
        self.work_signals = self._load_json(DATA_DIR / "work_signals.json")
        self.catalog = self._load_json(DATA_DIR / "certification_catalog.json")
        self.ontology = self._load_json(ONTOLOGY_PATH)

    def run(self, learner_id: str, certification: str | None = None) -> dict[str, Any]:  # type: ignore[override]
        """Return a structured weekly study plan for a learner and certification."""
        learner = self._find_learner(learner_id)
        target = certification or learner["certification_target"]
        cert = self._find_certification(target)
        signal = self._find_work_signal(learner["employee_id"])

        skill_gap = self._calculate_skill_gap(learner, cert)
        readiness = self._calculate_readiness(learner, cert, skill_gap)
        capacity = self._calculate_capacity(signal)
        remaining_hours = self._calculate_remaining_hours(learner, cert, readiness)
        weekly_plan = self._build_weekly_plan(
            cert=cert,
            skill_gap=skill_gap,
            signal=signal,
            remaining_hours=remaining_hours,
            weekly_capacity_hours=capacity["weekly_capacity_hours"],
        )

        return {
            "learner_id": learner["learner_id"],
            "employee_id": learner["employee_id"],
            "role": learner["role"],
            "certification": {
                "id": cert["id"],
                "name": cert["name"],
                "recommended_hours": cert["recommended_hours"],
                "pass_threshold_score": cert["pass_threshold_score"],
            },
            "fabric_iq_semantic_model": {
                "ontology": str(ONTOLOGY_PATH.relative_to(PROJECT_ROOT)),
                "entities_used": ["Employee", "Certification", "Role", "SkillGap", "ReadinessScore"],
            },
            "skill_gap": skill_gap,
            "readiness": readiness,
            "capacity": capacity,
            "remaining_hours": remaining_hours,
            "weekly_plan": weekly_plan,
            "manager_note": self._manager_note(readiness, signal),
        }

    @staticmethod
    def _load_json(path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def _find_learner(self, learner_id: str) -> dict[str, Any]:
        for learner in self.learners:
            if learner["learner_id"] == learner_id or learner["employee_id"] == learner_id:
                return learner
        raise ValueError(f"Unknown learner: {learner_id}")

    def _find_certification(self, certification_id: str) -> dict[str, Any]:
        for cert in self.catalog["certifications"]:
            if cert["id"].lower() == certification_id.lower():
                return cert
        raise ValueError(f"Unknown certification: {certification_id}")

    def _find_work_signal(self, employee_id: str) -> dict[str, Any]:
        for signal in self.work_signals:
            if signal["employee_id"] == employee_id:
                return signal
        raise ValueError(f"Missing work signals for employee: {employee_id}")

    def _calculate_skill_gap(self, learner: dict[str, Any], cert: dict[str, Any]) -> dict[str, Any]:
        current_skills = learner.get("current_skills", [])
        covered = []
        missing = []

        for required_skill in cert["skills"]:
            if self._skill_is_covered(required_skill, current_skills):
                covered.append(required_skill)
            else:
                missing.append(required_skill)

        total = len(cert["skills"]) or 1
        return {
            "covered_skills": covered,
            "missing_skills": missing,
            "gap_count": len(missing),
            "gap_ratio": round(len(missing) / total, 2),
        }

    @staticmethod
    def _skill_is_covered(required_skill: str, current_skills: list[str]) -> bool:
        required_tokens = set(re.findall(r"[a-z0-9]+", required_skill.lower()))
        for current_skill in current_skills:
            current_tokens = set(re.findall(r"[a-z0-9]+", current_skill.lower()))
            if required_tokens & current_tokens:
                return True
        return False

    def _calculate_readiness(
        self,
        learner: dict[str, Any],
        cert: dict[str, Any],
        skill_gap: dict[str, Any],
    ) -> dict[str, Any]:
        practice_component = learner["practice_score_avg"] * 0.7
        completion_ratio = min(learner["hours_studied"] / cert["recommended_hours"], 1)
        study_component = completion_ratio * 100 * 0.3
        skill_gap_penalty = skill_gap["gap_ratio"] * 10
        score = max(0, min(100, practice_component + study_component - skill_gap_penalty))

        if score >= cert["pass_threshold_score"]:
            classification = "ready"
        elif score >= 65:
            classification = "near_ready"
        else:
            classification = "at_risk"

        return {
            "score": round(score, 1),
            "classification": classification,
            "practice_component": round(practice_component, 1),
            "study_completion_component": round(study_component, 1),
            "skill_gap_penalty": round(skill_gap_penalty, 1),
            "target_score": cert["pass_threshold_score"],
        }

    @staticmethod
    def _calculate_capacity(signal: dict[str, Any]) -> dict[str, Any]:
        meeting_hours = signal["meeting_hours_per_week"]
        focus_hours = signal["focus_hours_per_week"]

        if meeting_hours > 22:
            daily_minutes = 30
            workload_level = "very_high"
        elif meeting_hours > 18:
            daily_minutes = 45
            workload_level = "high"
        elif meeting_hours >= 12:
            daily_minutes = 75
            workload_level = "medium"
        else:
            daily_minutes = 90
            workload_level = "low"

        study_days = signal.get("low_meeting_days") or [day for day in WEEKDAYS if day not in signal["peak_meeting_days"]]
        daily_capacity_hours = daily_minutes / 60
        weekly_capacity_hours = min(focus_hours * 0.4, daily_capacity_hours * len(study_days))

        return {
            "workload_level": workload_level,
            "meeting_hours_per_week": meeting_hours,
            "focus_hours_per_week": focus_hours,
            "preferred_learning_slot": signal["preferred_learning_slot"],
            "recommended_daily_minutes": daily_minutes,
            "study_days": study_days,
            "weekly_capacity_hours": round(weekly_capacity_hours, 1),
        }

    @staticmethod
    def _calculate_remaining_hours(
        learner: dict[str, Any],
        cert: dict[str, Any],
        readiness: dict[str, Any],
    ) -> float:
        base_remaining = max(cert["recommended_hours"] - learner["hours_studied"], 0)
        remediation_hours = cert["recommended_hours"] * 0.25 if readiness["classification"] != "ready" else 0
        return round(max(base_remaining, remediation_hours), 1)

    def _build_weekly_plan(
        self,
        cert: dict[str, Any],
        skill_gap: dict[str, Any],
        signal: dict[str, Any],
        remaining_hours: float,
        weekly_capacity_hours: float,
    ) -> list[dict[str, Any]]:
        if remaining_hours <= 0:
            remaining_hours = min(weekly_capacity_hours, 2)

        weeks_needed = max(1, math.ceil(remaining_hours / max(weekly_capacity_hours, 1)))
        focus_topics = skill_gap["missing_skills"] or cert["skills"]
        plan = []

        for week_number in range(1, weeks_needed + 1):
            hours = min(weekly_capacity_hours, remaining_hours - (week_number - 1) * weekly_capacity_hours)
            if hours <= 0:
                hours = weekly_capacity_hours

            topic = focus_topics[(week_number - 1) % len(focus_topics)]
            plan.append(
                {
                    "week": week_number,
                    "target_hours": round(hours, 1),
                    "primary_focus": topic,
                    "study_windows": [
                        f"{day} {signal['preferred_learning_slot'].lower()}"
                        for day in signal.get("low_meeting_days", [])[:3]
                    ],
                    "milestone": self._milestone_for_week(week_number, weeks_needed, topic),
                }
            )

        return plan

    @staticmethod
    def _milestone_for_week(week_number: int, weeks_needed: int, topic: str) -> str:
        if week_number == weeks_needed:
            return "Complete a timed practice assessment and review weak areas."
        if week_number == 1:
            return f"Build fundamentals and complete hands-on labs for {topic}."
        return f"Deepen implementation practice for {topic} and update notes."

    @staticmethod
    def _manager_note(readiness: dict[str, Any], signal: dict[str, Any]) -> str:
        if readiness["classification"] == "ready":
            return "Learner is close to exam-ready; protect planned study time and schedule final assessment."
        if signal["meeting_hours_per_week"] > 20:
            return "Learner needs workload protection before increasing certification pace."
        return "Learner should continue structured weekly milestones and recheck readiness after the plan."


def generate_study_plan(learner_id: str, weekly_hours: int | None = None) -> dict[str, Any]:
    """Compatibility wrapper for earlier placeholder callers."""
    planner = StudyPlanGeneratorAgent()
    plan = planner.run(learner_id=learner_id)
    if weekly_hours is not None:
        plan["capacity"]["weekly_capacity_hours"] = weekly_hours
    return plan


if __name__ == "__main__":
    planner = StudyPlanGeneratorAgent()
    print(json.dumps(planner.run(learner_id="L-1001", certification="AZ-204"), indent=2))
