import typer
import asyncio
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.markdown import Markdown
from rich import box
from pathlib import Path

router = typer.Typer()
console = Console()




def _read_file(file: str) -> tuple[Path, str]:
    path = Path(file)
    if not path.exists():
        console.print(f"[red]✗[/red] File not found: [bold]{file}[/bold]")
        raise typer.Exit(1)
    if path.suffix not in {".py", ".js", ".ts", ".jsx", ".tsx"}:
        console.print(f"[yellow]⚠[/yellow]  Unsupported file type: {path.suffix}")
    return path, path.read_text(encoding="utf-8")


def _print_header(file: str) -> None:
    console.rule(f"[bold blue]Debug Buddy[/bold blue]")
    console.print(f"  [dim]Target:[/dim] [bold]{file}[/bold]\n")


def _print_bug_analysis(bug) -> None:
    if not bug:
        return
    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    table.add_column("Field", style="dim", width=20)
    table.add_column("Value")
    table.add_row("Category", f"[yellow]{bug.error_category.value}[/yellow]")
    table.add_row("Root cause", bug.root_cause)
    if bug.responsible_lines:
        table.add_row("Lines", bug.responsible_lines)
    if bug.summary:
        table.add_row("Summary", f"[dim]{bug.summary}[/dim]")
    console.print(Panel(table, title="[bold yellow]Bug Analysis[/bold yellow]", box=box.ROUNDED))


def _print_fix(fix) -> None:
    if not fix:
        return
    console.print(Panel(
        Syntax(fix.correct_code, "python", theme="monokai", line_numbers=True),
        title="[bold green]Fixed Code[/bold green]",
        box=box.ROUNDED,
    ))
    console.print(Panel(
        Markdown(fix.explanation),
        title="[bold]Explanation[/bold]",
        box=box.ROUNDED,
        style="dim",
    ))
    if fix.improvement_suggestions and fix.improvement_suggestions != "N/A":
        console.print(Panel(
            Markdown(fix.improvement_suggestions),
            title="[bold cyan]Improvement Suggestions[/bold cyan]",
            box=box.ROUNDED,
        ))


def _print_evaluation(evaluation) -> None:
    if not evaluation:
        return

    score = evaluation.score
    score_color = "green" if score >= 0.8 else "yellow" if score >= 0.5 else "red"

    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    table.add_column("Metric", style="dim", width=20)
    table.add_column("Score")

    def _bar(val: float, invert=False) -> str:
        v = (1 - val) if invert else val
        filled = int(v * 10)
        bar = "█" * filled + "░" * (10 - filled)
        color = "green" if v >= 0.8 else "yellow" if v >= 0.5 else "red"
        return f"[{color}]{bar}[/{color}] {val:.2f}"

    table.add_row("Validity",        _bar(evaluation.validity))
    table.add_row("Fix quality",     _bar(evaluation.code_fix))
    table.add_row("Regression risk", _bar(evaluation.regression_risk, invert=True))
    table.add_row("─" * 20,          "─" * 20)
    table.add_row(
        "Overall score",
        f"[bold {score_color}]{score:.2f}[/bold {score_color}]"
    )

    console.print(Panel(table, title="[bold]Evaluation[/bold]", box=box.ROUNDED))

    if evaluation.feedback:
        console.print(Panel(
            evaluation.feedback,
            title="[dim]Evaluator feedback[/dim]",
            box=box.SIMPLE,
            style="dim",
        ))


def _print_history(history: list) -> None:
    if not history:
        return
    table = Table(title="Refinement history", box=box.SIMPLE, show_lines=False)
    table.add_column("Iter", justify="center", width=6)
    table.add_column("Score", justify="center", width=8)
    table.add_column("Feedback", overflow="fold")

    for entry in history:
        score = entry["score"]
        color = "green" if score >= 0.8 else "yellow" if score >= 0.5 else "red"
        table.add_row(
            str(entry["iteration"]),
            f"[{color}]{score:.2f}[/{color}]",
            entry["feedback"][:120] + ("…" if len(entry["feedback"]) > 120 else ""),
        )
    console.print(table)


def _save_fix(fix, original_path: Path) -> None:
    backup = original_path.with_suffix(".bak.py")
    backup.write_text(original_path.read_text(encoding="utf-8"), encoding="utf-8")
    original_path.write_text(fix.correct_code, encoding="utf-8")
    console.print(f"[green]✓[/green] Saved to [bold]{original_path}[/bold]")
    console.print(f"[dim]  Backup → {backup}[/dim]")




async def _run_pipeline(code: str, error: str, threshold: float, max_iters: int) -> dict:
    from graph.graph import build_graph
    from graph.state import AgentState

    graph = build_graph(threshold=threshold, max_iters=max_iters)
    initial: AgentState = {
        "code": code,
        "error": error,
        "context_docs": [],
        "bug_analysis": None,
        "fix": None,
        "evaluation": None,
        "iterations": 0,
        "history": [],
        "final_code": None,
    }
    return await graph.ainvoke(initial)




@router.command()
def debug(
    file: str = typer.Argument(..., help="Path to the file to debug"),
    error: str = typer.Option("", "--error", "-e", help="Error message or traceback"),
    threshold: float = typer.Option(0.8, "--threshold", "-t", help="Min score to accept fix (0-1)"),
    max_iters: int = typer.Option(3, "--iters", "-i", help="Max refinement iterations"),
    save: bool = typer.Option(False, "--save", "-s", help="Auto-save without prompting"),
):
    """Run the full debug pipeline: retrieve → analyze → fix → evaluate."""
    path, code = _read_file(file)
    _print_header(file)

    if not error:
        error = typer.prompt("Error / traceback")
    if not error.strip():
        console.print("[red]✗[/red] Error message is required.")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Running pipeline…", total=None)
        try:
            result = asyncio.run(_run_pipeline(code, error, threshold, max_iters))
        except Exception as e:
            console.print(f"\n[red]✗ Pipeline failed:[/red] {e}")
            raise typer.Exit(1)

    console.print()
    _print_bug_analysis(result.get("bug_analysis"))
    _print_fix(result.get("fix"))
    _print_evaluation(result.get("evaluation"))
    _print_history(result.get("history", []))
    console.rule()

    fix = result.get("fix")
    if fix:
        if save or typer.confirm("\nWrite fix to file?", default=False):
            _save_fix(fix, path)
        else:
            console.print("[dim]Fix not saved.[/dim]")


@router.command()
def analyze(
    file: str = typer.Argument(..., help="Path to the file to analyze"),
    error: str = typer.Option(..., "--error", "-e", help="Error message"),
):
    """Run only bug analysis — no fix generation."""
    from agents.bug_analyzer import Bug
    from schemas.schema import CodeInput

    path, code = _read_file(file)
    _print_header(file)

    async def _run():
        code_input = CodeInput(code=code, error=error)
        agent = Bug(state=code_input)
        return await agent.analyze()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Analyzing…", total=None)
        try:
            result = asyncio.run(_run())
        except Exception as e:
            console.print(f"\n[red]✗ Analysis failed:[/red] {e}")
            raise typer.Exit(1)

    _print_bug_analysis(result)


@router.command()
def version():
    """Show Debug Buddy version."""
    console.print("[bold blue]Debug Buddy[/bold blue] v0.1.0")