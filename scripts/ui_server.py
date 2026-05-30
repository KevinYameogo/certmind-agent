"""FastAPI backend for CertMind React UI — streams live agent events via SSE."""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UI_DIST = PROJECT_ROOT / "ui" / "dist"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.orchestrator import OrchestratorAgent  # noqa: E402

app = FastAPI(title="CertMind UI Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    request: str


# ── Agent metadata (icon, label, IQ layer) ────────────────────────────────────

AGENT_META: dict[str, dict[str, str]] = {
    "learning_path_curator": {
        "icon": "📘",
        "label": "Learning Path Curator",
        "role": "RAG · Knowledge Retrieval",
        "iq": "foundry",
    },
    "study_plan_generator": {
        "icon": "📅",
        "label": "Study Plan Generator",
        "role": "Scheduling · Pacing",
        "iq": "work",
    },
    "engagement_agent": {
        "icon": "💬",
        "label": "Engagement Agent",
        "role": "Motivational Coaching",
        "iq": "work",
    },
    "assessment_agent": {
        "icon": "📝",
        "label": "Assessment Agent",
        "role": "Quiz & Gap Analysis",
        "iq": "fabric",
    },
    "critic_verifier": {
        "icon": "🛡️",
        "label": "Critic Verifier",
        "role": "Quality Gate · Safety",
        "iq": "foundry",
    },
    "manager_insights": {
        "icon": "📊",
        "label": "Manager Insights",
        "role": "Team Dashboard",
        "iq": "fabric",
    },
}


# ── SSE Endpoint ──────────────────────────────────────────────────────────────

@app.post("/api/run")
async def run_agent(body: RunRequest):  # noqa: C901
    queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def emit(event: dict[str, Any]) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, event)

    def sync_run() -> None:
        orchestrator = OrchestratorAgent()

        # ── Patch _plan to capture and emit the workflow plan ─────────────
        original_plan = orchestrator._plan  # bound method

        def patched_plan(request_arg: str) -> dict[str, Any]:
            plan = original_plan(request_arg)
            emit({"type": "plan", "data": plan})
            return plan

        orchestrator._plan = patched_plan  # type: ignore[method-assign]

        # ── Patch _span to emit agent_start / agent_done / agent_error ────
        original_span = orchestrator._span  # bound method

        def patched_span(name: str, callback) -> Any:
            meta = AGENT_META.get(
                name, {"icon": "🤖", "label": name, "role": "", "iq": "foundry"}
            )
            emit({"type": "agent_start", "agent": name, "meta": meta})
            t0 = time.perf_counter()
            try:
                result = original_span(name, callback)
                elapsed_ms = round((time.perf_counter() - t0) * 1000)
                emit({"type": "agent_done", "agent": name, "elapsed_ms": elapsed_ms, "meta": meta})
                return result
            except Exception as exc:
                elapsed_ms = round((time.perf_counter() - t0) * 1000)
                emit({"type": "agent_error", "agent": name, "error": str(exc), "elapsed_ms": elapsed_ms, "meta": meta})
                raise

        orchestrator._span = patched_span  # type: ignore[method-assign]

        # ── Run the workflow ───────────────────────────────────────────────
        try:
            result = orchestrator.run(body.request)
            emit({"type": "result", "data": result})
        except Exception as exc:
            emit({"type": "error", "error": str(exc)})
        finally:
            emit(None)  # sentinel → close the stream

    async def generate():
        task = asyncio.create_task(asyncio.to_thread(sync_run))
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=120.0)
                if event is None:
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    break
                yield f"data: {json.dumps(event, default=str)}\n\n"
        except asyncio.TimeoutError:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Timeout waiting for agent'})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'error': str(exc)})}\n\n"
        finally:
            task.cancel()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


# ── Serve built React SPA ─────────────────────────────────────────────────────

if UI_DIST.exists():
    _assets = UI_DIST / "assets"
    if _assets.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):  # noqa: ARG001
        return FileResponse(str(UI_DIST / "index.html"))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    print("\n  🧠 CertMind UI Server")
    print("  ─────────────────────────────────────")
    print("  API  → http://localhost:8080/api/health")
    if UI_DIST.exists():
        print("  App  → http://localhost:8080")
    else:
        print("  Dev  → run `npm run dev` inside ui/")
    print("  ─────────────────────────────────────\n")

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
