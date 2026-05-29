# 🧠 CertMind Agent

> A multi-agent enterprise certification coaching system built on Microsoft Foundry — Agents League Hackathon 2026

[![Hackathon](https://img.shields.io/badge/Agents%20League-2026-blue)](https://aka.ms/agentsleague)
[![Track](https://img.shields.io/badge/Track-Reasoning%20Agents-purple)](https://aka.ms/agentsleague)
[![Microsoft Foundry](https://img.shields.io/badge/Built%20with-Microsoft%20Foundry-0078D4)](https://azure.microsoft.com/products/foundry)

---

## 📌 What is CertMind?

CertMind is a multi-agent enterprise learning system that helps organisations manage internal team certification programmes. It combines grounded AI retrieval, contextual work signals, and semantic business understanding to create capacity-aware, personalised certification coaching — for both individual learners and their managers.

Built entirely on Microsoft Foundry using **GPT-5-mini** as the reasoning backbone, CertMind demonstrates how multi-step reasoning agents can operate safely and reliably at enterprise scale.

> ⚠️ All data used in this project is **synthetic and fictional**. No real employee data, PII, or confidential information is included anywhere in this repository.

---

## 🏗️ Agent Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full system diagram and flow.

| Agent                      | Role                                                             | IQ Layer               |
| -------------------------- | ---------------------------------------------------------------- | ---------------------- |
| 🎓 Learning Path Curator   | Maps certification targets to grounded learning resources        | Foundry IQ             |
| 📅 Study Plan Generator    | Builds capacity-aware study schedules per role                   | Fabric IQ              |
| 🔔 Engagement Agent        | Adapts reminders to real work patterns and focus windows         | Work IQ                |
| ✅ Critic / Verifier Agent | Validates agent outputs before they reach the learner            | Foundry IQ             |
| 📝 Assessment Agent        | Generates cited, grounded quiz questions and evaluates readiness | Foundry IQ + Fabric IQ |
| 📊 Manager Insights Agent  | Surfaces team-level risk, progress, and readiness signals        | Work IQ + Fabric IQ    |
| 🧭 Orchestrator Agent      | Top-level planner; decomposes requests and routes to sub-agents  | All IQ layers          |

---

## 🔌 Microsoft IQ Integration

| IQ Layer       | How CertMind Uses It                                                                                                                                               |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Foundry IQ** | Knowledge base of synthetic certification guides, study docs, and assessment references. All agent answers are cited and grounded — no hallucinated certifications |
| **Work IQ**    | Work signals (meeting load, focus windows, collaboration patterns) inform when and how the Engagement Agent nudges learners                                        |
| **Fabric IQ**  | Semantic ontology models the relationships between employee → role → certification → skill gap → readiness score                                                   |

---

## 🧰 Tech Stack

- **Model**: GPT-5-mini via Microsoft Foundry (Azure free trial compatible)
- **Orchestration**: Microsoft Agent Framework + Foundry Agent Service
- **Grounding**: Foundry IQ (Azure AI Search backend)
- **Semantic layer**: Fabric IQ
- **Work context**: Work IQ (Microsoft 365 signals)
- **External tools**: Microsoft Learn MCP Server
- **Dev tooling**: GitHub Copilot, VS Code, Python 3.11+
- **Deployment**: Hosted Agents on Foundry Agent Service

---

## 📁 Project Structure

```
certmind-agent/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md        # Full system diagram + agent flow
│   ├── IMPLEMENTATION.md      # Step-by-step build checklist
│   └── MANUAL_STEPS.md        # Human steps (Azure setup, portal config, etc.)
├── synthetic-data/
│   ├── learner_profiles.json
│   ├── work_signals.json
│   ├── certification_catalog.json
│   ├── cert_guide.md          # Synthetic knowledge doc for Foundry IQ
│   ├── team_learning_report.md
│   └── workload_insights.md
├── agents/
│   ├── orchestrator.py
│   ├── learning_path_curator.py
│   ├── study_plan_generator.py
│   ├── engagement_agent.py
│   ├── critic_verifier.py
│   ├── assessment_agent.py
│   └── manager_insights.py
├── scripts/
│   ├── setup_foundry_iq.py    # Script to verify knowledge base docs
│   └── evaluate_agents.py     # Evaluation harness
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Azure subscription (free trial works — $200 credit covers GPT-5-mini usage)
- Microsoft Foundry project created
- VS Code + GitHub Copilot

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/certmind-agent
cd certmind-agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your Azure credentials in .env
```

### Run the Orchestrator

```bash
python agents/orchestrator.py
```

---

## 📊 Synthetic Data

All datasets are clearly fictional. See [`synthetic-data/`](synthetic-data/) for:

- Learner profiles with IDs like `L-1001`, `EMP-001`
- Work activity signals (meeting hours, focus windows)
- Certification catalog (AZ-204, AZ-400, DP-203, etc.)
- Knowledge documents used to populate Foundry IQ

---

## 🔐 Security

- No `.env` files committed — see `.gitignore`
- No real credentials, PII, or customer data anywhere in this repo
- Managed identity used for production agent identity in Foundry Agent Service
- All secrets managed via environment variables or Azure Key Vault

---

## 🎥 Demo

> Video walkthrough coming — recorded before June 14, 2026 submission deadline.

The demo shows:

1. A learner requesting a certification study plan
2. Orchestrator decomposing the task across all agents
3. Foundry IQ returning cited learning resources
4. Work IQ adapting the schedule to the learner's meeting load
5. Assessment Agent generating grounded quiz questions
6. Manager Insights Agent summarising team readiness

---

## 📋 Submission Checklist

- [ ] Multi-agent system aligned to challenge scenario
- [ ] Microsoft Foundry (SDK) used for orchestration
- [ ] All 3 Microsoft IQ layers integrated
- [ ] Multi-step reasoning demonstrated end-to-end
- [ ] Microsoft Learn MCP Server integrated
- [ ] Critic/Verifier reasoning pattern implemented
- [ ] Hosted Agent deployment on Foundry Agent Service
- [ ] Synthetic data only — no PII
- [ ] Public repo with this README
- [ ] Demo video recorded
- [ ] Telemetry and evaluation implemented

---

## 🏆 Track

**Reasoning Agents** — Agents League Hackathon @ AISF 2026, hosted by Microsoft
