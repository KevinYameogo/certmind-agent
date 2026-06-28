# 🎬 CertMind Demo - Ready for LinkedIn!

## ✅ What You Have

Your project has **3 demo scripts** ready to use:

### 1. **Terminal Demo** - `scripts/demo.py`
- Single learner scenario (Cloud Engineer → AZ-204)
- Live ASCII architecture visualization
- Shows all agents working sequentially
- Beautiful colored output with Rich library

### 2. **Full Terminal Demo** - `scripts/demo_full.py`
- **4 complete scenarios:**
  - Learner fails assessment → feedback loop
  - Learner passes assessment → exam ready
  - Manager dashboard with team insights
  - Responsible AI guardrail blocks bad requests
- Interactive menu to choose scenarios
- Option to run ALL scenarios sequentially (press "A")

### 3. **Web UI Demo** - React app
- Beautiful glassmorphic interface
- Live agent architecture diagram
- Real-time status updates
- Microsoft IQ badges visualization
- Trace logs with timestamps
- Interactive notebook with pre-built scenarios

---

## 🚀 How to Run (Super Quick)

### Option A: Automated Setup

```bash
# One command to set everything up
./QUICK_START.sh
```

Then run your preferred demo (options shown at the end).

### Option B: Manual Setup

```bash
# 1. Activate Python environment
source .venv/bin/activate

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Choose your demo:

# Terminal Demo (simple)
python scripts/demo.py

# OR Full Demo (all 4 scenarios)
python scripts/demo_full.py

# OR Web UI (most visual)
python scripts/ui_server.py
# Then open http://localhost:8080
```

---

## 🎥 Best Demo for LinkedIn

### Recommendation: **Web UI Demo** (2 minutes)

**Why?**
- Most professional looking
- Shows live agent orchestration
- Beautiful visual design
- Easy for viewers to understand

**Recording Steps:**

1. **Start the server:**
   ```bash
   source .venv/bin/activate
   python scripts/ui_server.py
   ```

2. **Open browser to:** `http://localhost:8080`

3. **Start recording** (Cmd+Shift+5 on Mac)

4. **Click scenario:** "I'm a Cloud Engineer and I want to get AZ-204 certified"

5. **Show:**
   - Agents activating in real-time
   - IQ badges lighting up
   - Trace logs updating
   - Final learning path output

6. **Stop recording**

**Duration:** 1-2 minutes is perfect for LinkedIn!

---

## 📱 LinkedIn Post Template

```
🧠 CertMind: AI-Powered Certification Coaching

I built a multi-agent system for Microsoft's Agents League Hackathon 2026!

🤖 7 Specialized Agents working together
🧩 All 3 Microsoft IQ Layers (Foundry + Work + Fabric)
🛡️ Critic/Verifier safety pattern
🔄 Feedback loops for personalized learning
📊 Privacy-compliant manager dashboards

Tech Stack:
• Microsoft Foundry + GPT-5-mini
• Python + FastAPI
• React + Vite
• Azure AI Search

Watch the demo to see real-time agent orchestration! 👇

[Attach your video]

#AgentsLeague2026 #MicrosoftFoundry #AIAgents #MultiAgent #AzureAI #MachineLearning
```

---

## 🎯 Key Demo Points to Highlight

While recording, mention these points:

1. **"7 specialized agents orchestrated by a planner"**
   - Learning Path Curator
   - Study Plan Generator
   - Engagement Agent
   - Assessment Agent
   - Critic/Verifier
   - Manager Insights
   - Orchestrator

2. **"Integrates all 3 Microsoft IQ layers"**
   - **Foundry IQ** = Knowledge base (grounded answers)
   - **Work IQ** = Calendar & meeting signals
   - **Fabric IQ** = Semantic business data

3. **"Built-in safety patterns"**
   - Critic/Verifier checks every output
   - Responsible AI guardrails
   - PII detection
   - Blocked term filtering

4. **"Feedback loops for learning"**
   - If assessment fails → back to study plan
   - Adapts based on work capacity
   - Personalized scheduling

---

## 📊 What Each Demo Shows

| Feature | Terminal Demo | Full Demo | Web UI |
|---------|--------------|-----------|--------|
| Single learner scenario | ✅ | ✅ | ✅ |
| Visual architecture | ASCII art | ASCII art | Interactive diagram |
| Agent execution | Sequential | Sequential | Real-time |
| Assessment loop | ❌ | ✅ | ✅ |
| Manager dashboard | ❌ | ✅ | ✅ |
| AI guardrails | ❌ | ✅ | ✅ |
| IQ badges | ❌ | ❌ | ✅ |
| Trace logs | Terminal | Terminal | Live updates |
| Best for | Quick test | Comprehensive | Recording |

---

## 🎬 Alternative: Full Terminal Demo

If you prefer terminal recording:

```bash
python scripts/demo_full.py
```

Choose **"A"** to run all scenarios.

This shows:
- ✅ Learner success scenario
- ✅ Learner failure scenario (feedback loop)
- ✅ Manager dashboard
- ✅ Responsible AI guardrails

**Recording tip:** Use a larger terminal font size for readability!

---

## 🐛 Quick Troubleshooting

### "Module not found"
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Web UI blank page
```bash
cd ui
npm install
npm run build
cd ..
python scripts/ui_server.py
```

### Port 8080 in use
```bash
lsof -ti:8080 | xargs kill -9
```

---

## 📁 Project Structure (for reference)

```
certmind-agent/
├── DEMO_GUIDE.md          ← Detailed guide (you're here!)
├── QUICK_START.sh         ← Automated setup script
├── scripts/
│   ├── demo.py           ← Simple terminal demo
│   ├── demo_full.py      ← Full demo (4 scenarios)
│   └── ui_server.py      ← Web UI backend
├── ui/                    ← React frontend
├── agents/                ← Agent implementations
├── synthetic-data/        ← Demo data
└── docs/                  ← Architecture docs
```

---

## 🎉 You're Ready!

**Next Steps:**

1. ✅ Run the setup: `./QUICK_START.sh` (or manual steps above)
2. ✅ Test the demo: Choose your preferred option
3. ✅ Record your screen: Show agents in action
4. ✅ Post on LinkedIn: Use the template above
5. ✅ Tag Microsoft and use hashtags!

**Good luck with your LinkedIn post! 🚀**

---

## 📧 Need Help?

Check these files:
- `DEMO_GUIDE.md` - Full detailed guide
- `docs/ARCHITECTURE.md` - System architecture
- `README.md` - Project overview
