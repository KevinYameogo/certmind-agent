# 🧠 CertMind Agent

> A multi-agent enterprise certification coaching system built on Microsoft Foundry — Agents League Hackathon 2026

[![Hackathon](https://img.shields.io/badge/Agents%20League-2026-blue)](https://aka.ms/agentsleague)
[![Track](https://img.shields.io/badge/Track-Reasoning%20Agents-purple)](https://aka.ms/agentsleague)
[![Microsoft Foundry](https://img.shields.io/badge/Built%20with-Microsoft%20Foundry-0078D4)](https://azure.microsoft.com/products/foundry)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB)](https://reactjs.org/)

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
│   ├── MANUAL_STEPS.md        # Azure setup guide
│   ├── DEPLOYMENT.md          # Deployment instructions
│   └── IMPLEMENTATION.md      # Development guide
├── synthetic-data/             # Synthetic training data
│   ├── learner_profiles.json
│   ├── work_signals.json
│   ├── certification_catalog.json
│   └── cert_guide.md
├── agents/                     # Multi-agent system
│   ├── orchestrator.py
│   ├── learning_path_curator.py
│   ├── study_plan_generator.py
│   ├── engagement_agent.py
│   ├── critic_verifier.py
│   ├── assessment_agent.py
│   └── manager_insights.py
├── scripts/                    # Demo and utility scripts
│   ├── demo.py
│   ├── demo_full.py
│   └── ui_server.py
├── ui/                         # React web interface
│   └── src/
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for Web UI)
- Azure subscription with Microsoft Foundry access

### Initial Setup

**For first-time setup with Azure integration**, follow these guides:

1. [`docs/MANUAL_STEPS.md`](docs/MANUAL_STEPS.md) - Azure account and Foundry setup
2. [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) - Deployment to Foundry Agent Service (optional)

### Quick Start (Local Demo)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/certmind-agent
cd certmind-agent

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment (optional for demo mode)
cp .env.example .env
# Edit .env with your Azure credentials for live API integration
# Or leave as-is to run in demo mode with synthetic data
```

### Running the Demos

**Option 1: Simple Terminal Demo**

```bash
source .venv/bin/activate
python scripts/demo.py
```

**Option 2: Full Terminal Demo (4 Scenarios)**

```bash
source .venv/bin/activate
python scripts/demo_full.py
# Choose "A" to run all scenarios sequentially
```

**Option 3: Web UI Demo** (Recommended)

```bash
# Build the React UI (first time only)
cd ui
npm install
npm run build
cd ..

# Start the server
source .venv/bin/activate
python scripts/ui_server.py

# Open browser to: http://localhost:8080
```

### What Each Demo Shows

- **Terminal Demo**: Single learner scenario with live agent visualization
- **Full Demo**: 4 scenarios including feedback loops, manager dashboard, and AI guardrails
- **Web UI**: Interactive interface with real-time agent execution and beautiful visualizations

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

## 🎥 Demo Video

Watch the full demo showcasing the multi-agent system in action:

[![CertMind Demo](https://img.youtube.com/vi/Msya-lIU-B8/maxresdefault.jpg)](https://youtu.be/Msya-lIU-B8)

**👉 [Watch Full Demo on YouTube](https://youtu.be/Msya-lIU-B8)**

**What you'll see:**

1. A learner requesting a certification study plan
2. Orchestrator decomposing the task across all agents
3. Live agent execution with real-time status updates
4. Microsoft IQ layers integration (Foundry + Work + Fabric)
5. Assessment Agent generating grounded quiz questions
6. Manager Insights Agent providing team readiness analytics
7. Responsible AI guardrails in action

---

---

## 🏆 Track

**Reasoning Agents** — Agents League Hackathon @ AISF 2026, hosted by Microsoft

---

## 🤝 Contributing

This project was built for Microsoft's Agents League Hackathon. Feel free to fork and extend it for your own use cases!

## 📄 License

MIT License - see LICENSE file for details
