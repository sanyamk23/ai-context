"""Main context document builder."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, PackageLoader

from ai_context.analyzer.ast_analyzer import AnalysisResult
from ai_context.analyzer.deps import DepsResult
from ai_context.analyzer.patterns import Conventions
from ai_context.analyzer.scanner import ScanResult
from ai_context.generator.token_counter import count_tokens_approx, format_tokens
from ai_context.utils.git import get_languages


TEMPLATE_MAP = {
    "claude": "claude.md.j2",
    "cursor": "cursor.j2",
    "copilot": "copilot.j2",
    "generic": "generic.j2",
}

OUTPUT_MAP = {
    "claude": "CLAUDE.md",
    "cursor": ".cursorrules",
    "copilot": ".github/copilot-instructions.md",
    "generic": "CONTEXT.md",
}


class ContextBuilder:
    """Build an optimized AI context document from codebase analysis."""

    def __init__(
        self,
        scan: ScanResult,
        analysis: AnalysisResult,
        deps: Optional[DepsResult],
        conventions: Conventions,
    ):
        self.scan = scan
        self.analysis = analysis
        self.deps = deps
        self.conventions = conventions

    def build(self, fmt: str = "claude") -> str:
        """Generate the context document in the specified format."""
        template_name = TEMPLATE_MAP.get(fmt)
        if not template_name:
            raise ValueError(f"Unknown format: {fmt}. Available: {list(TEMPLATE_MAP.keys())}")

        env = Environment(
            loader=PackageLoader("ai_context", "generator/templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(template_name)

        context = self._build_context_data()
        return template.render(**context)

    def _build_context_data(self) -> dict:
        """Assemble all data needed for template rendering."""
        # Languages from git
        git_languages = get_languages(self.scan.root)
        if not git_languages:
            # Fallback: count by file extension
            git_languages = {}
            for f in self.scan.source_files:
                lang = f.language or f.path.suffix.lstrip(".")
                if lang:
                    git_languages[lang.title()] = git_languages.get(lang.title(), 0) + 1

        # Dependencies summary
        deps_manager = self.deps.manager if self.deps else None
        core_deps = self._core_dependencies()
        dev_deps_count = len(self.deps.dev_dependencies) if self.deps else 0
        total_deps = (len(self.deps.dependencies) + dev_deps_count) if self.deps else 0

        # Test location
        test_location = None
        if self.scan.test_files:
            test_dirs = set()
            for tf in self.scan.test_files[:5]:
                parts = Path(tf.relative_path).parts
                if len(parts) > 1:
                    test_dirs.add(parts[0])
            if test_dirs:
                test_location = "/".join(sorted(test_dirs))

        return {
            "project_name": self._project_name(),
            "project_description": self._project_description(),
            "languages": git_languages,
            "architecture_overview": self._architecture_overview(),
            "entry_points": self.analysis.entry_points or ["(not detected)"],
            "directory_tree": self._compact_tree(),
            "deps_manager": deps_manager,
            "core_deps": core_deps[:15],  # Top 15 only
            "dev_deps_count": dev_deps_count,
            "total_deps": total_deps,
            "naming_convention": self.analysis.naming_convention,
            "indentation": self.conventions.indentation,
            "quote_style": self.conventions.quote_style,
            "has_type_hints": self.conventions.has_type_hints,
            "has_docstrings": self.conventions.has_docstrings,
            "testing_style": self.conventions.testing_style,
            "test_framework": self.analysis.test_framework,
            "test_count": len(self.scan.test_files),
            "test_location": test_location,
            "patterns": self.analysis.patterns_detected or ["General purpose project"],
            "gotchas": self._detect_gotchas(),
        }

    def _project_name(self) -> str:
        """Extract project name from directory or config."""
        # Try pyproject.toml
        pyproject = self.scan.root / "pyproject.toml"
        if pyproject.is_file():
            try:
                import re
                match = re.search(r'name\s*=\s*["\']([^"\']+)', pyproject.read_text())
                if match:
                    return match.group(1)
            except (OSError, re.error):
                pass

        # Try package.json
        pkg_json = self.scan.root / "package.json"
        if pkg_json.is_file():
            try:
                import json
                data = json.loads(pkg_json.read_text())
                if "name" in data:
                    return data["name"]
            except (json.JSONDecodeError, OSError):
                pass

        return self.scan.root.name

    def _project_description(self) -> str:
        """Extract or infer project description."""
        # Try pyproject.toml
        pyproject = self.scan.root / "pyproject.toml"
        if pyproject.is_file():
            try:
                import re
                content = pyproject.read_text()
                match = re.search(r'description\s*=\s*["\']([^"\']+)', content)
                if match:
                    return match.group(1)
            except (OSError, re.error):
                pass

        # Try package.json
        pkg_json = self.scan.root / "package.json"
        if pkg_json.is_file():
            try:
                import json
                data = json.loads(pkg_json.read_text())
                if "description" in data:
                    return data["description"]
            except (json.JSONDecodeError, OSError):
                pass

        # Try README
        for readme_name in ["README.md", "README.rst", "README.txt"]:
            readme = self.scan.root / readme_name
            if readme.is_file():
                try:
                    lines = readme.read_text(errors="ignore").splitlines()
                    for line in lines[1:10]:  # Skip title
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#") and not stripped.startswith("!"):
                            return stripped[:200]
                except OSError:
                    continue

        return f"A {self.scan.total_files} file project"

    def _architecture_overview(self) -> str:
        """Generate a high-level architecture description."""
        parts = []

        if self.deps and self.deps.manager:
            parts.append(f"Built with {self.deps.manager}.")

        source_count = len(self.scan.source_files)
        test_count = len(self.scan.test_files)

        if source_count > 50:
            parts.append(f"Large codebase ({source_count} source files).")
        elif source_count > 15:
            parts.append(f"Medium codebase ({source_count} source files).")
        else:
            parts.append(f"Small codebase ({source_count} source files).")

        if self.analysis.patterns_detected:
            parts.append(f"Uses {self.analysis.patterns_detected[0].lower()}.")

        if test_count:
            ratio = source_count / max(test_count, 1)
            parts.append(f"Has {test_count} test files ({ratio:.0f}:1 source-to-test ratio).")

        return " ".join(parts) if parts else "General purpose project."

    def _compact_tree(self) -> str:
        """Generate a compact directory tree (top 2 levels only)."""
        if not self.scan.tree:
            return "(empty project)"

        lines = self.scan.tree.splitlines()
        # Keep only first 40 lines for compactness
        if len(lines) > 40:
            return "\n".join(lines[:38]) + f"\n  ... and {len(lines) - 38} more"
        return self.scan.tree

    def _core_dependencies(self) -> list:
        """Get the most important dependencies."""
        if not self.deps:
            return []
        return self.deps.dependencies

    def _detect_gotchas(self) -> list[str]:
        """Detect non-obvious behaviors or potential issues."""
        gotchas = []

        # No tests
        if not self.scan.test_files and len(self.scan.source_files) > 5:
            gotchas.append("No test files detected — be extra careful with changes")

        # Very large files
        large_files = [f for f in self.scan.source_files if f.size > 50_000]
        if large_files:
            names = [f.relative_path for f in large_files[:3]]
            gotchas.append(f"Large files present: {', '.join(names)}")

        # No entry points found
        if not self.analysis.entry_points:
            gotchas.append("No clear entry points detected")

        # Mixed languages
        if len(self.scan.source_files) > 0:
            langs = set(f.language for f in self.scan.source_files if f.language)
            if len(langs) > 2:
                gotchas.append(f"Multi-language project ({', '.join(sorted(langs))})")

        # Config-heavy
        config_ratio = len(self.scan.config_files) / max(len(self.scan.source_files), 1)
        if config_ratio > 0.3:
            gotchas.append("Heavy configuration — check config files before changes")

        return gotchas


def generate_context(
    scan: ScanResult,
    analysis: AnalysisResult,
    deps: Optional[DepsResult],
    conventions: Conventions,
    fmt: str = "claude",
) -> tuple[str, dict]:
    """Generate context document and stats.

    Returns (document_text, stats_dict).
    """
    builder = ContextBuilder(scan, analysis, deps, conventions)
    document = builder.build(fmt)

    # Calculate stats
    context_tokens = count_tokens_approx(document)

    # Estimate what reading all source files would cost
    total_source_tokens = 0
    for f in scan.source_files:
        try:
            content = f.path.read_text(errors="ignore")
            total_source_tokens += count_tokens_approx(content)
        except (OSError, PermissionError):
            continue

    stats = {
        "context_tokens": context_tokens,
        "source_tokens": total_source_tokens,
        "tokens_saved": total_source_tokens - context_tokens,
        "savings_percent": round((1 - context_tokens / max(total_source_tokens, 1)) * 100, 1),
        "file_count": scan.total_files,
        "format": fmt,
        "output_file": OUTPUT_MAP.get(fmt, "CONTEXT.md"),
    }

    return document, stats
