"""Assessment Agent for cited quiz generation and readiness scoring."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.base_agent import AgentConfig, BaseAgent
from agents.critic_verifier import CriticVerifierAgent
from agents.study_plan_generator import StudyPlanGeneratorAgent


DATA_DIR = PROJECT_ROOT / "synthetic-data"


class AssessmentAgent(BaseAgent):
    """Generates cited assessments and evaluates learner readiness."""

    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config=config)
        self.learners = self._load_json(DATA_DIR / "learner_profiles.json")
        self.catalog = self._load_json(DATA_DIR / "certification_catalog.json")
        self.critic = CriticVerifierAgent(config=config)
        self.planner = StudyPlanGeneratorAgent(config=config)

    def run(
        self,
        learner_id: str,
        certification: str | None = None,
        answers: dict[str, str] | None = None,
    ) -> dict[str, Any]:  # type: ignore[override]
        """Generate a cited quiz and evaluate readiness for the learner."""
        return self.trace_call(
            "assessment_agent",
            f"learner_id={learner_id}; certification={certification or 'profile-target'}; answers={bool(answers)}",
            lambda: self._run(learner_id=learner_id, certification=certification, answers=answers),
        )

    def _run(
        self,
        learner_id: str,
        certification: str | None = None,
        answers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        learner = self._find_learner(learner_id)
        cert = self._find_certification(certification or learner["certification_target"])
        questions = self._generate_questions(cert)
        evaluation = self._evaluate(learner, cert, questions, answers or {})

        output = {
            "learner_id": learner["learner_id"],
            "employee_id": learner["employee_id"],
            "certification_id": cert["id"],
            "certification_name": cert["name"],
            "questions": questions,
            "evaluation": evaluation,
            "next_step": self._next_step(learner, cert, evaluation),
        }
        verdict = self.critic.review(
            original_question=f"Generate cited assessment for {cert['id']}",
            agent_output=output,
        )
        output["critic_verdict"] = {
            "approved": verdict["approved"],
            "issues": verdict["issues"],
        }
        if not verdict["approved"]:
            return verdict["revised_output"]
        return output

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

    @staticmethod
    def _generate_questions(cert: dict[str, Any]) -> list[dict[str, Any]]:
        questions = []
        skills = cert["skills"]
        for index, skill in enumerate(skills[:5], start=1):
            questions.append(
                {
                    "id": f"Q{index}",
                    "skill": skill,
                    "question": f"For {cert['id']}, what should a learner understand about {skill}?",
                    "expected_answer": f"Explain the key purpose, implementation concern, and Azure use case for {skill}.",
                    "citation": "[source: cert_guide.md]",
                }
            )

        while len(questions) < 5:
            index = len(questions) + 1
            questions.append(
                {
                    "id": f"Q{index}",
                    "skill": cert["id"],
                    "question": f"What readiness score should a learner target before booking {cert['id']}?",
                    "expected_answer": "A learner should target a practice score of 75% or above before booking.",
                    "citation": "[source: cert_guide.md]",
                }
            )
        return questions

    def _evaluate(
        self,
        learner: dict[str, Any],
        cert: dict[str, Any],
        questions: list[dict[str, Any]],
        answers: dict[str, str],
    ) -> dict[str, Any]:
        if answers:
            correct = sum(
                1
                for question in questions
                if self._answer_mentions_skill(answers.get(question["id"], ""), question["skill"])
            )
            quiz_score = round((correct / len(questions)) * 100, 1)
        else:
            correct = None
            quiz_score = learner["practice_score_avg"]

        study_completion = min(learner["hours_studied"] / cert["recommended_hours"], 1)
        readiness_score = min(100, quiz_score * 0.75 + study_completion * 100 * 0.25)
        readiness_score = round(readiness_score, 1)
        passed = readiness_score >= cert["pass_threshold_score"]

        return {
            "submitted_answers": bool(answers),
            "correct_answers": correct,
            "quiz_score": quiz_score,
            "study_completion_ratio": round(study_completion, 2),
            "readiness_score": readiness_score,
            "pass_threshold_score": cert["pass_threshold_score"],
            "passed": passed,
            "classification": "ready" if passed else self._classification(readiness_score),
        }

    @staticmethod
    def _answer_mentions_skill(answer: str, skill: str) -> bool:
        answer_tokens = {token.lower() for token in answer.replace("-", " ").split()}
        skill_tokens = {token.lower() for token in skill.replace("-", " ").split()}
        return bool(answer_tokens & skill_tokens)

    @staticmethod
    def _classification(score: float) -> str:
        if score >= 65:
            return "near_ready"
        return "needs_review"

    def _next_step(
        self,
        learner: dict[str, Any],
        cert: dict[str, Any],
        evaluation: dict[str, Any],
    ) -> dict[str, Any]:
        if evaluation["passed"]:
            return {
                "action": "schedule_exam_readiness_review",
                "message": f"{cert['id']} readiness is at or above threshold; schedule final review.",
            }

        study_plan = self.planner.run(learner_id=learner["learner_id"], certification=cert["id"])
        weeks = len(study_plan["weekly_plan"])
        hours = math.ceil(study_plan["remaining_hours"])
        return {
            "action": "loop_back_to_study_plan",
            "message": (
                f"{cert['id']} readiness is below {cert['pass_threshold_score']}%; "
                f"continue the structured plan for about {weeks} week(s) and {hours} hour(s)."
            ),
            "study_plan_summary": {
                "remaining_hours": study_plan["remaining_hours"],
                "weekly_plan": study_plan["weekly_plan"],
            },
        }


def generate_assessment(certification_id: str) -> dict[str, Any]:
    """Compatibility wrapper for earlier placeholder callers."""
    return AssessmentAgent().run(learner_id="L-1001", certification=certification_id)


if __name__ == "__main__":
    assessment = AssessmentAgent()
    print(json.dumps(assessment.run(learner_id="L-1001", certification="AZ-204"), indent=2))
