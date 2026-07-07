"""Tests for the AST analyzer."""

from pathlib import Path

import pytest

from ai_context.analyzer.ast_analyzer import analyze_codebase, _analyze_python, _analyze_js_ts
from ai_context.analyzer.scanner import FileInfo


def test_analyze_python_basic() -> None:
    content = '''
"""A simple module."""

import os
from pathlib import Path

class MyClass:
    """A class."""
    def method(self):
        pass

def standalone():
    pass
'''
    module = _analyze_python("test.py", content)

    assert module.language == "python"
    assert "MyClass" in module.classes
    assert "standalone" in module.functions
    assert "os" in module.imports
    assert "pathlib" in module.imports
    assert module.docstring is not None


def test_analyze_python_syntax_error() -> None:
    content = "def broken(\n"
    module = _analyze_python("bad.py", content)
    assert module.classes == []
    assert module.functions == []


def test_analyze_js_basic() -> None:
    content = '''
import React from 'react';

class MyComponent extends React.Component {
    render() { return null; }
}

function helper() { return true; }
'''
    module = _analyze_js_ts("comp.jsx", content, "react")
    assert "MyComponent" in module.classes
    assert "helper" in module.functions
    assert "react" in module.imports


def test_analyze_ts_functions() -> None:
    content = '''
export const processData = (data) => data;
export async function fetchData() {}
const internal = () => {};
'''
    module = _analyze_js_ts("utils.ts", content, "typescript")
    assert "processData" in module.functions
    assert "fetchData" in module.functions
    assert "internal" in module.functions


def test_analyze_codebase_with_real_files(tmp_path: Path) -> None:
    # Create test files
    (tmp_path / "app.py").write_text('"""App module."""\nimport flask\n\nclass App:\n    pass\n')
    (tmp_path / "utils.py").write_text("def helper(): pass")

    files = [
        FileInfo(tmp_path / "app.py", "app.py", 50, "source", "python"),
        FileInfo(tmp_path / "utils.py", "utils.py", 30, "source", "python"),
    ]

    result = analyze_codebase(files)
    assert result.total_classes >= 1
    assert result.total_functions >= 1
    assert "flask" in [imp for m in result.modules for imp in m.imports]
