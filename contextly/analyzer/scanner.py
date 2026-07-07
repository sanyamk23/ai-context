"""File discovery and codebase structure mapping."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from contextly.utils.ignore import FileFilter


@dataclass
class FileInfo:
    path: Path
    relative_path: str
    size: int
    category: str  # source, config, test, doc, other
    language: Optional[str] = None


@dataclass
class ScanResult:
    root: Path
    files: list[FileInfo] = field(default_factory=list)
    source_files: list[FileInfo] = field(default_factory=list)
    config_files: list[FileInfo] = field(default_factory=list)
    test_files: list[FileInfo] = field(default_factory=list)
    doc_files: list[FileInfo] = field(default_factory=list)
    tree: str = ""
    total_files: int = 0
    total_source_lines: int = 0


# Max file size to analyze (500KB)
MAX_FILE_SIZE = 500_000

# Directories to always skip during deep scan
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "coverage",
    ".mypy_cache", ".pytest_cache", "vendor", ".terraform",
}

# Language detection by extension
EXTENSION_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".jsx": "react", ".tsx": "react-ts", ".go": "go",
    ".rs": "rust", ".java": "java", ".kt": "kotlin",
    ".rb": "ruby", ".php": "php", ".c": "c", ".cpp": "cpp",
    ".h": "c", ".hpp": "cpp", ".sh": "shell",
    ".sql": "sql", ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml", ".json": "json", ".xml": "xml",
}


def scan_codebase(root: Path, extra_ignores: Optional[list[str]] = None) -> ScanResult:
    """Scan a codebase and categorize all files."""
    file_filter = FileFilter(root, extra_ignores)
    result = ScanResult(root=root)

    for dirpath, dirnames, filenames in os.walk(root):
        dir_path = Path(dirpath)

        # Skip ignored directories
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not file_filter.is_ignored(dir_path / d)
        ]
        dirnames.sort()

        for filename in sorted(filenames):
            file_path = dir_path / filename

            if file_filter.is_ignored(file_path):
                continue

            if file_path.stat().st_size > MAX_FILE_SIZE:
                continue

            rel = str(file_path.relative_to(root))
            size = file_path.stat().st_size
            ext = file_path.suffix.lower()
            lang = EXTENSION_LANG.get(ext)

            # Check test BEFORE source, since test files are a subset of source
            if file_filter.is_test(file_path):
                category = "test"
                tf = FileInfo(file_path, rel, size, category, lang)
                result.test_files.append(tf)
            elif file_filter.is_source(file_path):
                category = "source"
                sf = FileInfo(file_path, rel, size, category, lang)
                result.source_files.append(sf)
            elif file_filter.is_config(file_path):
                category = "config"
                cf = FileInfo(file_path, rel, size, category, lang)
                result.config_files.append(cf)
            elif file_filter.is_doc(file_path):
                category = "doc"
                df = FileInfo(file_path, rel, size, category, lang)
                result.doc_files.append(df)
            else:
                category = "other"

            result.files.append(FileInfo(file_path, rel, size, category, lang))
            result.total_files += 1

    result.tree = _build_tree(result)
    result.total_source_lines = _count_source_lines(result.source_files)

    return result


def _build_tree(result: ScanResult) -> str:
    """Build an ASCII directory tree of the project structure."""
    tree: dict = {}

    for f in result.files:
        parts = f.relative_path.split(os.sep)
        current = tree
        for part in parts:
            current = current.setdefault(part, {})

    lines: list[str] = []
    _render_tree(tree, "", lines, is_last=True)
    return "\n".join(lines)


def _render_tree(tree: dict, prefix: str, lines: list[str], is_last: bool) -> None:
    items = sorted(tree.items())
    for i, (name, children) in enumerate(items):
        is_final = i == len(items) - 1
        connector = "└── " if is_final else "├── "
        lines.append(f"{prefix}{connector}{name}")
        if children:
            extension = "    " if is_final else "│   "
            _render_tree(children, prefix + extension, lines, is_final)


def _count_source_lines(source_files: list[FileInfo]) -> int:
    """Count total lines across source files."""
    total = 0
    for f in source_files:
        try:
            total += sum(1 for _ in f.path.open("r", errors="ignore"))
        except (OSError, PermissionError):
            continue
    return total
