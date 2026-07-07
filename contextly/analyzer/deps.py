"""Dependency analysis from various package managers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DependencyInfo:
    name: str
    version: str
    is_dev: bool = False
    source: str = ""  # e.g. "npm", "pypi", "cargo"


@dataclass
class DepsResult:
    manager: str  # e.g. "npm", "pip", "cargo", "go"
    dependencies: list[DependencyInfo] = field(default_factory=list)
    dev_dependencies: list[DependencyInfo] = field(default_factory=list)
    python_version: Optional[str] = None
    node_version: Optional[str] = None
    go_version: Optional[str] = None
    rust_edition: Optional[str] = None
    scripts: dict[str, str] = field(default_factory=dict)


def analyze_dependencies(root: Path) -> Optional[DepsResult]:
    """Detect package manager and analyze dependencies."""
    # Try each package manager in order of likelihood
    for detector in [_detect_npm, _detect_pip, _detect_cargo, _detect_go, _detect_gem]:
        result = detector(root)
        if result is not None:
            return result
    return None


def _detect_npm(root: Path) -> Optional[DepsResult]:
    """Analyze package.json."""
    pkg_json = root / "package.json"
    if not pkg_json.is_file():
        return None

    try:
        data = json.loads(pkg_json.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    result = DepsResult(manager="npm")

    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    engines = data.get("engines", {})
    scripts = data.get("scripts", {})

    for name, ver in deps.items():
        result.dependencies.append(DependencyInfo(name, ver, source="npm"))
    for name, ver in dev_deps.items():
        result.dev_dependencies.append(DependencyInfo(name, ver, is_dev=True, source="npm"))

    if "node" in engines:
        result.node_version = engines["node"]
    result.scripts = {k: v for k, v in scripts.items() if isinstance(v, str)}

    return result


def _detect_pip(root: Path) -> Optional[DepsResult]:
    """Analyze pyproject.toml, requirements.txt, or setup.cfg."""
    # Try pyproject.toml first
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        return _parse_pyproject(pyproject)

    # Try requirements.txt
    req_files = list(root.glob("requirements*.txt"))
    if req_files:
        return _parse_requirements(root, req_files)

    return None


def _parse_pyproject(path: Path) -> Optional[DepsResult]:
    """Parse dependencies from pyproject.toml (basic parser, no tomllib)."""
    content = path.read_text()
    result = DepsResult(manager="pip")

    # Basic TOML parsing for [project.dependencies]
    in_deps = False
    for line in content.splitlines():
        stripped = line.strip()

        if stripped == "[project]":
            continue
        if stripped.startswith("[project.optional-dependencies]"):
            in_deps = False
            continue
        if stripped == "dependencies = [":
            in_deps = True
            continue
        if stripped.startswith("["):
            in_deps = False
            continue

        if in_deps and stripped.startswith('"'):
            dep_str = stripped.strip('",')
            name = re.split(r"[><=!~]", dep_str)[0].strip()
            version = dep_str[len(name):].strip() if len(dep_str) > len(name) else "*"
            result.dependencies.append(DependencyInfo(name, version, source="pypi"))

    # Check for requires-python
    py_match = re.search(r'requires-python\s*=\s*"[^"]*?(>=?[\d.]+)', content)
    if py_match:
        result.python_version = py_match.group(1)

    return result


def _parse_requirements(root: Path, req_files: list) -> Optional[DepsResult]:
    """Parse requirements*.txt files."""
    result = DepsResult(manager="pip")

    for rf in req_files:
        is_dev = "dev" in rf.stem.lower()
        try:
            for line in rf.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                name = re.split(r"[><=!~\[]", line)[0].strip()
                version = line[len(name):].strip() if len(line) > len(name) else "*"
                result.dependencies.append(
                    DependencyInfo(name, version, is_dev=is_dev, source="pypi")
                )
        except OSError:
            continue

    return result


def _detect_cargo(root: Path) -> Optional[DepsResult]:
    """Analyze Cargo.toml."""
    cargo_toml = root / "Cargo.toml"
    if not cargo_toml.is_file():
        return None

    content = cargo_toml.read_text()
    result = DepsResult(manager="cargo")

    # Extract edition
    ed_match = re.search(r'edition\s*=\s*"(\d{4})"', content)
    if ed_match:
        result.rust_edition = ed_match.group(1)

    # Parse [dependencies]
    in_deps = False
    in_dev = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[dependencies]":
            in_deps, in_dev = True, False
            continue
        if stripped == "[dev-dependencies]":
            in_deps, in_dev = False, True
            continue
        if stripped.startswith("["):
            in_deps, in_dev = False, False
            continue

        if (in_deps or in_dev) and "=" in stripped:
            parts = stripped.split("=", 1)
            name = parts[0].strip()
            ver = parts[1].strip().strip('"')
            result.dependencies.append(
                DependencyInfo(name, ver, is_dev=in_dev, source="crates.io")
            )

    return result


def _detect_go(root: Path) -> Optional[DepsResult]:
    """Analyze go.mod."""
    go_mod = root / "go.mod"
    if not go_mod.is_file():
        return None

    content = go_mod.read_text()
    result = DepsResult(manager="go")

    # Go version
    go_ver = re.search(r"go\s+([\d.]+)", content)
    if go_ver:
        result.go_version = go_ver.group(1)

    # Parse require blocks
    in_require = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("require"):
            in_require = True
            if "(" not in stripped:
                # Single require
                parts = stripped.split()
                if len(parts) >= 3:
                    result.dependencies.append(
                        DependencyInfo(parts[1], parts[2], source="go")
                    )
                in_require = False
            continue
        if in_require and stripped == ")":
            in_require = False
            continue
        if in_require:
            parts = stripped.split()
            if len(parts) >= 2:
                result.dependencies.append(
                    DependencyInfo(parts[0], parts[1], source="go")
                )

    return result


def _detect_gem(root: Path) -> Optional[DepsResult]:
    """Analyze Gemfile."""
    gemfile = root / "Gemfile"
    if not gemfile.is_file():
        return None

    content = gemfile.read_text()
    result = DepsResult(manager="ruby")

    in_group = False
    is_dev = False
    for line in content.splitlines():
        stripped = line.strip()
        if "group" in stripped and ":" in stripped:
            in_group = True
            is_dev = "development" in stripped or "test" in stripped
            continue
        if in_group and stripped == "end":
            in_group = False
            is_dev = False
            continue
        if stripped.startswith("gem "):
            match = re.match(r'gem\s+["\'](\w+)["\'](?:,\s*["\']([^"\']+)', stripped)
            if match:
                result.dependencies.append(
                    DependencyInfo(match.group(1), match.group(2) or "*", is_dev=is_dev, source="rubygems")
                )

    return result
