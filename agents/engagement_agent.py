"""Engagement Agent for Work IQ-aware study nudges."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.base_agent import AgentConfig, BaseAgent


DATA_DIR = PROJECT_ROOT / "synthetic-data"


class EngagementAgent(BaseAgent):
    """Creates personalised, non-intrusive study engagement recommendations."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config=config)
        self.learners = self._load_json(DATA_DIR / "learner_profiles.json")
        self.work_signals = self._load_json(DATA_DIR / "work_signals.json")

    def run(self, employee_id: str) -> dict[str, Any]:  # type: ignore[override]
        """Return Work IQ-aware engagement recommendations for an employee."""
        return self.trace_call(
            "engagement_agent",
            f"employee_id={employee_id}",
            lambda: self._run(employee_id=employee_id),
        )

    def _run(self, employee_id: str) -> dict[str, Any]:
        learner = self._find_learner(employee_id)
        signal = self._find_work_signal(employee_id)
        workload = self._classify_workload(signal)
        study_windows = self._study_windows(signal, workload)

        return {
            "employee_id": employee_id,
            "learner_id": learner["learner_id"],
            "role": learner["role"],
            "certification_target": learner["certification_target"],
            "work_iq_summary": {
                "workload_level": workload["level"],
                "meeting_hours_per_week": signal["meeting_hours_per_week"],
                "focus_hours_per_week": signal["focus_hours_per_week"],
                "collaboration_intensity": signal["collaboration_intensity"],
                "study_streak_days": signal["study_streak_days"],
            },
            "recommended_frequency": workload["frequency"],
            "engagement_tone": workload["tone"],
            "suggested_study_slots": study_windows,
            "personalised_nudges": self._nudges(learner, signal, workload, study_windows),
            "avoid_windows": self._avoid_windows(signal),
            "manager_visibility": self._manager_visibility(signal, workload),
        }

    @staticmethod
    def _load_json(path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def _find_learner(self, employee_id: str) -> dict[str, Any]:
        for learner in self.learners:
            if learner["employee_id"] == employee_id or learner["learner_id"] == employee_id:
                return learner
        raise ValueError(f"Unknown employee or learner: {employee_id}")

    def _find_work_signal(self, employee_id: str) -> dict[str, Any]:
        for signal in self.work_signals:
            if signal["employee_id"] == employee_id:
                return signal
        raise ValueError(f"Missing work signals for employee: {employee_id}")

    @staticmethod
    def _classify_workload(signal: dict[str, Any]) -> dict[str, str]:
        meeting_hours = signal["meeting_hours_per_week"]
        focus_hours = signal["focus_hours_per_week"]
        intensity = signal["collaboration_intensity"]

        if meeting_hours > 24 or focus_hours < 8 or intensity == "VERY_HIGH":
            return {
                "level": "very_high",
                "frequency": "one check-in per week",
                "tone": "protective and low-pressure",
                "minutes": "30",
            }
        if meeting_hours > 18 or intensity == "HIGH":
            return {
                "level": "high",
                "frequency": "two nudges per week",
                "tone": "brief, specific, and workload-aware",
                "minutes": "45",
            }
        if meeting_hours >= 12:
            return {
                "level": "medium",
                "frequency": "three nudges per week",
                "tone": "encouraging and milestone-focused",
                "minutes": "60-75",
            }
        return {
            "level": "low",
            "frequency": "three to four nudges per week",
            "tone": "goal-oriented and momentum-building",
            "minutes": "90",
        }

    @staticmethod
    def _study_windows(signal: dict[str, Any], workload: dict[str, str]) -> list[dict[str, str]]:
        low_meeting_days = signal.get("low_meeting_days") or []
        preferred_slot = signal["preferred_learning_slot"].lower()
        minutes = workload["minutes"]

        windows = []
        for day in low_meeting_days[:3]:
            windows.append(
                {
                    "day": day,
                    "slot": preferred_slot,
                    "duration_minutes": minutes,
                    "reason": f"{day} is a lower-meeting day and matches the learner's {preferred_slot} preference.",
                }
            )
        return windows

    @staticmethod
    def _avoid_windows(signal: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {
                "day": day,
                "reason": "Peak meeting day; avoid certification nudges unless the learner asks for a check-in.",
            }
            for day in signal.get("peak_meeting_days", [])
        ]

    @staticmethod
    def _nudges(
        learner: dict[str, Any],
        signal: dict[str, Any],
        workload: dict[str, str],
        windows: list[dict[str, str]],
    ) -> list[str]:
        cert = learner["certification_target"]
        streak = signal["study_streak_days"]
        first_window = windows[0] if windows else {"day": "the next low-meeting day", "slot": "preferred slot"}
        second_window = windows[1] if len(windows) > 1 else first_window

        if workload["level"] in {"high", "very_high"}:
            return [
                (
                    f"You have a lighter {first_window['day']} {first_window['slot']} window; "
                    f"use it for one focused {cert} topic instead of adding time to a packed day."
                ),
                (
                    f"Protect {workload['minutes']} minutes on {second_window['day']} for review. "
                    f"Skip nudges on peak meeting days so the plan stays sustainable."
                ),
            ]

        return [
            (
                f"Your {first_window['day']} {first_window['slot']} block is a good time to move "
                f"one {cert} milestone forward."
            ),
            (
                f"You have a {streak}-day study streak; keep the next session short and specific "
                "so the habit stays easy to continue."
            ),
        ]

    @staticmethod
    def _manager_visibility(signal: dict[str, Any], workload: dict[str, str]) -> str:
        if workload["level"] == "very_high":
            return "Recommend manager review before adding certification pressure."
        if signal["meeting_hours_per_week"] > 20:
            return "Manager should protect low-meeting study windows this week."
        return "No manager intervention needed; continue normal progress visibility."


def recommend_engagement_window(learner_id: str) -> dict[str, Any]:
    """Compatibility wrapper for earlier placeholder callers."""
    return EngagementAgent().run(employee_id=learner_id)


if __name__ == "__main__":
    engagement = EngagementAgent()
    print(json.dumps(engagement.run(employee_id="EMP-001"), indent=2))
