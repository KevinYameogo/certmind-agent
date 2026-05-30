# ✅ IMPLEMENTATION.md — Build Checklist for AI-Assisted Development

This is your step-by-step coding guide. Each task can be vibe-coded with GitHub Copilot or Claude.
Work through these in order — each builds on the previous.

> Reference `ARCHITECTURE.md` while building to stay aligned with the full system design.
> Reference `MANUAL_STEPS.md` for any Azure portal steps that block you.

---

## SPRINT 1 — Project Skeleton (June 4–5)

### [x] 1.1 Initialise Python project

```bash
mkdir certmind-agent && cd certmind-agent
git init
python -m venv .venv && source .venv/bin/activate
```

### [x] 1.2 Create requirements.txt with these dependencies

```
azure-ai-projects>=1.0.0
azure-identity>=1.15.0
azure-ai-inference>=1.0.0b9
azure-search-documents>=11.6.0
openai>=1.0.0
python-dotenv>=1.0.0
opentelemetry-sdk>=1.20.0
azure-monitor-opentelemetry>=1.0.0
requests>=2.31.0
rich>=13.0.0   # Pretty terminal output for demo
```

### [x] 1.3 Create .env.example (never commit the real .env!)

```
AZURE_AI_PROJECT_ENDPOINT=your-project-endpoint-here
AZURE_AI_MODEL_DEPLOYMENT=gpt-5-mini
FOUNDRY_IQ_KNOWLEDGE_BASE_ID=your-kb-id-here
MICROSOFT_LEARN_MCP_URL=your-mcp-url-here
AZURE_SUBSCRIPTION_ID=your-sub-id
AZURE_RESOURCE_GROUP=certmind-rg
```

### [x] 1.4 Create .gitignore

```
.venv/
.env
__pycache__/
*.pyc
.DS_Store
```

### [x] 1.5 Upload synthetic data files to repo

- Copy all files from `synthetic-data/` folder (already written — see that folder)
- Commit them: `git add synthetic-data/ && git commit -m "feat: add synthetic data"`

### [x] 1.6 Push skeleton to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/certmind-agent
git push -u origin main
```

✅ **Sprint 1 done when**: Repo is live on GitHub with skeleton structure

---

## SPRINT 2 — Foundry IQ Knowledge Base + Base Agent (June 5–6)

### [x] 2.1 Write setup_foundry_iq.py

- Connects to Azure using `DefaultAzureCredential`
- Verifies the 3 markdown knowledge docs intended for your Foundry IQ knowledge base
- Optionally verifies the uploaded blobs in `certmind-docs` when `AZURE_STORAGE_ACCOUNT_URL` is configured
- Prints confirmation with the configured knowledge base ID
- 💡 Prompt for Copilot: _"Write a Python script that verifies the three markdown knowledge docs for Foundry IQ ingestion and optionally checks they exist in an Azure Blob container using DefaultAzureCredential."_

### [x] 2.2 Run setup script and verify in Foundry portal

- Run: `python scripts/setup_foundry_iq.py`
- Check Foundry portal → Knowledge bases → all 3 markdown docs indexed
- ✅ Gate: Do not proceed until docs are indexed

### [x] 2.3 Write base_agent.py (shared base class)

All agents inherit from this. It should:

- Connect to Foundry using the project endpoint
- Initialise GPT-5-mini as the model client
- Provide a `run(prompt: str) -> str` method
- Include basic error handling and logging
- 💡 Prompt: _"Write a Python base class for a Microsoft Foundry agent using azure-ai-projects and the GPT-5-mini deployment"_

### [x] 2.4 Write learning_path_curator.py

- Inherits from BaseAgent
- Takes: `learner_role: str`, `certification_target: str`
- Queries Foundry IQ knowledge base for relevant study resources
- Returns: cited list of learning resources with source references
- **Must cite sources** — if no citation, reject the answer
- Integrate Microsoft Learn MCP server as a tool
- 💡 Prompt: _"Write a LearningPathCuratorAgent that queries a Foundry IQ knowledge base and requires citations in every response. Also connect to the Microsoft Learn MCP server as an additional tool."_

### [x] 2.5 Test Learning Path Curator with sample input

```python
curator = LearningPathCuratorAgent()
result = curator.run(role="Cloud Engineer", target="AZ-204")
print(result)
```

- Verify citations appear in output
- Verify Microsoft Learn content is retrieved
  ✅ **Sprint 2 done when**: Curator returns cited answers from Foundry IQ

---

## SPRINT 3 — Study Plan Generator + Fabric IQ (June 6–7)

### [x] 3.1 Model the Fabric IQ semantic ontology

Entities to model:

- `Employee` → has Role, has CertificationTarget
- `Certification` → has Skills[], has RecommendedHours, has Prerequisites[]
- `Role` → has RequiredCertifications[], has SkillAreas[]
- `SkillGap` → Employee vs Certification.Skills delta
- `ReadinessScore` → float 0–100, derived from practice scores + study hours

Create this as a JSON schema in `docs/fabric_iq_ontology.json`

### [x] 3.2 Write study_plan_generator.py

- Inherits from BaseAgent
- Takes: learner profile (from synthetic data), certification target, work signals
- Uses Fabric IQ semantic layer to:
  - Look up recommended study hours for the certification
  - Identify skill gaps based on learner role
  - Calculate realistic daily study allocation
- Returns: a structured weekly study plan with milestones
- 💡 Prompt: _"Write a StudyPlanGeneratorAgent that uses a Fabric IQ semantic model to generate a capacity-aware study schedule, accounting for meeting hours and focus windows from work signals"_

### [x] 3.3 Test Study Plan Generator

```python
planner = StudyPlanGeneratorAgent()
result = planner.run(learner_id="L-1001", certification="AZ-204")
print(result)
```

✅ **Sprint 3 done when**: Planner outputs a structured, realistic study schedule

---

## SPRINT 4 — Engagement Agent + Work IQ (June 7–8)

### [x] 4.1 Write engagement_agent.py

- Inherits from BaseAgent
- Takes: work signals (meeting_hours_per_week, focus_hours_per_week, preferred_learning_slot)
- Uses Work IQ context to:
  - Identify the best time windows to study (avoid peak meeting periods)
  - Personalise reminder tone based on workload pressure
  - Avoid generic "remember to study!" messages
- Returns: personalised engagement recommendations and suggested study slots
- 💡 Prompt: _"Write an EngagementAgent that uses Work IQ signals (meeting load, focus time, preferred slots) to generate personalised, non-intrusive study reminders that adapt to the learner's work rhythm"_

### [x] 4.2 Test Engagement Agent

```python
engagement = EngagementAgent()
result = engagement.run(employee_id="EMP-001")
print(result)
```

✅ **Sprint 4 done when**: Agent outputs personalised, timing-aware suggestions (not generic reminders)

---

## SPRINT 5 — Critic/Verifier + Assessment Agent (June 8–9)

### [x] 5.1 Write critic_verifier.py ⭐ (This is your differentiator)

- Inherits from BaseAgent
- Takes: any agent output + the original question
- Checks:
  - Is every factual claim cited to a source?
  - Does the answer actually address the question?
  - Are there any hallucinated certification names or exam codes?
  - Is the content appropriate for a work context?
- Returns: `{"approved": bool, "issues": [], "revised_output": str}`
- If approved=False, the orchestrator re-runs the originating agent
- 💡 Prompt: _"Write a CriticVerifierAgent that reviews another agent's output and checks for: unsupported claims, hallucinated certification codes, irrelevant answers, and inappropriate content. Return a structured verdict with specific issues listed."_

### [x] 5.2 Write assessment_agent.py

- Inherits from BaseAgent
- Takes: certification target, learner's study history
- Queries Foundry IQ to generate 5 grounded quiz questions (always cited)
- Evaluates learner answers and produces a readiness score 0–100
- Feeds score into Fabric IQ readiness model
- Loops back to study plan if score < 75
- 💡 Prompt: _"Write an AssessmentAgent that generates cited quiz questions from a Foundry IQ knowledge base, evaluates answers, returns a readiness score, and recommends next steps based on a Fabric IQ pass threshold"_

### [x] 5.3 Connect Critic/Verifier to Assessment Agent

- Assessment Agent output → Critic reviews it → only approved output reaches the learner
  ✅ **Sprint 5 done when**: Assessment loop works with critic gating output

---

## SPRINT 6 — Manager Insights + Orchestrator (June 9–10)

### [x] 6.1 Write manager_insights.py

- Inherits from BaseAgent
- Takes: list of employee IDs (a team)
- Aggregates from Fabric IQ:
  - Team-level pass rates and average readiness scores
  - Which certifications are at risk (< 70% readiness average)
  - Capacity-constrained team members (> 20 meeting hours/week)
- Returns: structured manager dashboard summary
- **Privacy rule**: Never surface individual scores — only team aggregates
- 💡 Prompt: _"Write a ManagerInsightsAgent that reads from Fabric IQ semantic data to produce a team-level certification readiness dashboard without exposing individual employee scores"_

### [x] 6.2 Write orchestrator.py ⭐ (The star of your demo)

This is the top-level Planner–Executor agent. It should:

- Accept a natural language request (e.g. "Help me prepare for AZ-204")
- Decompose it into sub-tasks using a planning step
- Route each sub-task to the right specialist agent
- Pass outputs through the Critic/Verifier before returning to user
- Handle the feedback loop: if assessment fails → loop back to study plan
- Log every step with trace IDs for observability
- 💡 Prompt: _"Write an OrchestratorAgent that implements the Planner-Executor pattern: plans a multi-step workflow, dispatches to specialist agents, passes results through a CriticVerifier, and manages the study-assess-loop feedback cycle. Include OpenTelemetry trace logging."_

### [x] 6.3 End-to-end test

```python
orchestrator = OrchestratorAgent()
result = orchestrator.run("I'm a Cloud Engineer and I want to get AZ-204 certified")
print(result)
```

✅ **Sprint 6 done when**: Full end-to-end flow works from one natural language input

---

## SPRINT 7 — Evaluation + Telemetry (June 10–11)

### [x] 7.1 Write evaluate_agents.py

- Test cases for each agent with expected output characteristics
- Scoring rubric: citation present? reasoning steps visible? no hallucinations?
- Run automated eval across 5 synthetic learner scenarios
- 💡 Prompt: _"Write an evaluation harness that tests each agent with synthetic input, checks for citations, multi-step reasoning, and no hallucinated exam codes, and outputs a score card"_

### [x] 7.2 Add OpenTelemetry tracing to all agents

- Every agent call should emit a trace span
- Include: agent name, input summary, output summary, latency, any critic rejections
- Connect to Azure Monitor for cloud observability
- 💡 Prompt: _"Add OpenTelemetry tracing to all agents using azure-monitor-opentelemetry, emitting spans for each agent invocation with input/output metadata"_

### [x] 7.3 Add responsible AI guardrails to Orchestrator

- Input validation: reject requests with PII or inappropriate content
- Output validation: flag any response mentioning real company names or real people
- Add a safety fallback message when guardrails trigger
  ✅ **Sprint 7 done when**: Evaluation harness runs and telemetry appears in Azure Monitor

---

## SPRINT 8 — Hosted Agent Deployment (June 11–12)

### [x] 8.1 Install AZD hosted-agent prerequisites

- Install **Azure Developer CLI (AZD) 1.25.0 or later**
- Install the hosted-agent extension:

```bash
azd ext install azure.ai.agents
azd ext list
azd auth login
```

- Confirm `azure.ai.agents` is `0.1.34-preview` or later
- Confirm you have **Foundry Project Manager** at project scope
- If AZD/Toolkit will create/assign resources, confirm you also have subscription **Owner** or **User Access Administrator**, or ask an admin to grant the required roles

### [x] 8.2 Scaffold hosted agent project with AZD

Use an empty scaffold directory:

```bash
mkdir certmind-orchestrator
cd certmind-orchestrator
azd ai agent init
```

Use these options:

- Language: `Python`
- Starter template: `Basic agent (Responses, Agent Framework, Python)`
- Agent name: default `agent-framework-agent-basic-responses`
- Deployment type: `Container deploy`
- Runtime: `Python 3.13`
- Entry point: default `main.py`
- Dependency resolution: `Remote build`
- Foundry Project: use existing `certmind-agent1` unless intentionally creating a new project
- Model deployment: use existing `gpt-5-mini` unless the scaffold requires its default model temporarily

After scaffolding, adapt the generated handler to call this repo's bridge:

```python
from agents.hosted_entrypoint import run_certmind_request
```

Current scaffold path:

```text
certmind-orchestrator/agent-framework-agent-basic-invocations
```

### [ ] 8.3 Provision, run locally, and deploy with AZD

Provision resources:

```bash
azd provision
```

Run locally:

```bash
azd ai agent run
```

In another terminal:

```bash
azd ai agent invoke --local "I'm a Cloud Engineer and I want to get AZ-204 certified"
```

Deploy:

```bash
azd deploy
```

Check hosted-agent status:

```bash
azd ai agent show
```

### [ ] 8.4 Test deployed endpoint

- Use AZD:

```bash
azd ai agent invoke "I'm a Cloud Engineer and I want to get AZ-204 certified"
```

- Or get the hosted agent endpoint from `azd deploy` output
- Test in the Foundry hosted-agent playground
- Or run: `CERTMIND_HOSTED_AGENT_ENDPOINT=<endpoint> .venv/bin/python scripts/test_hosted_agent.py`
- Verify it returns the same results as local
  ✅ **Sprint 8 done when**: Live hosted endpoint responds correctly

### Optional legacy fallback: manual Docker / ACR deployment

The official AZD hosted-agent path above is preferred. If AZD hosted-agent deployment is blocked, this repo also includes a manual Docker fallback:

- `Dockerfile`
- `scripts/deploy_acr.sh`
- `certmindacr.azurecr.io/certmind-agent:latest`

---

## SPRINT 9 — Polish + Demo (June 12–14)

### [ ] 9.1 Add rich terminal UI for demo

- Use the `rich` library to pretty-print agent steps
- Show a live "reasoning trace" as the orchestrator dispatches sub-agents
- This makes your demo video dramatically more compelling

### [ ] 9.2 Write a demo script

- A scripted walkthrough covering all 3 user scenarios:
  1. Individual learner requesting study plan
  2. Learner taking assessment and failing → loops back
  3. Manager requesting team readiness summary
- Each scenario shows different agents activating

### [ ] 9.3 Record demo video

- Show the terminal or a simple web UI
- Narrate which agent is doing what and which IQ layer is being used
- Show the Critic/Verifier rejecting a bad answer at least once (staged is fine)
- Keep under 5 minutes

### [ ] 9.4 Final README pass

- Add video link
- Check all badges render
- Confirm submission checklist is complete

### [ ] 9.5 Submit!

- Hackathon platform → Projects → Submit
- Deadline: **June 14, 2026**
  ✅ **ALL DONE** 🏆
