# 🎥 CertMind Demo Guide

> Quick guide to run the demo and record for LinkedIn

---

## 📋 Overview

CertMind has **3 demo modes**:

1. **Terminal Demo** (`scripts/demo.py`) - Single learner scenario with live agent visualization
2. **Full Terminal Demo** (`scripts/demo_full.py`) - All 4 scenarios including feedback loops, manager dashboard, and guardrails
3. **Web UI Demo** - React app with live agent architecture diagram and streaming results

---

## 🚀 Quick Start (First Time Setup)

### 1. Backend Setup

```bash
# Activate Python virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install FastAPI server dependencies
pip install fastapi uvicorn
```

### 2. Frontend Setup

```bash
# Navigate to UI directory
cd ui

# Install Node dependencies
npm install

# Build the React app
npm run build

# Go back to root
cd ..
```

---

## 🎬 Demo Options

### Option 1: Terminal Demo (Simple)

**Best for:** Quick demo showing one learner scenario

```bash
# Activate environment
source .venv/bin/activate

# Run the demo
python scripts/demo.py
```

**What you'll see:**
- ASCII logo header
- Live agent architecture visualization
- Sequential agent execution (Learning Path Curator → Study Plan → Engagement → Assessment → Critic)
- Colored status indicators (yellow=running, green=done)
- Generated learning path output
- Execution time stats

---

### Option 2: Full Terminal Demo (Comprehensive)

**Best for:** Video recording showing all features

```bash
# Activate environment
source .venv/bin/activate

# Run the full demo
python scripts/demo_full.py
```

**Interactive menu with 4 scenarios:**

1. **Learner Fails Assessment** (AZ-204)
   - Practice score: 67% (below 75% threshold)
   - Shows feedback loop back to study plan

2. **Learner Passes Assessment** (AZ-400)
   - Practice score: 82% (above 75% threshold)
   - Shows "exam ready" notification

3. **Manager Dashboard**
   - Team-level readiness aggregate
   - Privacy-compliant (no individual scores when team < 2)
   - Capacity constraints visualization

4. **Responsible AI Guardrail**
   - Blocks inappropriate requests
   - Shows PII detection
   - Displays blocked terms policy

**Pro tip:** Choose **"A"** to run all 4 scenarios sequentially for a complete demo video.

---

### Option 3: Web UI Demo (Visual)

**Best for:** Interactive demo with beautiful UI

#### Step 1: Start the Backend Server

```bash
# Activate environment
source .venv/bin/activate

# Start the FastAPI server
python scripts/ui_server.py
```

You should see:
```
🧠 CertMind UI Server
─────────────────────────────────────
API  → http://localhost:8080/api/health
App  → http://localhost:8080
─────────────────────────────────────
```

#### Step 2: Open the Web App

Open your browser and go to:
```
http://localhost:8080
```

#### Step 3: Run Demo Scenarios

The UI has a **notebook sidebar** with pre-built demo requests:

**Learner Scenarios:**
- "I'm a Cloud Engineer and I want to get AZ-204 certified"
- "I need a study plan for AZ-400 DevOps Expert"
- "What are my weak areas for AZ-204?"

**Manager Scenarios:**
- "Show me the team readiness dashboard for my engineers"
- "Which certifications are at risk on my team?"

**What you'll see:**
- Live agent architecture diagram
- Real-time agent status (idle → running → done)
- Microsoft IQ badges (Foundry, Work, Fabric)
- Trace log with timestamps
- Final output panel with formatted results

---

## 🎥 Recording Tips for LinkedIn

### Before Recording:

1. **Clear your terminal scrollback** (`Cmd+K` in macOS Terminal)
2. **Increase terminal font size** for readability
3. **Use full screen mode** (for terminal demos)
4. **Close unnecessary browser tabs** (for web UI demos)
5. **Test your microphone** if adding narration

### Demo Script Suggestions:

#### 30-Second Quick Demo:
1. Show the CertMind logo
2. Run `python scripts/demo.py`
3. Point out the live agent architecture
4. Show the final learning path output
5. "CertMind uses Microsoft Foundry + GPT-5-mini with 7 specialized agents"

#### 2-Minute Full Demo:
1. Start with web UI at http://localhost:8080
2. Click a learner request ("AZ-204 certification")
3. Show live agent execution on the architecture diagram
4. Highlight the IQ badges (Foundry, Work, Fabric)
5. Switch to terminal and run `python scripts/demo_full.py`
6. Choose scenario **"A"** for all scenarios
7. Highlight the feedback loop and guardrails
8. End with "Built for Agents League Hackathon 2026"

#### 5-Minute Comprehensive Demo:
- Do the 2-minute demo above
- Add Manager Dashboard scenario
- Explain each IQ layer (Foundry = knowledge, Work = capacity, Fabric = semantic)
- Show the Critic/Verifier safety pattern
- Mention the tech stack (Azure Foundry, GPT-5-mini, Python, React)

### Key Points to Mention:

✅ "Multi-agent system with 7 specialized agents"  
✅ "Built on Microsoft Foundry with GPT-5-mini"  
✅ "Integrates all 3 Microsoft IQ layers"  
✅ "Critic/Verifier pattern for safety"  
✅ "Feedback loop when assessment fails"  
✅ "Privacy-compliant manager dashboard"  
✅ "Responsible AI guardrails"  

---

## 🐛 Troubleshooting

### Error: "Module not found"
```bash
# Make sure you're in the right directory
cd /Users/kevinyameogo/Desktop/certmind-agent

# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Error: "fastapi not found"
```bash
pip install fastapi uvicorn
```

### Web UI shows blank page
```bash
# Rebuild the React app
cd ui
npm run build
cd ..

# Restart the server
python scripts/ui_server.py
```

### Port 8080 already in use
```bash
# Find and kill the process
lsof -ti:8080 | xargs kill -9

# Or edit ui_server.py and change port to 8081
```

### Azure authentication errors
- The demo uses **synthetic data** and **mock responses**
- If agents try to call Azure APIs, they'll fall back to synthetic data
- Check your `.env` file has placeholder values (it does)

---

## 📊 What Each Demo Shows

### Demo.py Features:
- ✅ Single learner scenario
- ✅ Live agent architecture
- ✅ Sequential workflow
- ✅ Critic verification
- ✅ Learning path generation

### Demo_full.py Features:
- ✅ All features from demo.py, PLUS:
- ✅ Assessment feedback loop
- ✅ Pass/fail scenarios
- ✅ Manager dashboard
- ✅ Team readiness aggregate
- ✅ Responsible AI guardrails
- ✅ PII detection demo

### Web UI Features:
- ✅ All features from demo_full.py, PLUS:
- ✅ Visual agent architecture diagram
- ✅ Real-time status updates
- ✅ IQ badge visualization
- ✅ Interactive notebook interface
- ✅ Streaming trace logs
- ✅ Beautiful glassmorphic UI

---

## 🎯 Best Demo for LinkedIn

**Recommended:** Record a **2-minute video** using the **Web UI** (Option 3)

**Why?**
- Most visually appealing
- Shows live agent orchestration
- Highlights Microsoft IQ integration
- Professional interface
- Easy to follow

**Recording Steps:**
1. Start the server: `python scripts/ui_server.py`
2. Open browser to `http://localhost:8080`
3. Start screen recording (Cmd+Shift+5 on macOS)
4. Click "Cloud Engineer + AZ-204" scenario
5. Watch agents execute in real-time
6. Show the final output
7. Stop recording

**Post with:**
```
🧠 CertMind: Multi-Agent Certification Coaching

Built for Microsoft Agents League Hackathon 2026

🤖 7 specialized agents orchestrated with Foundry
🧩 Integrates all 3 Microsoft IQ layers
🛡️ Critic/Verifier safety pattern
🔄 Feedback loops for personalized learning
📊 Privacy-compliant manager dashboards

Built with: Azure Foundry • GPT-5-mini • Python • React

#AgentsLeague2026 #MicrosoftFoundry #AIAgents #MultiAgent
```

---

## 🔗 Quick Links

- **Architecture Docs:** `docs/ARCHITECTURE.md`
- **Implementation Details:** `docs/IMPLEMENTATION.md`
- **Synthetic Data:** `synthetic-data/`
- **Agent Code:** `agents/`

---

**Good luck with your demo! 🚀**
