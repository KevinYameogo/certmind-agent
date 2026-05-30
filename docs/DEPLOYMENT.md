# CertMind Sprint 8 Deployment

## Build and Push Image

Use Azure Container Registry Tasks so the image builds in Azure and is pushed to ACR automatically:

```bash
az acr build --registry certmindacr --image certmind-agent:latest .
```

If ACR Tasks are not enabled for the registry/subscription, use the helper script. It falls back to a local Docker build and push:

```bash
bash scripts/deploy_acr.sh
```

Expected image:

```text
certmindacr.azurecr.io/certmind-agent:latest
```

## Foundry Hosted Agent Setup

Before creating the hosted agent, grant the Foundry project managed identity pull access to ACR.

1. In Azure AI Foundry, open the project resource.
2. Go to **Identity** and copy the system-assigned managed identity Object ID.
3. In Azure Container Registry `certmindacr`, go to **Access control (IAM)**.
4. Assign the managed identity the **Container Registry Repository Reader** role.
5. In Foundry Agent Service, create a hosted agent that points to:

```text
certmindacr.azurecr.io/certmind-agent:latest
```

Set runtime environment variables from `.env`; do not paste secrets into source files.

## Local Container Smoke Test

If Docker is available locally:

```bash
docker build -t certmind-agent:local .
docker run --rm --env-file .env certmind-agent:local
```

Expected behavior: the container prints the same orchestrator JSON produced by:

```bash
.venv/bin/python agents/orchestrator.py
```

## Hosted Endpoint Smoke Test

After the hosted agent exists in Foundry, set the endpoint URL and run:

```bash
export CERTMIND_HOSTED_AGENT_ENDPOINT="https://YOUR-HOSTED-AGENT-ENDPOINT"
.venv/bin/python scripts/test_hosted_agent.py
```
