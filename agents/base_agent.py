"""Shared Microsoft Foundry agent utilities."""

from __future__ import annotations

import logging
import os
import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from opentelemetry import trace

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - supports running before deps are installed
    def load_dotenv() -> bool:
        env_path = os.path.join(os.getcwd(), ".env")
        if not os.path.exists(env_path):
            return False
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                clean = line.strip()
                if not clean or clean.startswith("#") or "=" not in clean:
                    continue
                key, value = clean.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        return False


load_dotenv()

LOGGER = logging.getLogger(__name__)
_AZURE_MONITOR_CONFIGURED = False


def configure_observability() -> None:
    """Configure Azure Monitor OpenTelemetry when a connection string is present."""
    global _AZURE_MONITOR_CONFIGURED
    if _AZURE_MONITOR_CONFIGURED:
        return

    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
    if not connection_string:
        return

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
    except ImportError:
        LOGGER.warning("azure-monitor-opentelemetry is not installed; telemetry export disabled.")
        return

    configure_azure_monitor(connection_string=connection_string)
    _AZURE_MONITOR_CONFIGURED = True


@dataclass(frozen=True)
class AgentConfig:
    """Runtime configuration shared by CertMind agents."""

    project_endpoint: str
    model_deployment: str
    knowledge_base_id: str
    learn_mcp_url: str
    use_live_foundry: bool

    @classmethod
    def from_env(cls) -> "AgentConfig":
        return cls(
            project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT", ""),
            model_deployment=os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-5-mini"),
            knowledge_base_id=os.getenv("FOUNDRY_IQ_KNOWLEDGE_BASE_ID", ""),
            learn_mcp_url=os.getenv(
                "MICROSOFT_LEARN_MCP_URL",
                "https://learn.microsoft.com/api/mcp",
            ),
            use_live_foundry=os.getenv("CERTMIND_USE_FOUNDRY_LIVE", "false").lower()
            in {"1", "true", "yes"},
        )


class BaseAgent:
    """Base class for agents that can call Microsoft Foundry when configured."""

    def __init__(self, config: Optional[AgentConfig] = None) -> None:
        configure_observability()
        self.config = config or AgentConfig.from_env()
        self._project_client = None
        self._openai_client = None
        self.tracer = trace.get_tracer(f"certmind.{self.__class__.__name__}")

    @property
    def project_client(self):
        """Create a Microsoft Foundry project client lazily."""
        if self._project_client is not None:
            return self._project_client

        if not self.config.use_live_foundry:
            LOGGER.info("CERTMIND_USE_FOUNDRY_LIVE is false; using local mode.")
            return None

        if not self.config.project_endpoint:
            LOGGER.info("AZURE_AI_PROJECT_ENDPOINT is not set; using local mode.")
            return None

        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential
        except ImportError as exc:
            LOGGER.warning("Azure SDK packages are not installed: %s", exc)
            return None

        try:
            self._project_client = AIProjectClient(
                endpoint=self.config.project_endpoint,
                credential=DefaultAzureCredential(),
            )
        except Exception as exc:  # pragma: no cover - depends on Azure runtime
            LOGGER.exception("Could not initialise Foundry project client: %s", exc)
            return None

        return self._project_client

    @property
    def openai_client(self):
        """Create the Foundry-backed OpenAI client lazily."""
        if self._openai_client is not None:
            return self._openai_client

        project_client = self.project_client
        if project_client is None:
            return None

        try:
            self._openai_client = project_client.get_openai_client()
        except Exception as exc:  # pragma: no cover - depends on Azure runtime
            LOGGER.exception("Could not initialise Foundry OpenAI client: %s", exc)
            return None

        return self._openai_client

    def run(self, prompt: str) -> str:
        """Run a prompt through Foundry when available."""
        client = self.openai_client
        if client is None:
            raise RuntimeError("Foundry client is not configured; use an agent method with local fallback.")

        try:
            response = client.responses.create(
                model=self.config.model_deployment,
                input=prompt,
            )
            return response.output_text
        except Exception as exc:  # pragma: no cover - depends on Azure runtime
            LOGGER.warning("Foundry run unavailable; falling back when supported: %s", exc)
            raise

    @staticmethod
    def has_citation(text: str) -> bool:
        """Return True when an answer contains markdown-style source citations."""
        return "[source:" in text.lower()

    def trace_call(
        self,
        agent_name: str,
        input_summary: str,
        callback: Callable[[], Any],
    ) -> Any:
        """Trace one agent invocation with local and Azure Monitor-compatible metadata."""
        start = time.perf_counter()
        with self.tracer.start_as_current_span(agent_name) as span:
            span.set_attribute("certmind.agent", agent_name)
            span.set_attribute("certmind.input_summary", input_summary[:500])
            try:
                output = callback()
                status = "ok"
                span.set_attribute("certmind.output_summary", self.summarize_output(output))
                span.set_attribute("certmind.status", status)
                if isinstance(output, dict) and "critic_verdict" in output:
                    verdict = output["critic_verdict"]
                    span.set_attribute("certmind.critic_approved", bool(verdict.get("approved")))
                    span.set_attribute("certmind.critic_issue_count", len(verdict.get("issues", [])))
                return output
            except Exception as exc:
                status = "error"
                span.set_attribute("certmind.status", status)
                span.record_exception(exc)
                raise
            finally:
                latency_ms = round((time.perf_counter() - start) * 1000, 2)
                span.set_attribute("certmind.latency_ms", latency_ms)

    @staticmethod
    def summarize_output(output: Any) -> str:
        """Return a compact output summary suitable for trace attributes."""
        if isinstance(output, str):
            return output.splitlines()[0][:200] if output else ""
        if isinstance(output, dict):
            summary = {key: output[key] for key in list(output.keys())[:6]}
            return json.dumps(summary, ensure_ascii=True, default=str)[:500]
        if isinstance(output, list):
            return f"list[{len(output)}]"
        return type(output).__name__
