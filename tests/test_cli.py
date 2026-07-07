"""Tests for the CLI."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from ai_context.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Create a realistic sample project."""
    # Main app
    (tmp_path / "app.py").write_text('''"""Main application module."""
import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello"

if __name__ == "__main__":
    app.run()
''')

    # Utils
    (tmp_path / "utils.py").write_text('''"""Utility functions."""
def format_name(first: str, last: str) -> str:
    return f"{first} {last}"
''')

    # Tests
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text('''"""Tests for app."""
import pytest
from app import app

def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
''')

    # Config
    (tmp_path / "requirements.txt").write_text("flask>=2.0\npytest>=7.0\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "sample-app"\ndescription = "A sample Flask app"\n')

    return tmp_path


def test_cli_version(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "ai-context" in result.output


def test_cli_generate_claude(runner: CliRunner, sample_project: Path) -> None:
    result = runner.invoke(main, ["generate", "-d", str(sample_project), "-o", str(sample_project / "CLAUDE.md")])
    assert result.exit_code == 0
    assert (sample_project / "CLAUDE.md").exists()
    content = (sample_project / "CLAUDE.md").read_text()
    assert len(content) > 50


def test_cli_generate_cursor(runner: CliRunner, sample_project: Path) -> None:
    result = runner.invoke(main, ["generate", "-f", "cursor", "-d", str(sample_project), "-o", str(sample_project / ".cursorrules")])
    assert result.exit_code == 0
    assert (sample_project / ".cursorrules").exists()


def test_cli_generate_generic(runner: CliRunner, sample_project: Path) -> None:
    result = runner.invoke(main, ["generate", "-f", "generic", "-d", str(sample_project), "-o", str(sample_project / "CONTEXT.md")])
    assert result.exit_code == 0
    assert (sample_project / "CONTEXT.md").exists()


def test_cli_analyze(runner: CliRunner, sample_project: Path) -> None:
    result = runner.invoke(main, ["analyze", "-d", str(sample_project)])
    assert result.exit_code == 0
    assert "flask" in result.output.lower() or "Flask" in result.output


def test_cli_analyze_json(runner: CliRunner, sample_project: Path) -> None:
    result = runner.invoke(main, ["analyze", "-d", str(sample_project), "--json"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert "total_files" in data
    assert data["total_files"] > 0


def test_cli_cost(runner: CliRunner, sample_project: Path) -> None:
    result = runner.invoke(main, ["cost", "-d", str(sample_project)])
    assert result.exit_code == 0
    assert "savings" in result.output.lower() or "cost" in result.output.lower()


def test_cli_check(runner: CliRunner, sample_project: Path) -> None:
    result = runner.invoke(main, ["check", "-d", str(sample_project)])
    # check should not fail, even if no context file exists
    assert result.exit_code == 0


def test_cli_check_with_context_file(runner: CliRunner, sample_project: Path) -> None:
    (sample_project / "CLAUDE.md").write_text("# Test")
    result = runner.invoke(main, ["check", "-d", str(sample_project)])
    assert result.exit_code == 0
    assert "Found" in result.output
