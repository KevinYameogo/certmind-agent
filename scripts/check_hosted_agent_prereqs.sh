#!/usr/bin/env bash
set -euo pipefail

echo "Checking hosted-agent prerequisites..."

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if command -v python3.13 >/dev/null 2>&1; then
    PYTHON_BIN="python3.13"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  fi
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "Python not found. Install Python 3.13 or later."
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
import sys
version = sys.version_info
print(f"Python: {version.major}.{version.minor}.{version.micro}")
if (version.major, version.minor) < (3, 13):
    raise SystemExit("Python 3.13 or later is required for the hosted-agent quickstart.")
PY

if ! command -v git >/dev/null 2>&1; then
  echo "git not found. Install Git."
  exit 1
fi
echo "Git: $(git --version)"

if ! command -v azd >/dev/null 2>&1; then
  echo "azd not found. Install Azure Developer CLI 1.25.0 or later."
  echo "macOS: brew tap azure/azd && brew install azd"
  exit 1
fi

echo "AZD: $(azd version | head -n 1)"

if ! azd ext list | grep -q "azure.ai.agents"; then
  echo "azd extension azure.ai.agents is not installed."
  echo "Run: azd ext install azure.ai.agents"
  exit 1
fi

echo "AZD hosted-agent extension:"
azd ext list | grep "azure.ai.agents"
echo "Hosted-agent prerequisites look ready."
