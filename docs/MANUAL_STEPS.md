# 🙋 MANUAL_STEPS.md — Things Only You Can Do

These are steps that cannot be automated or vibe-coded. Do these yourself, in order.
Each one is a gate — don't skip ahead.

---

## PHASE 1 — Accounts & Access (Do This NOW, before June 4)

### [x] 1. Create a Microsoft Azure Account

- Go to https://azure.microsoft.com/free
- Sign up with a personal Microsoft account
- The free $200 credit is sufficient for the entire hackathon using GPT-5-mini — no upgrade needed
- 💡 Only upgrade to Pay-As-You-Go if your $200 credit runs out, which is unlikely for a 10-day prototype
- ✅ Done when: You have an active Azure free trial account

### [x] 2. Create a Microsoft Foundry Project

- Go to https://ai.azure.com
- Click "New project"
- Name it: `certmind-agent`
- Select your Azure subscription and a resource group (create one called `certmind-rg`)
- Choose region: **East US** or **West Europe** (best GPT-5-mini availability)
- ✅ Done when: You see your Foundry project dashboard at ai.azure.com

### [x] 3. Deploy GPT-5-mini in Foundry

- Inside your Foundry project → go to "Models" → "Model catalog"
- Search for `gpt-5-mini`
- Click "Deploy" → choose "Global Standard"
- Name the deployment: `gpt-5-mini`
- ✅ Done when: Deployment shows status "Succeeded"
- 💡 Note: GPT-5-mini works with the Azure free trial — no paid subscription needed

### [x] 4. Get Your Project Endpoint

- In your Foundry project → Settings → copy the **Project endpoint URL**
- It looks like: `https://YOUR-PROJECT.services.ai.azure.com/...`
- Put this in your `.env` file as `AZURE_AI_PROJECT_ENDPOINT`
- ✅ Done when: You have the endpoint saved locally (NOT committed to GitHub)

### [x] 5. Create a GitHub Repository

- Go to https://github.com/new
- Name: `certmind-agent`
- Set to **Public** (required for submission)
- Don't initialise with README (you'll push the one from this project)
- ✅ Done when: Empty public repo exists at github.com/YOUR_USERNAME/certmind-agent

### [x] 6. Register on Hackathon Platform

- Go to the Agents League hackathon page
- Click Register (if not already done)
- ✅ Done when: You have official participant status and a profile

---

## PHASE 2 — Azure Services Setup (Do before June 7)

### [x] 7. Set Up Foundry IQ Knowledge Base

- In your Foundry project → go to "Foundry IQ" or "Knowledge bases"
- Click "New knowledge base" → name it `certmind-knowledge`
- Upload only the 3 markdown knowledge documents from `synthetic-data/`:
  - `cert_guide.md`
  - `team_learning_report.md`
  - `workload_insights.md`
- Keep the 3 JSON files in the code repo; agents load them directly:
  - `learner_profiles.json`
  - `work_signals.json`
  - `certification_catalog.json`
- Wait for indexing to complete (may take 5–15 minutes)
- Copy the **Knowledge base ID** — you'll need it in agent configs
- ✅ Done when: All 3 markdown docs show "Indexed" status in Foundry IQ

### [x] 8. Enable Microsoft Learn MCP Server

- Use the remote Microsoft Learn MCP Server endpoint; it is free and requires no authentication
- Add this endpoint to your `.env` as `MICROSOFT_LEARN_MCP_URL`:
  - `https://learn.microsoft.com/api/mcp`
- ✅ Done when: You can query Microsoft Learn content from your agent

### [x] 9. Set Up Azure Container Registry (for Hosted Agent deployment)

- In Azure Portal → search "Container Registry" → Create
- Name: `certmindacr` (must be globally unique, add random suffix if needed)
- SKU: Basic
- Same resource group: `certmind-rg`
- ✅ Done when: ACR is created and you can see it in your resource group

### [x] 10. Set Up Microsoft Fabric Trial (for Fabric IQ)

- Go to https://app.fabric.microsoft.com
- Start a **60-day free trial**
- Create a new workspace called `certmind-fabric`
- ✅ Done when: You have a Fabric workspace ready

---

## PHASE 3 — Discord & Community (Do before June 8)

### [x] 11. Join the Agents League Discord

- Go to https://aka.ms/agentsleague/discord
- Join the `#agentsleague` channel
- Introduce yourself — community vote is 10% of judging!
- Share progress updates as you build (this builds votes)
- ✅ Done when: You're active in Discord

### [ ] 12. Watch the Live Battle (June 10)

- Tune in to Microsoft Reactor on June 10 at 9 AM PT
- This is the Reasoning Agents battle — your track!
- Take notes on patterns experts use
- ✅ Done when: Watched and noted key techniques

---

## PHASE 4 — Submission (June 13–14)

### [ ] 13. Record Your Demo Video

- Show the full end-to-end flow (see README for what to cover)
- Keep it under 5 minutes
- Use screen recording (OBS, Loom, or QuickTime)
- Upload to YouTube (unlisted is fine) or include in repo
- ✅ Done when: Video link is ready

### [ ] 14. Final Repo Check Before Submitting

- Run: `git grep -r "AZURE\|password\|secret\|key" --include="*.py" --include="*.env"`
- Make sure `.env` is in `.gitignore` and NOT committed
- Confirm repo is **public**
- Confirm README is complete with video link
- ✅ Done when: Clean repo, no secrets, public

### [ ] 15. Submit on Hackathon Platform

- Go to the hackathon page → Projects → Submit
- Link your GitHub repo
- Fill in project description
- Attach demo video
- Select track: **Reasoning Agents**
- ✅ Deadline: June 14, 2026

---

## 💡 Tips

- Do Phase 1 steps **today** — Azure setup can take time to propagate
- GPT-5-mini works on the Azure free trial — your $200 credit covers the full hackathon build at reasonable usage
- Keep sharing on Discord — community vote (10%) can be the difference between winning and not
