#!/usr/bin/env bash
set -euo pipefail

ACR_NAME="${ACR_NAME:-certmindacr}"
IMAGE_NAME="${IMAGE_NAME:-certmind-agent:latest}"
LOGIN_SERVER="${LOGIN_SERVER:-}"

if az acr build --registry "$ACR_NAME" --image "$IMAGE_NAME" .; then
  echo "Built and pushed $IMAGE_NAME with Azure Container Registry Tasks."
  exit 0
fi

echo "ACR Tasks build failed; falling back to local Docker build and push."

if [ -z "$LOGIN_SERVER" ]; then
  LOGIN_SERVER="$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)"
fi

az acr login --name "$ACR_NAME"
docker build -t "$LOGIN_SERVER/$IMAGE_NAME" .
docker push "$LOGIN_SERVER/$IMAGE_NAME"

echo "Built and pushed $LOGIN_SERVER/$IMAGE_NAME with local Docker."
