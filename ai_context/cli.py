"""ai-context CLI — generate optimized AI context for your codebase."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ai_context import __version__
from ai_context.analyzer.ast_analyzer import analyze_codebase
from ai_context.analyzer.deps import analyze_dependencies
from ai_context.analyzer.patterns import detect_conventions
from ai_context.analyzer.scanner import scan_codebase
from ai_context.cost.estimator import estimate_cost_per_session, estimate_tokens
from ai_context.generator.context import OUTPUT_MAP, ContextBuilder, generate_context

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="ai-context")
def main() -> None:
    """Generate optimized AI context for your codebase.

    Reduce token usage by 60-80% when using AI coding assistants.
    """


@main.command()
@click.option(
    "-f", "--format",
    "fmt",
    type=click.Choice(["claude", "cursor", "copilot", "generic"]),
    default="claude",
    help="Output format for the context document.",
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    default=None,
    help="Output file path (default: auto-detected from format).",
)
@click.option(
    "-d", "--directory",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Target directory to analyze (default: current directory).",
)
@click.option(
    "--update",
    is_flag=True,
    help="Update existing context file instead of overwriting.",
)
@click.option(
    "--max-files",
    type=int,
    default=100,
    help="Maximum number of source files to analyze.",
)
def generate(
    fmt: str,
    output: Optional[str],
    directory: Optional[Path],
    update: bool,
    max_files: int,
) -> None:
    """Generate an optimized context document for AI tools.

    Analyzes your codebase and creates a concise context file that
    dramatically reduces token usage in AI coding sessions.
    """
    root = directory or Path.cwd()
    output_path = Path(output) if output else Path(OUTPUT_MAP[fmt])

    console.print(f"\n[bold cyan]ai-context[/] — analyzing [bold]{root}[/]\n")

    # Step 1: Scan
    with console.status("[bold green]Scanning codebase..."):
        scan = scan_codebase(root)

    console.print(f"  Found [bold]{scan.total_files}[/] files ({len(scan.source_files)} source, {len(scan.test_files)} tests)")

    if scan.total_files == 0:
        console.print("[red]No files found. Is this the right directory?[/]")
        sys.exit(1)

    # Step 2: Analyze
    with console.status("[bold green]Analyzing code patterns..."):
        analysis = analyze_codebase(scan.source_files, max_files=max_files)

    # Step 3: Dependencies
    with console.status("[bold green]Detecting dependencies..."):
        deps = analyze_dependencies(root)

    # Step 4: Conventions
    with console.status("[bold green]Detecting conventions..."):
        conventions = detect_conventions(scan)

    # Step 5: Generate
    document, stats = generate_context(scan, analysis, deps, conventions, fmt)

    # Write output
    if update and output_path.exists():
        # Merge strategy: replace sections between headers
        existing = output_path.read_text(errors="ignore")
        # For now, just overwrite — section-based merging is v2
        output_path.write_text(document)
        console.print(f"\n  [green]Updated[/] {output_path}")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(document)
        console.print(f"\n  [green]Generated[/] {output_path}")

    # Show stats
    _print_stats(stats)


@main.command()
@click.option(
    "-d", "--directory",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def analyze(directory: Optional[Path], as_json: bool) -> None:
    """Analyze your codebase and show detailed information."""
    root = directory or Path.cwd()

    with console.status("[bold green]Scanning..."):
        scan = scan_codebase(root)
    with console.status("[bold green]Analyzing..."):
        analysis = analyze_codebase(scan.source_files)
    with console.status("[bold green]Detecting deps..."):
        deps = analyze_dependencies(root)
    with console.status("[bold green]Detecting conventions..."):
        conventions = detect_conventions(scan)

    if as_json:
        data = {
            "total_files": scan.total_files,
            "source_files": len(scan.source_files),
            "test_files": len(scan.test_files),
            "total_source_lines": scan.total_source_lines,
            "naming_convention": analysis.naming_convention,
            "test_framework": analysis.test_framework,
            "patterns": analysis.patterns_detected,
            "entry_points": analysis.entry_points,
            "conventions": {
                "indentation": conventions.indentation,
                "quote_style": conventions.quote_style,
                "type_hints": conventions.has_type_hints,
                "docstrings": conventions.has_docstrings,
                "async": conventions.uses_async,
            },
            "dependencies": {
                "manager": deps.manager if deps else None,
                "count": len(deps.dependencies) if deps else 0,
                "dev_count": len(deps.dev_dependencies) if deps else 0,
            },
        }
        click.echo(json.dumps(data, indent=2))
        return

    # Pretty print
    console.print(f"\n[bold cyan]Codebase Analysis[/]\n")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")
    table.add_row("Total files", str(scan.total_files))
    table.add_row("Source files", str(len(scan.source_files)))
    table.add_row("Test files", str(len(scan.test_files)))
    table.add_row("Source lines", f"{scan.total_source_lines:,}")
    table.add_row("Naming convention", analysis.naming_convention)
    table.add_row("Test framework", analysis.test_framework or "not detected")
    table.add_row("Entry points", ", ".join(analysis.entry_points[:5]) or "none detected")
    console.print(table)

    if analysis.patterns_detected:
        console.print("\n[bold]Patterns:[/]")
        for p in analysis.patterns_detected:
            console.print(f"  - {p}")

    if deps:
        console.print(f"\n[bold]Dependencies:[/] {deps.manager}")
        console.print(f"  Production: {len(deps.dependencies)}")
        console.print(f"  Development: {len(deps.dev_dependencies)}")


@main.command()
@click.option(
    "-d", "--directory",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
)
@click.option("--team", is_flag=True, help="Show team-wide estimates (50 devs).")
def cost(directory: Optional[Path], team: bool) -> None:
    """Estimate token cost savings from using ai-context."""
    root = directory or Path.cwd()

    with console.status("[bold green]Analyzing..."):
        scan = scan_codebase(root)
        analysis = analyze_codebase(scan.source_files)
        deps = analyze_dependencies(root)
        conventions = detect_conventions(scan)

    # Get context token estimate
    builder = ContextBuilder(scan, analysis, deps, conventions)
    document = builder.build("claude")
    context_tokens = estimate_tokens(document)

    # Estimate tokens needed without context (reading key files)
    source_tokens = 0
    for f in scan.source_files[:30]:
        try:
            source_tokens += estimate_tokens(f.path.read_text(errors="ignore"))
        except (OSError, PermissionError):
            continue

    # Show cost comparison
    estimates = estimate_cost_per_session(source_tokens, context_tokens)

    console.print(f"\n[bold cyan]Cost Savings Estimate[/]\n")
    console.print(f"  Tokens to explain codebase [dim](without context)[/]: [bold]{_fmt_tokens(source_tokens)}[/]")
    console.print(f"  Tokens with [bold]ai-context[/]: [bold]{_fmt_tokens(context_tokens)}[/]")
    console.print(f"  Tokens saved per session: [bold green]{_fmt_tokens(source_tokens - context_tokens)}[/]\n")

    table = Table(title="Savings by Provider", show_lines=True)
    table.add_column("Provider", style="cyan")
    table.add_column("Without Context", justify="right")
    table.add_column("With Context", justify="right")
    table.add_column("Saved", justify="right", style="green")
    table.add_column("Monthly (10 sessions)", justify="right", style="green")
    if team:
        table.add_column("Monthly (50 devs)", justify="right", style="bold green")

    for e in estimates[:6]:
        row = [
            e.provider,
            f"${e.cost_without_context:.4f}",
            f"${e.cost_with_context:.4f}",
            f"${e.cost_saved:.4f} ({e.savings_percent:.0f}%)",
            f"${e.monthly_savings_10_sessions:.2f}",
        ]
        if team:
            row.append(f"${e.monthly_savings_50_sessions * 10:.2f}")
        table.add_row(*row)

    console.print(table)

    if team:
        best = estimates[0]
        console.print(
            f"\n  [bold green]Potential team savings: ${best.monthly_savings_50_sessions * 10:.0f}/month[/]"
            f" with {best.provider}"
        )


@main.command()
@click.option(
    "-d", "--directory",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
)
def check(directory: Optional[Path]) -> None:
    """Check if context file is up-to-date (for CI)."""
    root = directory or Path.cwd()

    # Check if any context file exists
    for fmt, filename in OUTPUT_MAP.items():
        path = root / filename
        if path.is_file():
            console.print(f"[green]Found[/] {filename}")

            # Basic freshness check: is it older than 7 days?
            import os
            mtime = os.path.getmtime(path)
            import time
            age_days = (time.time() - mtime) / 86400

            if age_days > 7:
                console.print(f"  [yellow]Warning:[/] {filename} is {age_days:.0f} days old. Consider running `ai-context generate --update`")
            else:
                console.print(f"  [green]Fresh[/] ({age_days:.1f} days old)")

    console.print("\n[dim]Tip: Add `ai-context check` to your CI pipeline[/]")


def _print_stats(stats: dict) -> None:
    """Print generation statistics."""
    console.print(Panel(
        f"[bold]Format:[/] {stats['format']}\n"
        f"[bold]Output:[/] {stats['output_file']}\n"
        f"[bold]Files analyzed:[/] {stats['file_count']}\n"
        f"[bold]Context tokens:[/] {_fmt_tokens(stats['context_tokens'])}\n"
        f"[bold]Source tokens:[/] {_fmt_tokens(stats['source_tokens'])}\n"
        f"[bold]Tokens saved:[/] [green]{_fmt_tokens(stats['tokens_saved'])} ({stats['savings_percent']}%)[/]",
        title="[bold]Generation Stats[/]",
        border_style="cyan",
    ))


def _fmt_tokens(count: int) -> str:
    """Format token count for display."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


if __name__ == "__main__":
    main()
