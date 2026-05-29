"""Top-level Planner-Executor orchestrator for CertMind workflows."""

from __future__ import annotations

import json
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from opentelemetry import trace


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.assessment_agent import AssessmentAgent
from agents.base_agent import AgentConfig, BaseAgent
from agents.critic_verifier import CriticVerifierAgent
from agents.engagement_agent import EngagementAgent
from agents.learning_path_curator import LearningPathCuratorAgent
from agents.manager_insights import ManagerInsightsAgent
from agents.study_plan_generator import StudyPlanGeneratorAgent


DATA_DIR = PROJECT_ROOT / "synthetic-data"


class OrchestratorAgent(BaseAgent):
    """Plans and executes multi-agent CertMind workflows."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config=config)
        self.trace_id = uuid.uuid4().hex[:12]
        self.trace: list[dict[str, Any]] = []
        self.tracer = trace.get_tracer("certmind.orchestrator")
        self.learners = self._load_json(DATA_DIR / "learner_profiles.json")
        self.curator = LearningPathCuratorAgent(config=config)
        self.planner = StudyPlanGeneratorAgent(config=config)
        self.engagement = EngagementAgent(config=config)
        self.assessment = AssessmentAgent(config=config)
        self.manager = ManagerInsightsAgent(config=config)
        self.critic = CriticVerifierAgent(config=config)

    def run(self, request: str) -> dict[str, Any]:  # type: ignore[override]
        """Run a natural-language request through the planner-executor workflow."""
        plan = self._plan(request)
        if plan["intent"] == "manager_insights":
            return self._run_manager_workflow(request, plan)
        return self._run_learner_workflow(request, plan)

    @staticmethod
    def _load_json(path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def _plan(self, request: str) -> dict[str, Any]:
        lowered = request.lower()
        if any(term in lowered for term in ["manager", "team", "dashboard", "readiness summary"]):
            return {
                "intent": "manager_insights",
                "steps": ["manager_insights", "critic"],
            }

        cert = self._extract_certification(request) or "AZ-204"
        role = self._extract_role(request) or "Cloud Engineer"
        learner = self._match_learner(role=role, certification=cert)
        return {
            "intent": "learner_certification_coaching",
            "role": role,
            "certification": cert,
            "learner_id": learner["learner_id"],
            "employee_id": learner["employee_id"],
            "steps": ["curator", "study_plan", "engagement", "assessment", "critic"],
        }

    @staticmethod
    def _extract_certification(request: str) -> str | None:
        match = re.search(r"\b[A-Z]{2}-\d{3}\b", request.upper())
        return match.group(0) if match else None

    @staticmethod
    def _extract_role(request: str) -> str | None:
        roles = ["Cloud Engineer", "DevOps Engineer", "Data Engineer", "Security Engineer"]
        lowered = request.lower()
        for role in roles:
            if role.lower() in lowered:
                return role
        return None

    def _match_learner(self, role: str, certification: str) -> dict[str, Any]:
        for learner in self.learners:
            if learner["role"] == role and learner["certification_target"] == certification:
                return learner
        for learner in self.learners:
            if learner["certification_target"] == certification:
                return learner
        raise ValueError(f"No learner profile matches role={role!r}, certification={certification!r}")

    def _run_learner_workflow(self, request: str, plan: dict[str, Any]) -> dict[str, Any]:
        role = plan["role"]
        cert = plan["certification"]
        learner_id = plan["learner_id"]
        employee_id = plan["employee_id"]

        learning_path = self._span(
            "learning_path_curator",
            lambda: self.curator.run(role=role, target=cert),
        )
        study_plan = self._span(
            "study_plan_generator",
            lambda: self.planner.run(learner_id=learner_id, certification=cert),
        )
        engagement = self._span(
            "engagement_agent",
            lambda: self.engagement.run(employee_id=employee_id),
        )
        assessment = self._span(
            "assessment_agent",
            lambda: self.assessment.run(learner_id=learner_id, certification=cert),
        )

        combined = {
            "request": request,
            "plan": plan,
            "learning_path": learning_path,
            "study_plan": study_plan,
            "engagement": engagement,
            "assessment": assessment,
            "feedback_loop": self._feedback_loop(assessment),
        }
        verdict = self._span(
            "critic_verifier",
            lambda: self.critic.review(original_question=request, agent_output=combined),
        )
        return {
            "trace_id": self.trace_id,
            "critic_approved": verdict["approved"],
            "critic_issues": verdict["issues"],
            "result": combined if verdict["approved"] else verdict["revised_output"],
            "trace": self.trace,
        }

    def _run_manager_workflow(self, request: str, plan: dict[str, Any]) -> dict[str, Any]:
        insights = self._span("manager_insights", lambda: self.manager.run())
        verdict = self._span(
            "critic_verifier",
            lambda: self.critic.review(original_question=request, agent_output=insights),
        )
        return {
            "trace_id": self.trace_id,
            "critic_approved": verdict["approved"],
            "critic_issues": verdict["issues"],
            "result": insights if verdict["approved"] else verdict["revised_output"],
            "trace": self.trace,
            "plan": plan,
        }

    @staticmethod
    def _feedback_loop(assessment: dict[str, Any]) -> dict[str, Any]:
        next_step = assessment.get("next_step", {})
        return {
            "triggered": next_step.get("action") == "loop_back_to_study_plan",
            "action": next_step.get("action"),
            "message": next_step.get("message"),
        }

    def _span(self, name: str, callback):
        start = time.perf_counter()
        with self.tracer.start_as_current_span(name) as span:
            span.set_attribute("certmind.trace_id", self.trace_id)
            span.set_attribute("certmind.agent", name)
            try:
                output = callback()
                status = "ok"
                span.set_attribute("certmind.status", status)
                span.set_attribute("certmind.output_summary", self._summarize_output(output))
                return output
            except Exception as exc:
                status = "error"
                output = {"error": str(exc)}
                span.set_attribute("certmind.status", status)
                span.record_exception(exc)
                raise
            finally:
                elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
                self.trace.append(
                    {
                        "trace_id": self.trace_id,
                        "span": name,
                        "status": status,
                        "latency_ms": elapsed_ms,
                        "output_summary": self._summarize_output(output),
                    }
                )

    @staticmethod
    def _summarize_output(output: Any) -> str:
        if isinstance(output, str):
            return output.splitlines()[0][:120] if output else ""
        if isinstance(output, dict):
            return ", ".join(list(output.keys())[:6])
        return type(output).__name__


def main() -> None:
    """Run a local orchestration sample."""
    orchestrator = OrchestratorAgent()
    result = orchestrator.run("I'm a Cloud Engineer and I want to get AZ-204 certified")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
