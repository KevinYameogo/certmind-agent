# 🏗️ ARCHITECTURE.md — CertMind Agent System Design

> Full context for AI-assisted development

---

## System Overview

CertMind is a **multi-agent enterprise certification coaching system** built on Microsoft Foundry. It uses 7 specialised agents orchestrated by a top-level Planner–Executor to help employees achieve certifications while respecting their real work capacity.

The system implements three Microsoft IQ intelligence layers, a Critic/Verifier safety pattern, and a feedback loop that routes learners back through preparation if they fail assessments.

---

## Agent Roster

### 🧭 Orchestrator Agent (Top-level Planner–Executor)

**File**: `agents/orchestrator.py`
**Pattern**: Planner–Executor
**Responsibility**:

- Receives natural language input from the user
- Plans a multi-step workflow by decomposing the request
- Dispatches sub-tasks to specialist agents
- Passes every agent output through the Critic/Verifier before surfacing to user
- Manages the study→assess→loop feedback cycle
- Emits OpenTelemetry trace spans for every dispatch

**Key decisions it makes**:

- "Is this a learner request or a manager request?"
- "Which agents need to run, and in what order?"
- "Did the assessment pass? If not, re-route to Study Plan Generator."

**IQ layers used**: Routes to agents that use all three IQ layers

---

### 🎓 Learning Path Curator Agent

**File**: `agents/learning_path_curator.py`
**Pattern**: Retrieval-Augmented Generation (RAG) with mandatory citation
**Responsibility**:

- Maps a certification target + learner role to grounded learning resources
- Queries Foundry IQ knowledge base for relevant certification guides
- Calls Microsoft Learn MCP Server for live Microsoft Learn content
- Returns a cited, structured list of resources — rejects uncited answers

**Inputs**:

```python
{
  "learner_role": "Cloud Engineer",
  "certification_target": "AZ-204",
  "current_skills": ["Python", "REST APIs"]
}
```

**Outputs**:

```python
{
  "resources": [
    {
      "title": "Develop Azure compute solutions",
      "source": "cert_guide.md § Cloud Engineer",
      "url": "https://learn.microsoft.com/...",
      "estimated_hours": 4
    }
  ],
  "total_estimated_hours": 18,
  "citations": ["cert_guide.md", "Microsoft Learn: AZ-204"]
}
```

**IQ layer**: Foundry IQ (primary), Microsoft Learn MCP (secondary tool)

---

### 📅 Study Plan Generator Agent

**File**: `agents/study_plan_generator.py`
**Pattern**: Semantic reasoning over structured business data
**Responsibility**:

- Takes learner profile + certification target + work signals
- Uses Fabric IQ semantic model to understand role→certification→skill gap relationships
- Calculates realistic daily study allocation given meeting load
- Outputs a week-by-week study plan with milestones and checkpoints

**Inputs**:

```python
{
  "learner_id": "L-1001",
  "role": "Cloud Engineer",
  "certification": "AZ-204",
  "meeting_hours_per_week": 22,
  "focus_hours_per_week": 10,
  "target_exam_date": "2027-07-15"
}
```

**Outputs**:

```python
{
  "weeks": [
    {
      "week": 1,
      "focus": "Azure Functions + Storage",
      "daily_hours": 1.5,
      "milestone": "Complete Module 1 on Microsoft Learn"
    }
  ],
  "total_weeks": 5,
  "recommended_practice_score_before_exam": 75
}
```

**IQ layer**: Fabric IQ (semantic model of certification requirements and role mappings)

---

### 🔔 Engagement Agent

**File**: `agents/engagement_agent.py`
**Pattern**: Context-aware personalisation
**Responsibility**:

- Reads Work IQ signals: meeting load, focus hours, preferred learning slots
- Determines optimal study window recommendations (avoids peak meeting periods)
- Generates personalised, non-generic engagement nudges
- Adapts tone: lighter touch for high-workload employees, more active for low-workload

**Inputs**:

```python
{
  "employee_id": "EMP-001",
  "meeting_hours_per_week": 22,
  "focus_hours_per_week": 10,
  "preferred_learning_slot": "Morning",
  "current_study_streak_days": 3
}
```

**Outputs**:

```python
{
  "recommended_slots": ["Tuesday 8–9 AM", "Thursday 8–9 AM"],
  "engagement_message": "You have a light morning Thursday before your 10 AM standup — perfect for 45 mins on Azure Functions.",
  "workload_flag": "HIGH",
  "suggested_daily_minutes": 45
}
```

**IQ layer**: Work IQ (meeting patterns, focus windows, collaboration load)

---

### ✅ Critic / Verifier Agent ⭐ Differentiator

**File**: `agents/critic_verifier.py`
**Pattern**: Critic / Verifier (validation layer before output)
**Responsibility**:

- Reviews every agent output before it reaches the user or the next agent
- Checks: citations present, exam codes are real, answer addresses the question, no PII, no hallucinated content
- Returns structured verdict: approved or rejected with specific issues
- If rejected, Orchestrator re-runs the originating agent (max 2 retries)

**Inputs**:

```python
{
  "original_question": "What should I study for AZ-204?",
  "agent_name": "LearningPathCurator",
  "agent_output": "...",
}
```

**Outputs**:

```python
{
  "approved": False,
  "issues": [
    "Exam code 'AZ-999' does not exist",
    "Resource listed without citation"
  ],
  "revised_output": null  # null means re-run the agent
}
```

**IQ layer**: Foundry IQ (to verify citation sources exist in knowledge base)

---

### 📝 Assessment Agent

**File**: `agents/assessment_agent.py`
**Pattern**: RAG + Semantic Scoring + Loop trigger
**Responsibility**:

- Generates 5 grounded, cited quiz questions from Foundry IQ knowledge base
- Receives learner answers and scores them
- Produces a readiness score 0–100 using Fabric IQ pass thresholds
- If score ≥ 75: recommends sitting the exam → next certification
- If score < 75: triggers loop back to Study Plan Generator

**Inputs**:

```python
{
  "learner_id": "L-1001",
  "certification": "AZ-204",
  "study_history": {"hours_studied": 18, "practice_score_avg": 67}
}
```

**Outputs**:

```python
{
  "questions": [
    {
      "question": "Which Azure service is best suited for event-driven serverless compute?",
      "citation": "cert_guide.md § Azure Functions",
      "correct_answer": "Azure Functions"
    }
  ],
  "readiness_score": 71,
  "pass_threshold": 75,
  "recommendation": "LOOP_BACK",
  "weak_areas": ["Azure Functions", "Storage"]
}
```

**IQ layer**: Foundry IQ (question generation + citation), Fabric IQ (pass thresholds + scoring model)

---

### 📊 Manager Insights Agent

**File**: `agents/manager_insights.py`
**Pattern**: Aggregate analytics + Privacy-preserving summary
**Responsibility**:

- Takes a team roster (list of employee IDs)
- Aggregates from Fabric IQ: team pass rates, average readiness, risk areas
- Uses Work IQ: identifies capacity-constrained team members (without naming them)
- Returns team-level dashboard — NEVER individual scores
- Highlights certifications at risk and recommended interventions

**Inputs**:

```python
{
  "manager_id": "MGR-001",
  "team_ids": ["EMP-001", "EMP-002", "EMP-003"],
  "focus_certification": "AZ-204"
}
```

**Outputs**:

```python
{
  "team_size": 3,
  "avg_readiness_score": 71,
  "certifications_at_risk": ["AZ-204"],
  "at_risk_reason": "2 of 3 team members below 75% readiness threshold",
  "capacity_note": "1 team member has >20 meeting hours/week — reduced study capacity likely",
  "recommendation": "Schedule a team study session for Azure Functions this week"
}
```

**IQ layer**: Fabric IQ (semantic aggregation), Work IQ (team capacity signals)

---

## System Flow Diagram

![](/docs/assets/architecture.png.png)

```
User Request (Natural Language)
         │
         ▼
  ┌─────────────────┐
  │   ORCHESTRATOR  │  ← Planner-Executor
  │   (Top-level)   │
  └────────┬────────┘
           │ Plans & Decomposes
           ▼
  ┌────────────────────────────────────────────────┐
  │              AGENT DISPATCH LAYER               │
  ├──────────────┬──────────────┬──────────────────┤
  │   CURATOR    │   PLANNER    │   ENGAGEMENT     │
  │ (Foundry IQ) │ (Fabric IQ)  │   (Work IQ)      │
  └──────┬───────┴──────┬───────┴──────┬───────────┘
         │              │              │
         └──────────────┴──────────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ CRITIC/VERIFIER │  ← Every output passes through here
               └────────┬────────┘
                        │
               Approved?│
              ┌─────────┴──────────┐
             YES                   NO
              │                    │
              ▼                    ▼
       ┌─────────────┐      Re-run originating
       │  ASSESSMENT │      agent (max 2x)
       │    AGENT    │
       └──────┬──────┘
              │
     Score ≥ 75?
    ┌──────────┴───────────┐
   YES                     NO
    │                      │
    ▼                      ▼
"Exam Ready!"         Loop back to
Next Cert →           Study Planner

(Manager path bypasses learner loop → goes direct to Manager Insights Agent)
```

---

## Microsoft IQ Layer Map

```
FOUNDRY IQ
├── Learning Path Curator → citations from knowledge base docs
├── Assessment Agent → grounded quiz questions
└── Critic/Verifier → validates citations exist in KB

WORK IQ
├── Engagement Agent → meeting load, focus windows, preferred slots
└── Manager Insights Agent → team capacity signals

FABRIC IQ
├── Study Plan Generator → role→cert→skill gap semantic model
├── Assessment Agent → pass thresholds and scoring model
└── Manager Insights Agent → team readiness aggregation
```

---

## Data Flow (Synthetic Only)

```
synthetic-data/
├── learner_profiles.json     → Study Plan Generator, Assessment Agent
├── work_signals.json         → Engagement Agent, Manager Insights
├── certification_catalog.json → Fabric IQ seed data, Study Plan Generator
├── cert_guide.md             → Foundry IQ knowledge base document 1
├── team_learning_report.md   → Foundry IQ knowledge base document 2
└── workload_insights.md      → Foundry IQ knowledge base document 3
```

---

## Reasoning Patterns Used

| Pattern                         | Where                                                 |
| ------------------------------- | ----------------------------------------------------- |
| **Planner–Executor**            | Orchestrator decomposes requests and dispatches       |
| **Critic/Verifier**             | All outputs gated before reaching user                |
| **Self-reflection + Iteration** | Orchestrator re-runs failed agents (max 2x)           |
| **Role-based Specialisation**   | 7 agents with clear, non-overlapping responsibilities |
| **Feedback Loop**               | Assessment failure triggers return to Study Plan      |

---

## Responsible AI Controls

- All outputs pass through Critic/Verifier before user sees them
- Manager Insights never exposes individual scores — team aggregates only
- Input guardrail: reject requests containing PII patterns (email, phone, SSN)
- Output guardrail: flag any response containing real company names or real people
- Synthetic data only — documented clearly in README and all data files
- No secrets in source code — managed identity + env vars only

---

## Tech Stack Reference

| Component      | Technology                                    |
| -------------- | --------------------------------------------- |
| Model          | GPT-5-mini via Microsoft Foundry              |
| Agent SDK      | azure-ai-projects + Microsoft Agent Framework |
| Grounding      | Foundry IQ (Azure AI Search backend)          |
| Semantic layer | Fabric IQ                                     |
| Work context   | Work IQ (M365 signals)                        |
| External tools | Microsoft Learn MCP Server                    |
| Observability  | OpenTelemetry + Azure Monitor                 |
| Deployment     | Hosted Agents on Foundry Agent Service        |
| Container      | Docker → Azure Container Registry             |
| Dev tools      | GitHub Copilot, VS Code                       |
| Language       | Python 3.11                                   |

---

## Environment Variables Reference

| Variable                                | Used By                            |
| --------------------------------------- | ---------------------------------- |
| `AZURE_AI_PROJECT_ENDPOINT`             | All agents (Foundry connection)    |
| `AZURE_AI_MODEL_DEPLOYMENT`             | All agents (= `GPT-5-mini`)        |
| `FOUNDRY_IQ_KNOWLEDGE_BASE_ID`          | Curator, Assessment, Critic agents |
| `MICROSOFT_LEARN_MCP_URL`               | Learning Path Curator              |
| `AZURE_SUBSCRIPTION_ID`                 | Fabric IQ connection               |
| `AZURE_RESOURCE_GROUP`                  | Fabric IQ connection               |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Telemetry/OpenTelemetry            |
