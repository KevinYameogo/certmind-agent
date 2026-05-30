# CertMind Sprint 8 Deployment

## Preferred Path: AZD Hosted Agents

The preferred deployment path uses the new Foundry hosted-agent backend through Azure Developer CLI (AZD) and the `azure.ai.agents` extension. This replaces the older/manual Docker-first plan.

Official hosted-agent quickstart flow:

1. Scaffold a hosted agent project.
2. Test locally.
3. Deploy to Foundry Agent Service.
4. Chat with the agent in the playground.
5. Clean up resources when done.

## Prerequisites

Install:

- Python 3.13 or later
- Git
- Azure Developer CLI 1.25.0 or later
- `azd ai agent` extension `0.1.34-preview` or later

Check your machine:

```bash
bash scripts/check_hosted_agent_prereqs.sh
```

Install and sign in:

```bash
azd ext install azure.ai.agents
azd ext list
azd auth login
```

Permissions:

- **Foundry Project Manager** at project scope is required to create and deploy hosted agents.
- If AZD or the VS Code extension must assign ACR pull/managed-identity roles automatically, you also need subscription **Owner** or **User Access Administrator**.
- If you do not have subscription-level role-assignment permission, ask an admin to grant the hosted-agent roles from the permissions reference.

## 1. Scaffold Hosted Agent Project

Use an empty scaffold directory:

```bash
mkdir certmind-orchestrator
cd certmind-orchestrator
azd ai agent init
```

Choose:

```text
Language: Python
Starter template: Basic agent (Responses, Agent Framework, Python)
Agent name: default agent-framework-agent-basic-responses
Deployment type: Container deploy
Runtime: Python 3.13
Entry point: default main.py
Dependency resolution: Remote build
Foundry Project: use existing certmind-agent1 unless intentionally creating a new project
Model deployment: use existing gpt-5-mini if available
```

## 2. Wire CertMind Orchestrator Into the Scaffold

After the scaffold is created, keep the generated protocol and deployment files. Adapt the generated handler/body to call this repo's bridge:

```python
from agents.hosted_entrypoint import run_certmind_request

result = run_certmind_request("I'm a Cloud Engineer and I want to get AZ-204 certified")
```

Depending on where the scaffold is created, either:

- copy this repo's `agents/`, `synthetic-data/`, `docs/fabric_iq_ontology.json`, and `requirements.txt` into the scaffold, or
- create the scaffold inside this repo and adjust imports so `agents.hosted_entrypoint` is importable.

## 3. Provision Resources

From the scaffold directory:

```bash
azd provision
```

This creates or connects the hosted-agent resources declared in `azure.yaml`.

## 4. Test Locally

Start the local hosted agent:

```bash
azd ai agent run
```

In a second terminal:

```bash
azd ai agent invoke --local '{"message": "I'\''m a Cloud Engineer and I want to get AZ-204 certified"}'
```

## 5. Deploy

From the scaffold directory:

```bash
azd deploy
```

When deployment finishes, AZD prints the hosted-agent playground link and endpoint.

Check status:

```bash
azd ai agent show
```

Expected status: `Active`.

## 6. Test Deployed Agent

Use AZD:

```bash
azd ai agent invoke '{"message": "I'\''m a Cloud Engineer and I want to get AZ-204 certified"}'
```

Or use this repo's endpoint smoke test:

```bash
export CERTMIND_HOSTED_AGENT_ENDPOINT="https://YOUR-HOSTED-AGENT-ENDPOINT"
.venv/bin/python scripts/test_hosted_agent.py
```

You can also test in Foundry portal:

```text
Build -> Agents -> Open in playground
```

## Optional Monitoring

Stream hosted-agent logs:

```bash
azd ai agent monitor --follow
```

The platform injects the Application Insights connection string into the container. OpenTelemetry traces appear in the provisioned Application Insights resource under **Investigate > Transaction search** or **Performance**.

## Optional Legacy Fallback: Manual Docker / ACR

The official AZD hosted-agent flow above is preferred. This repo still includes a manual container fallback:

```bash
bash scripts/deploy_acr.sh
```

Previously pushed image:

```text
certmindacr.azurecr.io/certmind-agent:latest
sha256:deaa422706548d35d284926a2f18dbb96b76a2e36e427393035f46ddc5dd97f6
```

Use this only if AZD hosted-agent deployment is blocked.
