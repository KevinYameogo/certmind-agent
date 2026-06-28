# 🙋 MANUAL_STEPS.md — Azure Setup Guide

These are steps that must be done manually to set up your own instance of CertMind.
Each step is required for the system to work properly.

---

## PHASE 1 — Azure Account & Foundry Setup

### 1. Create a Microsoft Azure Account

- Go to https://azure.microsoft.com/free
- Sign up with a Microsoft account
- The free $200 credit is sufficient for development and testing with GPT-5-mini
- ✅ Done when: You have an active Azure account

### 2. Create a Microsoft Foundry Project

- Go to https://ai.azure.com
- Click "New project"
- Name it: `certmind-agent` (or your preferred name)
- Select your Azure subscription and create a resource group (e.g., `certmind-rg`)
- Choose region: **East US** or **West Europe** (best GPT-5-mini availability)
- ✅ Done when: You see your Foundry project dashboard at ai.azure.com

### 3. Deploy GPT-5-mini in Foundry

- Inside your Foundry project → go to "Models" → "Model catalog"
- Search for `gpt-5-mini`
- Click "Deploy" → choose "Global Standard"
- Name the deployment: `gpt-5-mini`
- ✅ Done when: Deployment shows status "Succeeded"

### 4. Get Your Project Endpoint

- In your Foundry project → Settings → copy the **Project endpoint URL**
- It looks like: `https://YOUR-PROJECT.services.ai.azure.com/...`
- Put this in your `.env` file as `AZURE_AI_PROJECT_ENDPOINT`
- ✅ Done when: You have the endpoint saved locally (NOT committed to GitHub)

---

## PHASE 2 — Azure Services Setup

### 5. Set Up Foundry IQ Knowledge Base

- In your Foundry project → go to "Foundry IQ" or "Knowledge bases"
- Click "New knowledge base" → name it `certmind-knowledge`
- Upload the 3 markdown knowledge documents from `synthetic-data/`:
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

### 6. Enable Microsoft Learn MCP Server

- Use the remote Microsoft Learn MCP Server endpoint; it is free and requires no authentication
- Add this endpoint to your `.env` as `MICROSOFT_LEARN_MCP_URL`:
  - `https://learn.microsoft.com/api/mcp`
- ✅ Done when: You can query Microsoft Learn content from your agent

### 7. Set Up Azure Container Registry (for Hosted Agent deployment)

- In Azure Portal → search "Container Registry" → Create
- Name: `certmindacr` (must be globally unique, add random suffix if needed)
- SKU: Basic
- Same resource group: `certmind-rg`
- ✅ Done when: ACR is created and you can see it in your resource group

### 8. Set Up Microsoft Fabric Trial (for Fabric IQ)

- Go to https://app.fabric.microsoft.com
- Start a **60-day free trial**
- Create a new workspace called `certmind-fabric`
- ✅ Done when: You have a Fabric workspace ready

---

## Environment Variables

After completing the setup above, update your `.env` file with:

```bash
# Copy .env.example to .env and fill in these values:
AZURE_AI_PROJECT_ENDPOINT=<your-foundry-endpoint>
AZURE_AI_MODEL_DEPLOYMENT=gpt-5-mini
FOUNDRY_IQ_KNOWLEDGE_BASE_ID=<your-knowledge-base-id>
MICROSOFT_LEARN_MCP_URL=https://learn.microsoft.com/api/mcp
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=certmind-rg
```

---

## 💡 Tips

- Azure setup can take time to propagate — allow 15-30 minutes
- GPT-5-mini works on the Azure free trial
- Keep your `.env` file private and never commit it to Git
- Use the demo scripts to test your setup once complete
