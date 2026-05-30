"""Rich terminal UI demo for CertMind."""

import sys
import time
from pathlib import Path

from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.columns import Columns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.orchestrator import OrchestratorAgent


def get_logo() -> Panel:
    """Return a stylized ASCII logo for CertMind."""
    logo = r"""
  ____          _   __  __ _           _ 
 / ___|___ _ __| |_|  \/  (_)_ __   __| |
| |   / _ \ '__| __| |\/| | | '_ \ / _` |
| |__|  __/ |  | |_| |  | | | | | | (_| |
 \____\___|_|   \__|_|  |_|_|_| |_|\__,_|
    """
    text = Text(logo, style="bold bright_cyan")
    subtitle_text = Text(
        "  AI-Powered Certification Coaching  ·  Multi-Agent Orchestration  ·  Azure Foundry  ",
        style="dim white"
    )
    return Panel(
        Group(Align.center(text), Align.center(subtitle_text)),
        border_style="cyan",
        title="[bold white]✦ Autonomous Coaching Orchestrator ✦[/bold white]",
        subtitle="[dim cyan]certmind-agent · v1.0.0[/dim cyan]",
        padding=(0, 4),
    )


def main() -> None:
    """Run the rich demo."""
    console = Console()
    console.clear()

    console.print(get_logo())
    console.print()

    request = "I'm a Cloud Engineer and I want to get AZ-204 certified"
    req_panel = Panel(
        f"[bold yellow]⬡  Incoming Learner Request[/bold yellow]\n\n"
        f"  [white italic]\"{request}\"[/white italic]",
        border_style="yellow",
        style="on grey11",
        padding=(1, 3),
    )
    console.print(req_panel)
    console.print("\n[dim]  Spinning up sub-agent swarm...[/dim]\n")

    agent_states: dict[str, dict] = {
        "learning_path_curator": {
            "icon": "📘", "name": "Learning Path Curator",
            "role": "RAG · Knowledge Retrieval",
            "status": "[dim]◦  Idle[/dim]", "elapsed": None,
        },
        "study_plan_generator": {
            "icon": "📅", "name": "Study Plan Generator",
            "role": "Scheduling · Pacing",
            "status": "[dim]◦  Idle[/dim]", "elapsed": None,
        },
        "engagement_agent": {
            "icon": "💬", "name": "Engagement Agent",
            "role": "Motivational Coaching",
            "status": "[dim]◦  Idle[/dim]", "elapsed": None,
        },
        "assessment_agent": {
            "icon": "📝", "name": "Assessment Agent",
            "role": "Quiz & Gap Analysis",
            "status": "[dim]◦  Idle[/dim]", "elapsed": None,
        },
        "critic_verifier": {
            "icon": "🛡️ ", "name": "Critic Verifier",
            "role": "Quality Gate · Safety",
            "status": "[dim]◦  Idle[/dim]", "elapsed": None,
        },
    }

    start_total = time.perf_counter()
    orchestrator = OrchestratorAgent()
    original_span = orchestrator._span

    def generate_architecture_view() -> Panel:
        workflow_agents = list(agent_states.keys())
        completed  = sum(1 for a in agent_states.values() if a["elapsed"] is not None)
        in_progress = sum(1 for a in agent_states.values() if "Working" in a["status"])
        elapsed_total = time.perf_counter() - start_total

        lines = []

        # ── Orchestrator node ──────────────────────────────────────────────
        lines.append("      [bold bright_cyan]┌──────────────────────────────────────────┐[/bold bright_cyan]")
        lines.append("      [bold bright_cyan]│[/bold bright_cyan]         [bold white]🧠  ORCHESTRATOR  AGENT[/bold white]          [bold bright_cyan]│[/bold bright_cyan]")
        lines.append("      [bold bright_cyan]│[/bold bright_cyan]    [dim]Intent Router · Workflow Planner[/dim]      [bold bright_cyan]│[/bold bright_cyan]")
        lines.append("      [bold bright_cyan]└─────────────────────┬────────────────────┘[/bold bright_cyan]")
        lines.append("                            [bold bright_cyan]│[/bold bright_cyan]")
        lines.append("       [dim]────────── Sequential Agent Dispatch ──────────[/dim]")
        lines.append("                            [bold bright_cyan]│[/bold bright_cyan]")

        # ── Sub-agent nodes ────────────────────────────────────────────────
        for i, agent_key in enumerate(workflow_agents):
            state   = agent_states[agent_key]
            is_last = (i == len(workflow_agents) - 1)
            connector = "└──▶" if is_last else "├──▶"
            vertical  = " "    if is_last else "│"

            # Colour-code the box border by state
            if "Working" in state["status"]:
                box_color  = "bold yellow"
                status_str = "[bold blink yellow]⚡ Working...[/bold blink yellow]"
            elif state["elapsed"] is not None:
                box_color  = "bold green"
                status_str = f"[bold green]✓ Done[/bold green]  [dim]({state['elapsed']:.2f}s)[/dim]"
            else:
                box_color  = "dim"
                status_str = state["status"]

            name_col = f"{state['icon']} {state['name']}"
            role_col = f"[dim italic]{state['role']}[/dim italic]"
            lines.append(
                f"      [bold bright_cyan]{connector}[/bold bright_cyan] "
                f"[{box_color}]┤[/{box_color}] {name_col.ljust(28)}"
                f"[{box_color}]├[/{box_color}]  {status_str}"
            )
            lines.append(
                f"      [bold bright_cyan]{vertical}[/bold bright_cyan]       "
                f"  [dim]└ {state['role']}[/dim]"
            )
            if not is_last:
                lines.append(f"      [bold bright_cyan]{vertical}[/bold bright_cyan]")

        # ── Stats footer ───────────────────────────────────────────────────
        lines.append("")
        lines.append(
            f"  [dim]Status →[/dim]  "
            f"[green]{completed} completed[/green]  "
            f"[yellow]{in_progress} running[/yellow]  "
            f"[dim]{len(workflow_agents) - completed - in_progress} queued[/dim]"
            f"   [dim]│[/dim]   [dim]Elapsed:[/dim] [white]{elapsed_total:.1f}s[/white]"
        )

        return Panel(
            "\n".join(lines),
            title="[bold magenta]⚡ Live Multi-Agent Architecture[/bold magenta]",
            border_style="magenta",
            padding=(1, 3),
        )

    with Live(generate_architecture_view(), console=console, refresh_per_second=15) as live:
        def verbose_span(name: str, callback: callable) -> any:
            if name in agent_states:
                agent_states[name]["status"] = "Working"
            live.update(generate_architecture_view())

            start = time.perf_counter()
            try:
                result = original_span(name, callback)
                elapsed = time.perf_counter() - start
                if name in agent_states:
                    agent_states[name]["elapsed"] = elapsed
                    agent_states[name]["status"]  = "[bold green]✓ Done[/bold green]"
                live.update(generate_architecture_view())
                time.sleep(0.45)
                return result
            except Exception:
                elapsed = time.perf_counter() - start
                if name in agent_states:
                    agent_states[name]["elapsed"] = elapsed
                    agent_states[name]["status"]  = "[bold red]✗ Failed[/bold red]"
                live.update(generate_architecture_view())
                raise

        orchestrator._span = verbose_span
        result = orchestrator.run(request)

    total_elapsed = time.perf_counter() - start_total
    console.print()
    console.print(Rule("[bold green]🚀  Workflow Complete[/bold green]", style="green"))
    console.print(f"   [dim]Total execution time:[/dim] [bold white]{total_elapsed:.2f}s[/bold white]\n")

    # ── Critic verdict ─────────────────────────────────────────────────────
    verdict = result.get("critic_approved", False)
    if verdict:
        console.print(Panel(
            "[bold green]✓  APPROVED[/bold green]\n\n"
            "  The multi-agent plan passed all quality gates,\n"
            "  safety checks, and skill-gap validations.",
            title="[bold green]🛡️   Critic Verification Layer[/bold green]",
            border_style="green",
            padding=(1, 3),
        ))
    else:
        issues = result.get("critic_issues", [])
        console.print(Panel(
            f"[bold red]✗  REJECTED[/bold red]\n\nIssues detected:\n{issues}",
            title="[bold red]🛡️   Critic Verification Layer[/bold red]",
            border_style="red",
            padding=(1, 3),
        ))

    # ── Learning path preview ──────────────────────────────────────────────
    console.print()
    console.print(Rule("[bold bright_blue]Generated Learning Path[/bold bright_blue]", style="blue"))
    learning_path = result.get("result", {}).get("learning_path", "")
    if learning_path:
        preview = learning_path[:1800] + (
            "\n\n[dim]…truncated — full plan available in JSON output[/dim]"
            if len(learning_path) > 1800 else ""
        )
        console.print(Panel(Markdown(preview), border_style="blue", padding=(1, 3)))
    else:
        console.print("[dim]No learning path generated.[/dim]")


if __name__ == "__main__":
    main()
