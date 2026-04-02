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

app = typer.Typer(invoke_without_command=True, add_completion=False)
console = Console()

LANGUAGE_MAP = {
    "py":   "python",
    "js":   "javascript",
    "ts":   "typescript",
    "jsx":  "jsx",
    "tsx":  "tsx",
    "c":    "c",
    "cpp":  "cpp",
}

SUPPORTED_EXTENSIONS = set(LANGUAGE_MAP.keys())

def _read_file(file: str) -> tuple[Path, str]:
    path = Path(file)
    if not path.exists():
        console.print(f"[red]✗[/red] File not found: [bold]{file}[/bold]")
        raise typer.Exit(1)
    ext = path.suffix.lstrip(".")
    if ext not in SUPPORTED_EXTENSIONS:
        console.print(f"[yellow]⚠[/yellow]  Unsupported file type: {path.suffix}")
    return path, path.read_text(encoding="utf-8")


def _language_for(path: Path) -> str:
    return LANGUAGE_MAP.get(path.suffix.lstrip(".").lower(), "text")


def _print_header(file: str) -> None:
    console.rule("[bold blue]Debug Buddy[/bold blue]")
    console.print(f"  [dim]Target:[/dim] [bold]{file}[/bold]\n")


def _print_bug_analysis(bug) -> None:
    if not bug:
        return
    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    table.add_column("Field", style="dim", width=20)
    table.add_column("Value")
    table.add_row("Category",   f"[yellow]{bug.error_category.value}[/yellow]")
    table.add_row("Root cause", bug.root_cause)
    if bug.responsible_lines:
        table.add_row("Lines", bug.responsible_lines)
    if bug.summary:
        table.add_row("Summary", f"[dim]{bug.summary}[/dim]")
    console.print(Panel(table, title="[bold yellow]Bug Analysis[/bold yellow]", box=box.ROUNDED))


def _print_fix(fix, path: Path) -> None:
    if not fix:
        return
    language = _language_for(path)
    console.print(Panel(
        Syntax(fix.correct_code, language, theme="monokai", line_numbers=True),
        title=f"[bold green]Fixed Code ({language})[/bold green]",
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

    score       = evaluation.score
    score_color = "green" if score >= 0.8 else "yellow" if score >= 0.5 else "red"

    def _bar(val: float, invert: bool = False) -> str:
        v      = (1 - val) if invert else val
        filled = int(v * 10)
        bar    = "█" * filled + "░" * (10 - filled)
        color  = "green" if v >= 0.8 else "yellow" if v >= 0.5 else "red"
        return f"[{color}]{bar}[/{color}] {val:.2f}"

    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    table.add_column("Metric", style="dim", width=20)
    table.add_column("Score")
    table.add_row("Validity",        _bar(evaluation.validity))
    table.add_row("Fix quality",     _bar(evaluation.code_fix))
    table.add_row("Regression risk", _bar(evaluation.regression_risk, invert=True))
    table.add_row("─" * 20,          "─" * 20)
    table.add_row("Overall score",   f"[bold {score_color}]{score:.2f}[/bold {score_color}]")
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
    table.add_column("Iter",     justify="center", width=6)
    table.add_column("Score",    justify="center", width=8)
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
    backup = original_path.with_suffix(f".bak{original_path.suffix}")
    backup.write_text(original_path.read_text(encoding="utf-8"), encoding="utf-8")
    original_path.write_text(fix.correct_code, encoding="utf-8")
    console.print(f"[green]✓[/green] Saved to [bold]{original_path}[/bold]")
    console.print(f"[dim]  Backup → {backup}[/dim]")


async def _run_pipeline(code: str, error: str, threshold: float, max_iters: int) -> dict:
    from graph.graph import build_graph
    from graph.state import AgentState

    graph   = build_graph(threshold=threshold, max_iters=max_iters)
    initial: AgentState = {
        "code":         code,
        "error":        error,
        "context_docs": [],
        "bug_analysis": None,
        "fix":          None,
        "evaluation":   None,
        "iterations":   0,
        "history":      [],
        "final_code":   None,
    }
    return await graph.ainvoke(initial)

@app.command()
def main(
    file:      str   = typer.Argument(...,        help="Path to the file to debug"),
    error:     str   = typer.Option("",  "--error",     "-e", help="Error message or traceback"),
    threshold: float = typer.Option(0.5, "--threshold", "-t", help="Min score to accept fix (0–1)"),
    max_iters: int   = typer.Option(3,   "--iters",     "-i", help="Max refinement iterations"),
    save:      bool  = typer.Option(False,"--save",     "-s", help="Auto-save without prompting"),
    analyze_only: bool = typer.Option(False, "--analyze-only", "-a", help="Only analyze bug, skip fix generation"),
):
    """
    Debug Buddy — AI-powered bug fixer.

    \b
    Quick start:
      debugbuddy myfile.py -e "NameError: name 'x' is not defined"
      debugbuddy myfile.py          # prompts for error interactively
      debugbuddy myfile.py -a       # analyze only, no fix
    """
    path, code = _read_file(file)
    _print_header(file)

    if not error:
        error = typer.prompt("Paste the error / traceback")
    if not error.strip():
        console.print("[red]✗[/red] An error message is required.")
        raise typer.Exit(1)

    if analyze_only:
        from agents.bug_analyzer import Bug
        from schemas.schema import CodeInput

        async def _run_analyze():
            return await Bug(state=CodeInput(code=code, error=error)).analyze()

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      TimeElapsedColumn(), console=console, transient=True) as progress:
            progress.add_task("Analyzing…", total=None)
            try:
                result = asyncio.run(_run_analyze())
            except Exception as exc:
                console.print(f"\n[red]✗ Analysis failed:[/red] {exc}")
                raise typer.Exit(1)

        _print_bug_analysis(result)
        return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  TimeElapsedColumn(), console=console, transient=True) as progress:
        progress.add_task("Running pipeline…", total=None)
        try:
            result = asyncio.run(_run_pipeline(code, error, threshold, max_iters))
        except Exception as exc:
            console.print(f"\n[red]✗ Pipeline failed:[/red] {exc}")
            raise typer.Exit(1)

    console.print()
    _print_bug_analysis(result.get("bug_analysis"))
    _print_fix(result.get("fix"), path)        
    _print_evaluation(result.get("evaluation"))
    _print_history(result.get("history", []))
    console.rule()

    fix = result.get("fix")
    if fix:
        if save or typer.confirm("\nWrite fix to file?", default=False):
            _save_fix(fix, path)
        else:
            console.print("[dim]Fix not saved.[/dim]")


if __name__ == "__main__":
    app()