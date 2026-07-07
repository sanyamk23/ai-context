"""Git helper utilities."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


def run_git(args: list[str], cwd: Path) -> Optional[str]:
    """Run a git command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_repo_root(path: Path) -> Optional[Path]:
    """Find the git repo root containing the given path."""
    output = run_git(["rev-parse", "--show-toplevel"], cwd=path)
    if output:
        return Path(output)
    return None


def get_recent_commits(path: Path, count: int = 10) -> list[str]:
    """Get recent commit messages."""
    output = run_git(
        ["log", f"--oneline", f"-{count}", "--format=%s"],
        cwd=path,
    )
    if output:
        return output.splitlines()
    return []


def get_languages(path: Path) -> dict[str, int]:
    """Get language breakdown from git ls-files."""
    output = run_git(["ls-files"], cwd=path)
    if not output:
        return {}

    lang_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".jsx": "React", ".tsx": "React TS", ".go": "Go",
        ".rs": "Rust", ".java": "Java", ".rb": "Ruby",
        ".php": "PHP", ".c": "C", ".cpp": "C++",
        ".h": "C Header", ".hpp": "C++ Header",
        ".sh": "Shell", ".sql": "SQL",
    }

    counts: dict[str, int] = {}
    for line in output.splitlines():
        ext = Path(line).suffix.lower()
        lang = lang_map.get(ext)
        if lang:
            counts[lang] = counts.get(lang, 0) + 1

    return counts
