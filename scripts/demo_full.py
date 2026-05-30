"""Full CertMind demo — covers all 4 scenarios for video recording.

Scenarios
─────────
  1. Learner Fails Assessment  → feedback loop back to study plan  (L-1001 / AZ-204)
  2. Learner Passes Assessment → exam-ready notification            (L-1002 / AZ-400)
  3. Manager Dashboard        → team readiness aggregate view
  4. Responsible AI Guardrail → request blocked for policy breach

Run with:
    python scripts/demo_full.py
"""

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
from rich.prompt import Confirm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.orchestrator import OrchestratorAgent


# ─── helpers ──────────────────────────────────────────────────────────────────

def get_logo() -> Panel:
    logo = r"""
  ____          _   __  __ _           _ 
 / ___|___ _ __| |_|  \/  (_)_ __   __| |
| |   / _ \ '__| __| |\/| | | '_ \ / _` |
| |__|  __/ |  | |_| |  | | | | | | (_| |
 \____\___|_|   \__|_|  |_|_|_| |_|\__,_|
    """
    text = Text(logo, style="bold bright_cyan")
    subtitle = Text(
        "  AI-Powered Certification Coaching  ·  Multi-Agent Orchestration  ·  Azure Foundry  ",
        style="dim white",
    )
    return Panel(
        Group(Align.center(text), Align.center(subtitle)),
        border_style="cyan",
        title="[bold white]✦ Autonomous Coaching Orchestrator ✦[/bold white]",
        subtitle="[dim cyan]certmind-agent · v1.0.0[/dim cyan]",
        padding=(0, 4),
    )


AGENT_META = {
    "learning_path_curator": {"icon": "📘", "name": "Learning Path Curator",  "role": "RAG · Knowledge Retrieval"},
    "study_plan_generator":  {"icon": "📅", "name": "Study Plan Generator",   "role": "Scheduling · Pacing"},
    "engagement_agent":      {"icon": "💬", "name": "Engagement Agent",        "role": "Motivational Coaching"},
    "assessment_agent":      {"icon": "📝", "name": "Assessment Agent",        "role": "Quiz & Gap Analysis"},
    "manager_insights":      {"icon": "📊", "name": "Manager Insights",        "role": "Team Readiness · Privacy"},
    "critic_verifier":       {"icon": "🛡️ ", "name": "Critic Verifier",        "role": "Quality Gate · Safety"},
}


def make_arch_panel(agent_states: dict, start_total: float, title: str = "Live Multi-Agent Architecture") -> Panel:
    completed  = sum(1 for a in agent_states.values() if a["elapsed"] is not None)
    in_progress = sum(1 for a in agent_states.values() if "Working" in a["status"])
    elapsed_total = time.perf_counter() - start_total

    lines = []
    lines.append("      [bold bright_cyan]┌──────────────────────────────────────────┐[/bold bright_cyan]")
    lines.append("      [bold bright_cyan]│[/bold bright_cyan]         [bold white]🧠  ORCHESTRATOR  AGENT[/bold white]          [bold bright_cyan]│[/bold bright_cyan]")
    lines.append("      [bold bright_cyan]│[/bold bright_cyan]    [dim]Intent Router · Workflow Planner[/dim]      [bold bright_cyan]│[/bold bright_cyan]")
    lines.append("      [bold bright_cyan]└─────────────────────┬────────────────────┘[/bold bright_cyan]")
    lines.append("                            [bold bright_cyan]│[/bold bright_cyan]")
    lines.append("       [dim]────────── Sequential Agent Dispatch ──────────[/dim]")
    lines.append("                            [bold bright_cyan]│[/bold bright_cyan]")

    keys = list(agent_states.keys())
    for i, key in enumerate(keys):
        state = agent_states[key]
        is_last = (i == len(keys) - 1)
        connector = "└──▶" if is_last else "├──▶"
        vertical  = " "    if is_last else "│"

        if "Working" in state["status"]:
            box_color  = "bold yellow"
            status_str = "[bold blink yellow]⚡ Working...[/bold blink yellow]"
        elif state["elapsed"] is not None:
            box_color  = "bold green"
            status_str = f"[bold green]✓ Done[/bold green]  [dim]({state['elapsed']:.2f}s)[/dim]"
        elif "Failed" in state["status"] or "Blocked" in state["status"]:
            box_color  = "bold red"
            status_str = state["status"]
        else:
            box_color  = "dim"
            status_str = state["status"]

        name_col = f"{state['icon']} {state['name']}"
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

    lines.append("")
    lines.append(
        f"  [dim]Status →[/dim]  "
        f"[green]{completed} completed[/green]  "
        f"[yellow]{in_progress} running[/yellow]  "
        f"[dim]{len(keys) - completed - in_progress} queued[/dim]"
        f"   [dim]│[/dim]   [dim]Elapsed:[/dim] [white]{elapsed_total:.1f}s[/white]"
    )
    return Panel(
        "\n".join(lines),
        title=f"[bold magenta]⚡ {title}[/bold magenta]",
        border_style="magenta",
        padding=(1, 3),
    )


def run_scenario(
    console: Console,
    orchestrator: OrchestratorAgent,
    request: str,
    active_agents: list[str],
    scenario_label: str,
    scenario_color: str = "yellow",
) -> dict:
    """Run a single scenario with the live architecture view and return the result."""
    req_panel = Panel(
        f"[bold {scenario_color}]⬡  {scenario_label}[/bold {scenario_color}]\n\n"
        f"  [white italic]\"{request}\"[/white italic]",
        border_style=scenario_color,
        style="on grey11",
        padding=(1, 3),
    )
    console.print(req_panel)
    console.print("\n[dim]  Spinning up sub-agent swarm...[/dim]\n")

    agent_states = {
        key: {
            **AGENT_META[key],
            "status": "[dim]◦  Idle[/dim]",
            "elapsed": None,
        }
        for key in active_agents
    }

    start_total = time.perf_counter()
    original_span = orchestrator._span

    with Live(make_arch_panel(agent_states, start_total), console=console, refresh_per_second=15) as live:
        def verbose_span(name: str, callback) -> any:
            if name in agent_states:
                agent_states[name]["status"] = "Working"
            live.update(make_arch_panel(agent_states, start_total))

            start = time.perf_counter()
            try:
                result = original_span(name, callback)
                elapsed = time.perf_counter() - start
                if name in agent_states:
                    agent_states[name]["elapsed"] = elapsed
                    agent_states[name]["status"] = "[bold green]✓ Done[/bold green]"
                live.update(make_arch_panel(agent_states, start_total))
                time.sleep(0.4)
                return result
            except Exception:
                elapsed = time.perf_counter() - start
                if name in agent_states:
                    agent_states[name]["elapsed"] = elapsed
                    agent_states[name]["status"] = "[bold red]✗ Failed[/bold red]"
                live.update(make_arch_panel(agent_states, start_total))
                raise

        orchestrator._span = verbose_span
        result = orchestrator.run(request)
        orchestrator._span = original_span

    return result, time.perf_counter() - start_total


def print_critic_verdict(console: Console, result: dict) -> None:
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


def print_learning_path(console: Console, result: dict) -> None:
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


def print_assessment(console: Console, result: dict) -> None:
    console.print(Rule("[bold bright_yellow]Assessment & Readiness Score[/bold bright_yellow]", style="yellow"))
    assessment = result.get("result", {}).get("assessment", {})
    if not assessment:
        console.print("[dim]No assessment data.[/dim]")
        return

    evaluation = assessment.get("evaluation", {})
    next_step   = assessment.get("next_step", {})

    score_color = "green" if evaluation.get("passed") else "red"
    status_label = "✓ PASSED" if evaluation.get("passed") else "✗ BELOW THRESHOLD"

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="dim")
    table.add_column("Value", style="white")
    table.add_row("Certification",    assessment.get("certification_id", "—"))
    table.add_row("Quiz Score",       f"{evaluation.get('quiz_score', '—')}%")
    table.add_row("Readiness Score",  f"[{score_color}]{evaluation.get('readiness_score', '—')}%[/{score_color}]")
    table.add_row("Pass Threshold",   f"{evaluation.get('pass_threshold_score', '—')}%")
    table.add_row("Study Completion", f"{round(evaluation.get('study_completion_ratio', 0)*100)}%")
    table.add_row("Status",           f"[{score_color}]{status_label}[/{score_color}]")

    console.print(Panel(table, border_style=score_color, padding=(1, 3)))

    action = next_step.get("action", "")
    msg    = next_step.get("message", "")
    if action == "loop_back_to_study_plan":
        console.print(Panel(
            f"[bold yellow]↺  FEEDBACK LOOP TRIGGERED[/bold yellow]\n\n{msg}",
            title="[bold yellow]Orchestrator — Loop Back Decision[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        ))
    elif action == "schedule_exam_readiness_review":
        console.print(Panel(
            f"[bold green]🎯  EXAM READY[/bold green]\n\n{msg}",
            title="[bold green]Orchestrator — Exam Readiness Confirmed[/bold green]",
            border_style="green",
            padding=(1, 2),
        ))

    # Practice questions preview
    questions = assessment.get("questions", [])
    if questions:
        console.print(Rule("[dim]Practice Questions (Preview)[/dim]", style="dim"))
        for q in questions[:3]:
            console.print(
                f"  [bold cyan]{q['id']}.[/bold cyan] {q['question']}\n"
                f"     [dim]→ {q['expected_answer']}[/dim]\n"
                f"     [dim italic]{q['citation']}[/dim italic]\n"
            )


def print_manager_dashboard(console: Console, result: dict) -> None:
    console.print(Rule("[bold bright_magenta]Manager — Team Readiness Dashboard[/bold bright_magenta]", style="magenta"))
    dashboard = result.get("result", {})

    # The manager_insights agent returns a formatted markdown string
    if isinstance(dashboard, str):
        console.print(Panel(Markdown(dashboard), border_style="magenta", padding=(1, 3)))
        return

    # dict path (fallback)
    overview = dashboard.get("team_overview", {})
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="dim")
    table.add_column("Value", style="white")
    table.add_row("Team Size",                  str(overview.get("team_size", "—")))
    table.add_row("Avg Readiness Score",        str(overview.get("avg_readiness_score", "—")))
    table.add_row("Certs Attempted / Passed",   f"{overview.get('certifications_attempted', '—')} / {overview.get('certifications_passed', '—')}")
    table.add_row("Capacity Constrained",       str(overview.get("capacity_constrained_count", "—")))
    console.print(Panel(table, title="[bold]Team Overview[/bold]", border_style="magenta", padding=(1, 3)))

    risks = dashboard.get("certification_risks", [])
    if risks:
        console.print(Rule("[dim]Certification Risk Groups[/dim]", style="dim"))
        for r in risks:
            color = {"at_risk": "red", "watch": "yellow", "on_track": "green"}.get(r.get("risk_status"), "white")
            console.print(
                f"  [{color}]●[/{color}] [bold]{r['certification_id']}[/bold]  "
                f"({r['learner_count']} learner{'s' if r['learner_count']!=1 else ''})  "
                f"[dim]status: {r['risk_status']}[/dim]"
            )

    actions = dashboard.get("recommended_actions", [])
    if actions:
        console.print()
        console.print(Rule("[dim]Recommended Actions[/dim]", style="dim"))
        for act in actions:
            console.print(f"  [cyan]→[/cyan] {act}")


def print_guardrail_block(console: Console, result: dict) -> None:
    inner = result.get("result", {})
    guardrail = inner.get("guardrail", {})
    console.print(Panel(
        f"[bold red]🚫  REQUEST BLOCKED[/bold red]\n\n"
        f"  [dim]Guardrail type:[/dim]  [bold white]{guardrail.get('type', 'unknown')}[/bold white]\n\n"
        f"  [dim]Reason:[/dim]  {guardrail.get('reason', '—')}\n\n"
        f"  [white]{inner.get('message', '')}[/white]",
        title="[bold red]🛡️   Responsible AI Guardrail — TRIGGERED[/bold red]",
        border_style="red",
        padding=(1, 3),
    ))


# ─── scenarios ────────────────────────────────────────────────────────────────

def scenario_1_fails(console: Console) -> None:
    """Cloud Engineer (L-1001 / AZ-204) — practice score 67 → fails → loops back."""
    console.print()
    console.print(Rule(
        "[bold red]SCENARIO 1 — Learner Fails Assessment → Feedback Loop[/bold red]",
        style="red",
    ))
    console.print(
        "[dim]L-1001 · Cloud Engineer · AZ-204 · Practice score: 67% (below 75% threshold)[/dim]\n"
    )

    orch = OrchestratorAgent()
    result, elapsed = run_scenario(
        console, orch,
        request="I'm a Cloud Engineer and I want to get AZ-204 certified",
        active_agents=["learning_path_curator", "study_plan_generator", "engagement_agent",
                       "assessment_agent", "critic_verifier"],
        scenario_label="Incoming Learner Request",
        scenario_color="red",
    )

    console.print()
    console.print(Rule("[bold green]Scenario 1 Complete[/bold green]", style="green"))
    console.print(f"   [dim]Total:[/dim] [bold white]{elapsed:.2f}s[/bold white]\n")
    print_critic_verdict(console, result)
    print_assessment(console, result)
    print_learning_path(console, result)


def scenario_2_passes(console: Console) -> None:
    """DevOps Engineer (L-1002 / AZ-400) — practice score 82 → passes → exam ready."""
    console.print()
    console.print(Rule(
        "[bold green]SCENARIO 2 — Learner Passes Assessment → Exam Ready[/bold green]",
        style="green",
    ))
    console.print(
        "[dim]L-1002 · DevOps Engineer · AZ-400 · Practice score: 82% (above 75% threshold)[/dim]\n"
    )

    orch = OrchestratorAgent()
    result, elapsed = run_scenario(
        console, orch,
        request="I need a study plan for AZ-400 DevOps Expert",
        active_agents=["learning_path_curator", "study_plan_generator", "engagement_agent",
                       "assessment_agent", "critic_verifier"],
        scenario_label="Incoming Learner Request",
        scenario_color="green",
    )

    console.print()
    console.print(Rule("[bold green]Scenario 2 Complete[/bold green]", style="green"))
    console.print(f"   [dim]Total:[/dim] [bold white]{elapsed:.2f}s[/bold white]\n")
    print_critic_verdict(console, result)
    print_assessment(console, result)
    print_learning_path(console, result)


def scenario_3_manager(console: Console) -> None:
    """Manager dashboard — aggregate team readiness (privacy-safe, no individual scores)."""
    console.print()
    console.print(Rule(
        "[bold magenta]SCENARIO 3 — Manager Dashboard (Team Readiness)[/bold magenta]",
        style="magenta",
    ))
    console.print(
        "[dim]Aggregates 5 learners · Individual scores masked when group size < 2 · Privacy-compliant[/dim]\n"
    )

    orch = OrchestratorAgent()
    result, elapsed = run_scenario(
        console, orch,
        request="Show me the team readiness dashboard for my engineers",
        active_agents=["manager_insights", "critic_verifier"],
        scenario_label="Manager Request",
        scenario_color="magenta",
    )

    console.print()
    console.print(Rule("[bold green]Scenario 3 Complete[/bold green]", style="green"))
    console.print(f"   [dim]Total:[/dim] [bold white]{elapsed:.2f}s[/bold white]\n")
    print_critic_verdict(console, result)
    print_manager_dashboard(console, result)


def scenario_4_guardrail(console: Console) -> None:
    """Responsible AI guardrail — blocks request containing inappropriate/negative language."""
    console.print()
    console.print(Rule(
        "[bold red]SCENARIO 4 — Responsible AI Guardrail Triggered[/bold red]",
        style="red",
    ))
    console.print(
        "[dim]The orchestrator checks every input for PII, blocked terms, and inappropriate language[/dim]\n"
    )

    blocked_request = "This lazy engineer is worthless — punish them and fire them from the program."

    req_panel = Panel(
        "[bold red]⬡  Incoming Request (will be blocked)[/bold red]\n\n"
        f"  [white italic]\"{blocked_request}\"[/white italic]",
        border_style="red",
        style="on grey11",
        padding=(1, 3),
    )
    console.print(req_panel)
    console.print("\n[dim]  Running responsible AI input validation...[/dim]\n")

    orch = OrchestratorAgent()
    start = time.perf_counter()
    result = orch.run(blocked_request)
    elapsed = time.perf_counter() - start

    # Show the guardrail panel
    console.print()
    console.print(Rule("[bold red]Scenario 4 Complete[/bold red]", style="red"))
    console.print(f"   [dim]Blocked in:[/dim] [bold white]{elapsed*1000:.0f}ms[/bold white]\n")
    print_guardrail_block(console, result)

    # Show what terms are on the blocklist
    blocked_terms = sorted(OrchestratorAgent.BLOCKED_INPUT_TERMS)
    console.print(Panel(
        "\n".join(f"  [red]✗[/red]  [italic]{t}[/italic]" for t in blocked_terms),
        title="[bold]🛡️ Blocked Input Terms (Responsible AI Policy)[/bold]",
        border_style="dim red",
        padding=(1, 3),
    ))

    # Also demo a PII block
    console.print()
    console.print(Rule("[dim]Bonus: PII Detection Demo[/dim]", style="dim"))
    pii_request = "Help john.smith@contoso.com prepare for AZ-204 with SSN 123-45-6789"
    console.print(f"[dim]Testing:[/dim] [italic]\"{pii_request}\"[/italic]")
    pii_result = orch.run(pii_request)
    inner = pii_result.get("result", {})
    guardrail = inner.get("guardrail", {})
    console.print(Panel(
        f"[bold red]🚫 BLOCKED — {guardrail.get('type', 'pii')}[/bold red]\n\n"
        f"  {guardrail.get('reason', '—')}",
        border_style="red",
        padding=(1, 2),
    ))


# ─── main ─────────────────────────────────────────────────────────────────────

SCENARIOS = [
    ("1", "Learner Fails Assessment → Feedback Loop (AZ-204)",  scenario_1_fails),
    ("2", "Learner Passes Assessment → Exam Ready (AZ-400)",    scenario_2_passes),
    ("3", "Manager Dashboard — Team Readiness",                  scenario_3_manager),
    ("4", "Responsible AI Guardrail Triggered",                  scenario_4_guardrail),
]


def main() -> None:
    console = Console()
    console.clear()
    console.print(get_logo())
    console.print()

    # Scenario menu
    console.print(Panel(
        "\n".join(
            f"  [bold cyan]{num}.[/bold cyan]  {label}"
            for num, label, _ in SCENARIOS
        ) + "\n\n  [bold cyan]A.[/bold cyan]  Run ALL scenarios sequentially",
        title="[bold white]Available Demo Scenarios[/bold white]",
        border_style="cyan",
        padding=(1, 3),
    ))
    console.print()

    choice = console.input("[bold cyan]Select scenario (1 / 2 / 3 / 4 / A): [/bold cyan]").strip().upper()

    if choice == "A":
        for _, _, fn in SCENARIOS:
            fn(console)
            console.print()
            time.sleep(0.5)
    else:
        matched = {num: fn for num, _, fn in SCENARIOS}
        if choice in matched:
            matched[choice](console)
        else:
            console.print(f"[red]Unknown choice '{choice}'. Pick 1, 2, 3, 4, or A.[/red]")
            sys.exit(1)

    console.print()
    console.print(Rule("[bold bright_cyan]CertMind Demo Complete[/bold bright_cyan]", style="cyan"))
    console.print(
        "  [dim]All scenarios demonstrate the full multi-agent pipeline:[/dim]\n"
        "  [cyan]Orchestrator → Curator → Planner → Engagement → Assessment → Critic[/cyan]\n"
        "  [dim]with Responsible AI guardrails at every input/output boundary.[/dim]\n"
    )


if __name__ == "__main__":
    main()
