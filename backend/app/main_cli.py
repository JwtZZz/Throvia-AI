from __future__ import annotations

import sys
import warnings
from pathlib import Path

from rich.console import Console
from rich.panel import Panel


warnings.simplefilter("ignore")
warnings.filterwarnings(
    "ignore",
    message=r"urllib3 v2 only supports OpenSSL 1\.1\.1\+.*",
)
warnings.filterwarnings(
    "ignore",
    message=r"The default value of `allowed_objects` will change in a future version.*",
)
warnings.filterwarnings("ignore", category=Warning, module=r"urllib3.*")
warnings.filterwarnings("ignore", category=Warning, module=r"langgraph\.cache\.base.*")


if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.graph.state import build_initial_state
from app.graph.workflow import build_workflow


console = Console()


def run_cli(user_input: str, workflow=None) -> str:
    workflow = workflow or build_workflow()
    initial_state = build_initial_state(user_input=user_input)
    final_state = workflow.invoke(initial_state)
    report = final_state.get("final_report") or "No final report was produced."
    console.print(Panel(report, title="AnthroVest AI", border_style="green"))
    return report


def interactive_cli() -> int:
    workflow = build_workflow()
    console.print("[bold green]AnthroVest AI CLI[/bold green]")
    console.print("Enter a prompt to run the multi-agent workflow.")
    console.print("Type `exit`, `quit`, or `q` to leave.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nExiting AnthroVest AI CLI.", style="yellow")
            return 0

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "q"}:
            console.print("Exiting AnthroVest AI CLI.", style="yellow")
            return 0

        run_cli(user_input, workflow=workflow)
        console.print()


def main() -> int:
    if len(sys.argv) < 2:
        return interactive_cli()

    user_input = " ".join(sys.argv[1:]).strip()
    run_cli(user_input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
