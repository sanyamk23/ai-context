"""Tests for the codebase scanner."""

from pathlib import Path
import tempfile

import pytest

from contextly.analyzer.scanner import scan_codebase, EXTENSION_LANG


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Create a minimal sample project for testing."""
    # Source files
    (tmp_path / "main.py").write_text("def hello(): pass")
    (tmp_path / "utils.py").write_text("import os\ndef helper(): pass")
    (tmp_path / "app.js").write_text("function init() {}")

    # Test files
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_hello(): pass")

    # Config files
    (tmp_path / "package.json").write_text('{"name": "test"}')

    # Doc files
    (tmp_path / "README.md").write_text("# Test Project")

    # Files that should be ignored
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "main.cpython-311.pyc").write_bytes(b"")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "dep.js").write_text("module.exports = {}")

    return tmp_path


def test_scan_finds_source_files(sample_project: Path) -> None:
    result = scan_codebase(sample_project)
    source_names = {f.relative_path for f in result.source_files}
    assert "main.py" in source_names
    assert "utils.py" in source_names
    assert "app.js" in source_names


def test_scan_finds_test_files(sample_project: Path) -> None:
    result = scan_codebase(sample_project)
    test_names = {f.relative_path for f in result.test_files}
    assert "tests/test_main.py" in test_names


def test_scan_finds_config_files(sample_project: Path) -> None:
    result = scan_codebase(sample_project)
    config_names = {f.relative_path for f in result.config_files}
    assert "package.json" in config_names


def test_scan_finds_doc_files(sample_project: Path) -> None:
    result = scan_codebase(sample_project)
    doc_names = {f.relative_path for f in result.doc_files}
    assert "README.md" in doc_names


def test_scan_ignores_pycache(sample_project: Path) -> None:
    result = scan_codebase(sample_project)
    all_names = {f.relative_path for f in result.files}
    assert not any("__pycache__" in n for n in all_names)


def test_scan_ignores_node_modules(sample_project: Path) -> None:
    result = scan_codebase(sample_project)
    all_names = {f.relative_path for f in result.files}
    assert not any("node_modules" in n for n in all_names)


def test_scan_builds_tree(sample_project: Path) -> None:
    result = scan_codebase(sample_project)
    assert result.tree  # Should not be empty
    assert "main.py" in result.tree


def test_scan_counts_files(sample_project: Path) -> None:
    result = scan_codebase(sample_project)
    assert result.total_files > 0


def test_scan_with_empty_directory(tmp_path: Path) -> None:
    result = scan_codebase(tmp_path)
    assert result.total_files == 0
    assert result.source_files == []


def test_extension_language_mapping() -> None:
    assert EXTENSION_LANG[".py"] == "python"
    assert EXTENSION_LANG[".js"] == "javascript"
    assert EXTENSION_LANG[".ts"] == "typescript"
    assert EXTENSION_LANG[".go"] == "go"
    assert EXTENSION_LANG[".rs"] == "rust"
