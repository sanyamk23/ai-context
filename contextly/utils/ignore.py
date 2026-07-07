"""File filtering respecting .gitignore patterns."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pathspec


# Patterns that should always be ignored
DEFAULT_IGNORES = [
    # Python
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.egg-info",
    ".mypy_cache",
    ".pytest_cache",
    "venv",
    ".venv",
    # Node
    "node_modules",
    ".npm",
    # Build artifacts
    "dist",
    "build",
    ".next",
    ".nuxt",
    # IDE
    ".vscode",
    ".idea",
    "*.swp",
    # Git
    ".git",
    # OS
    ".DS_Store",
    "Thumbs.db",
    # AI context (avoid recursion)
    "CLAUDE.md",
    ".cursorrules",
]

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    ".zip", ".tar", ".gz", ".bz2", ".rar", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".woff", ".woff2", ".ttf", ".eot",
    ".exe", ".dll", ".so", ".dylib",
    ".pyc", ".pyo", ".class",
    ".lock",
}

# Source file extensions by language
SOURCE_EXTENSIONS = {
    # Python
    ".py",
    # JavaScript/TypeScript
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    # Go
    ".go",
    # Rust
    ".rs",
    # Java
    ".java", ".kt", ".scala",
    # C/C++
    ".c", ".cpp", ".h", ".hpp",
    # Ruby
    ".rb",
    # PHP
    ".php",
    # Shell
    ".sh", ".bash", ".zsh",
}

CONFIG_FILENAMES = {
    "package.json", "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
    "Cargo.toml", "go.mod", "go.sum", "Gemfile", "composer.json",
    "tsconfig.json", "jsconfig.json", ".eslintrc", ".prettierrc",
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".env.example", "Procfile", "vercel.json", "netlify.toml",
}

TEST_PATTERNS = {"test_", "_test.", ".test.", "tests/", "test/", "__tests__/"}

DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}
DOC_FOLDERS = {"docs/", "doc/", "documentation/"}


class FileFilter:
    """Filter files based on .gitignore rules and custom patterns."""

    def __init__(self, root: Path, extra_ignores: Optional[list[str]] = None):
        self.root = root
        self._specs: list[pathspec.PathSpec] = []

        # Load .gitignore files
        self._load_gitignore(root)

        # Add default ignores
        gitignore_lines = list(DEFAULT_IGNORES)
        if extra_ignores:
            gitignore_lines.extend(extra_ignores)
        self._specs.append(pathspec.PathSpec.from_lines("gitignore", gitignore_lines))

    def _load_gitignore(self, directory: Path) -> None:
        """Walk up and load .gitignore files."""
        gitignore_files = []
        current = directory
        while current != current.parent:
            gi = current / ".gitignore"
            if gi.is_file():
                gitignore_files.append(gi)
            current = current.parent

        for gi_file in reversed(gitignore_files):
            patterns = gi_file.read_text().splitlines()
            self._specs.append(pathspec.PathSpec.from_lines("gitignore", patterns))

    def is_ignored(self, path: Path) -> bool:
        """Check if a file/directory should be ignored."""
        try:
            rel = path.relative_to(self.root)
        except ValueError:
            return True

        rel_str = str(rel)

        # Check binary extensions
        if path.suffix.lower() in BINARY_EXTENSIONS:
            return True

        # Check gitignore patterns
        for spec in self._specs:
            if spec.match_file(rel_str):
                return True

        return False

    def is_source(self, path: Path) -> bool:
        """Check if a file is a source code file."""
        if path.suffix.lower() in SOURCE_EXTENSIONS:
            return True
        if path.name in {"Makefile", "Dockerfile", "Justfile"}:
            return True
        return False

    def is_config(self, path: Path) -> bool:
        """Check if a file is a config file."""
        return path.name in CONFIG_FILENAMES

    def is_test(self, path: Path) -> bool:
        """Check if a file is a test file."""
        try:
            rel = str(path.relative_to(self.root))
        except ValueError:
            rel = str(path)
        # Check both relative path and parent directory names
        if any(p in rel for p in TEST_PATTERNS):
            return True
        # Also check if any ancestor directory name looks like a test dir
        for part in path.parts:
            if part in ("tests", "test", "__tests__"):
                return True
        return False

    def is_doc(self, path: Path) -> bool:
        """Check if a file is a documentation file."""
        return path.suffix.lower() in DOC_EXTENSIONS
