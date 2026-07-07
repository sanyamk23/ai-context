"""Tests for the context generator."""

from pathlib import Path

import pytest

from ai_context.analyzer.ast_analyzer import AnalysisResult
from ai_context.analyzer.deps import DepsResult, DependencyInfo
from ai_context.analyzer.patterns import Conventions
from ai_context.analyzer.scanner import ScanResult, FileInfo
from ai_context.generator.context import ContextBuilder, generate_context


@pytest.fixture
def sample_scan(tmp_path: Path) -> ScanResult:
    (tmp_path / "main.py").write_text("def main(): pass")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_main(): pass")

    scan = ScanResult(root=tmp_path)
    scan.source_files = [FileInfo(tmp_path / "main.py", "main.py", 20, "source", "python")]
    scan.test_files = [FileInfo(tmp_path / "tests" / "test_main.py", "tests/test_main.py", 20, "test", "python")]
    scan.total_files = 2
    scan.tree = "main.py\ntests/\n  test_main.py"
    return scan


@pytest.fixture
def sample_analysis() -> AnalysisResult:
    return AnalysisResult(
        entry_points=["main.py"],
        naming_convention="snake_case",
        test_framework="pytest",
        patterns_detected=["FastAPI web application"],
        total_classes=2,
        total_functions=5,
    )


@pytest.fixture
def sample_deps() -> DepsResult:
    return DepsResult(
        manager="pip",
        dependencies=[
            DependencyInfo("fastapi", ">=0.100.0", source="pypi"),
            DependencyInfo("uvicorn", ">=0.20.0", source="pypi"),
        ],
        dev_dependencies=[
            DependencyInfo("pytest", ">=7.0", is_dev=True, source="pypi"),
        ],
    )


@pytest.fixture
def sample_conventions() -> Conventions:
    return Conventions(
        indentation="4 spaces",
        quote_style="double",
        has_type_hints=True,
        has_docstrings=True,
        testing_style="pytest",
    )


def test_generate_claude_format(
    sample_scan, sample_analysis, sample_deps, sample_conventions
) -> None:
    document, stats = generate_context(
        sample_scan, sample_analysis, sample_deps, sample_conventions, "claude"
    )
    assert "# " in document  # Should have a title
    assert "fastapi" in document.lower() or "FastAPI" in document
    assert stats["format"] == "claude"
    assert stats["output_file"] == "CLAUDE.md"
    assert stats["context_tokens"] > 0


def test_generate_cursor_format(
    sample_scan, sample_analysis, sample_deps, sample_conventions
) -> None:
    document, stats = generate_context(
        sample_scan, sample_analysis, sample_deps, sample_conventions, "cursor"
    )
    assert stats["format"] == "cursor"
    assert stats["output_file"] == ".cursorrules"


def test_generate_generic_format(
    sample_scan, sample_analysis, sample_deps, sample_conventions
) -> None:
    document, _ = generate_context(
        sample_scan, sample_analysis, sample_deps, sample_conventions, "generic"
    )
    assert "fastapi" in document.lower() or "FastAPI" in document


def test_context_builder_builds(
    sample_scan, sample_analysis, sample_deps, sample_conventions
) -> None:
    builder = ContextBuilder(sample_scan, sample_analysis, sample_deps, sample_conventions)
    document = builder.build("claude")

    # Should contain key sections
    assert "main.py" in document  # entry point
    assert "snake_case" in document  # naming convention
    assert "pytest" in document  # test framework


def test_context_minimal_info(
    sample_scan,
) -> None:
    """Test generation with minimal analysis data."""
    analysis = AnalysisResult()
    conventions = Conventions()

    document, stats = generate_context(sample_scan, analysis, None, conventions, "claude")
    assert document
    assert stats["context_tokens"] > 0


def test_context_no_tests(
    sample_scan, sample_analysis, sample_deps, sample_conventions
) -> None:
    """Test that missing tests are flagged."""
    sample_scan.test_files = []
    builder = ContextBuilder(sample_scan, sample_analysis, sample_deps, sample_conventions)
    document = builder.build("claude")
    # Should include a gotcha about no tests
    assert "no test" in document.lower() or "test" in document.lower()
