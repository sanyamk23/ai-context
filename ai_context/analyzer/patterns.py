"""Convention and pattern detection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ai_context.analyzer.scanner import ScanResult


@dataclass
class Conventions:
    indentation: str = "4 spaces"
    quote_style: str = "double"
    line_ending: str = "unix"
    max_line_length: Optional[int] = None
    import_order: Optional[str] = None
    has_type_hints: bool = False
    has_docstrings: bool = False
    uses_async: bool = False
    uses_decorators: bool = False
    testing_style: Optional[str] = None  # "unittest", "pytest", "describe/it"
    config_files_present: list[str] = None

    def __post_init__(self):
        if self.config_files_present is None:
            self.config_files_present = []


def detect_conventions(scan: ScanResult) -> Conventions:
    """Detect coding conventions from the codebase."""
    conv = Conventions()

    if not scan.source_files:
        return conv

    # Sample up to 20 source files
    samples = scan.source_files[:20]
    all_content: list[str] = []

    for fi in samples:
        try:
            all_content.append(fi.path.read_text(errors="ignore"))
        except (OSError, PermissionError):
            continue

    if not all_content:
        return conv

    joined = "\n".join(all_content)

    # Indentation
    tabs = sum(c.count("\t") for c in all_content)
    four_spaces = sum(1 for c in all_content for line in c.splitlines() if line.startswith("    ") and not line.startswith("     "))
    two_spaces = sum(1 for c in all_content for line in c.splitlines() if line.startswith("  ") and not line.startswith("   "))
    if tabs > four_spaces and tabs > two_spaces:
        conv.indentation = "tabs"
    elif two_spaces > four_spaces:
        conv.indentation = "2 spaces"
    else:
        conv.indentation = "4 spaces"

    # Quote style
    single_quotes = len(re.findall(r"'[^']*'", joined))
    double_quotes = len(re.findall(r'"[^"]*"', joined))
    conv.quote_style = "single" if single_quotes > double_quotes else "double"

    # Line endings
    crlf_count = joined.count("\r\n")
    conv.line_ending = "windows" if crlf_count > len(all_content) else "unix"

    # Max line length (from config files)
    conv.max_line_length = _detect_line_length(scan)

    # Type hints (Python)
    type_hint_pattern = r"def\s+\w+\([^)]*:\s*(str|int|float|bool|list|dict|Optional|Union|Any)"
    conv.has_type_hints = bool(re.search(type_hint_pattern, joined))

    # Docstrings
    conv.has_docstrings = '"""' in joined or "'''" in joined

    # Async
    conv.uses_async = "async def" in joined or "async function" in joined

    # Decorators
    conv.uses_decorators = bool(re.search(r"^@\w+", joined, re.MULTILINE))

    # Testing style
    if "describe(" in joined or "it(" in joined:
        conv.testing_style = "jest-style"
    elif "def test_" in joined:
        conv.testing_style = "pytest"
    elif "def test" in joined:
        conv.testing_style = "unittest"

    # Config files
    config_names = {"pyproject.toml", ".eslintrc", ".prettierrc", "tsconfig.json", "tox.ini", ".flake8"}
    conv.config_files_present = [f.relative_path for f in scan.config_files if f.path.name in config_names]

    return conv


def _detect_line_length(scan: ScanResult) -> Optional[int]:
    """Try to detect max line length from config files."""
    for fi in scan.config_files:
        if fi.path.name in {".flake8", "tox.ini", "pyproject.toml"}:
            try:
                content = fi.path.read_text(errors="ignore")
                match = re.search(r"max[-_]line[-_]length\s*[=:]\s*(\d+)", content)
                if match:
                    return int(match.group(1))
            except (OSError, PermissionError):
                continue

        if fi.path.name == ".eslintrc":
            try:
                import json
                data = json.loads(fi.path.read_text())
                rules = data.get("rules", {})
                length_rule = rules.get("max-len")
                if isinstance(length_rule, list) and len(length_rule) > 1:
                    return int(length_rule[1].get("code", 120))
            except (json.JSONDecodeError, OSError, TypeError):
                continue

    return None
