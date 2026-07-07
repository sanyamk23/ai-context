"""AST-based code analysis for extracting patterns and structure."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from contextly.analyzer.scanner import FileInfo


@dataclass
class ModuleInfo:
    path: str
    language: str
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    docstring: Optional[str] = None
    lines: int = 0


@dataclass
class AnalysisResult:
    modules: list[ModuleInfo] = field(default_factory=list)
    entry_points: list[str] = field(default_factory=list)
    main_classes: list[str] = field(default_factory=list)
    key_functions: list[str] = field(default_factory=list)
    naming_convention: str = "unknown"
    test_framework: Optional[str] = None
    avg_function_length: float = 0.0
    avg_class_length: float = 0.0
    total_classes: int = 0
    total_functions: int = 0
    patterns_detected: list[str] = field(default_factory=list)


def analyze_codebase(source_files: list[FileInfo], max_files: int = 100) -> AnalysisResult:
    """Analyze source files and extract code patterns."""
    result = AnalysisResult()

    # Prioritize: entry points first, then configs, then random samples
    prioritized = _prioritize_files(source_files)[:max_files]

    all_functions: list[int] = []
    all_class_lengths: list[int] = []

    for fi in prioritized:
        try:
            content = fi.path.read_text(errors="ignore")
        except (OSError, PermissionError):
            continue

        lang = fi.language or "unknown"

        if lang == "python":
            module = _analyze_python(fi.relative_path, content)
        elif lang in ("javascript", "typescript", "react", "react-ts"):
            module = _analyze_js_ts(fi.relative_path, content, lang)
        else:
            module = ModuleInfo(path=fi.relative_path, language=lang, lines=len(content.splitlines()))

        result.modules.append(module)
        result.total_classes += len(module.classes)
        result.total_functions += len(module.functions)
        all_class_lengths.extend([0] * len(module.classes))  # placeholder
        all_functions.extend([0] * len(module.functions))

        if module.docstring:
            result.entry_points.append(fi.relative_path)

    # Detect naming conventions
    result.naming_convention = _detect_naming(result.modules)

    # Detect test framework
    result.test_framework = _detect_test_framework(result.modules)

    # Detect patterns
    result.patterns_detected = _detect_patterns(result.modules)

    # Identify main entry points
    result.entry_points = _find_entry_points(source_files, result.modules)

    return result


def _prioritize_files(files: list[FileInfo]) -> list[FileInfo]:
    """Prioritize files: entry points > configs > others."""
    score_map = {
        "main.py": 10, "app.py": 10, "cli.py": 9, "__main__.py": 10,
        "index.js": 9, "index.ts": 9, "main.go": 10, "main.rs": 10,
        "__init__.py": 5, "server.py": 9, "api.py": 8,
    }
    return sorted(files, key=lambda f: score_map.get(f.path.name, 1), reverse=True)


def _analyze_python(path: str, content: str) -> ModuleInfo:
    """Analyze a Python file using the ast module."""
    module = ModuleInfo(path=path, language="python", lines=len(content.splitlines()))

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return module

    # Docstring
    if (docstring := ast.get_docstring(tree)):
        module.docstring = docstring[:200]

    # First pass: collect class methods
    class_methods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    class_methods.add(f"{node.name}.{item.name}")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            module.classes.append(node.name)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if f"{node.name}.{item.name}" not in module.functions:
                        module.functions.append(f"{node.name}.{item.name}")
            for dec in node.decorator_list:
                name = _get_decorator_name(dec)
                if name:
                    module.decorators.append(name)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Only add if not already added as a class method
            if node.name not in class_methods and f"{node.name}" not in [
                f.split(".")[-1] for f in module.functions
            ]:
                module.functions.append(node.name)

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module.imports.append(alias.name)
            else:
                if node.module:
                    module.imports.append(node.module)

    return module


def _analyze_js_ts(path: str, content: str, lang: str) -> ModuleInfo:
    """Analyze a JavaScript/TypeScript file using regex patterns."""
    module = ModuleInfo(path=path, language=lang, lines=len(content.splitlines()))

    # Classes
    module.classes = re.findall(r"(?:export\s+)?class\s+(\w+)", content)

    # Functions
    module.functions = re.findall(
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)",
        content,
    )

    # Arrow functions assigned to const/let/var
    arrow_funcs = re.findall(
        r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(",
        content,
    )
    module.functions.extend(arrow_funcs)

    # Imports
    module.imports = re.findall(
        r"""(?:import|from)\s+['"]([^'"]+)['"]""",
        content,
    )

    # JSDoc: first docblock
    doc_match = re.search(r"/\*\*\s*(.*?)\s*\*/", content, re.DOTALL)
    if doc_match:
        module.docstring = doc_match.group(1).strip()[:200]

    return module


def _get_decorator_name(node) -> Optional[str]:
    """Extract decorator name from AST node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _get_decorator_name(node.func)
    return None


def _detect_naming(modules: list[ModuleInfo]) -> str:
    """Detect predominant naming convention."""
    snake = camel = pascal = 0

    for m in modules:
        for func in m.functions:
            if "_" in func and func[0].islower():
                snake += 1
            elif func[0].isupper():
                pascal += 1
            elif any(c.isupper() for c in func[1:]):
                camel += 1

    for cls in m.classes:
        if cls[0].isupper():
            pascal += 1

    total = snake + camel + pascal
    if total == 0:
        return "unknown"

    winner = max([("snake_case", snake), ("camelCase", camel), ("PascalCase", pascal)], key=lambda x: x[1])
    return winner[0]


def _detect_test_framework(modules: list[ModuleInfo]) -> Optional[str]:
    """Detect which test framework is used."""
    all_imports = [imp for m in modules for imp in m.imports]
    import_str = " ".join(all_imports)

    if "pytest" in import_str:
        return "pytest"
    if "unittest" in import_str:
        return "unittest"
    if "jest" in import_str or "describe" in import_str:
        return "jest"
    if "vitest" in import_str:
        return "vitest"
    return None


def _detect_patterns(modules: list[ModuleInfo]) -> list[str]:
    """Detect common architectural patterns."""
    patterns = []
    all_imports = " ".join(imp for m in modules for imp in m.imports)
    all_classes = [c for m in modules for c in m.classes]
    all_decorators = [d for m in modules for d in m.decorators]

    # Web framework patterns
    if "flask" in all_imports.lower():
        patterns.append("Flask web application")
    if "django" in all_imports.lower():
        patterns.append("Django web application")
    if "fastapi" in all_imports.lower():
        patterns.append("FastAPI web application")
    if "express" in all_imports.lower():
        patterns.append("Express.js web application")
    if "next" in all_imports.lower():
        patterns.append("Next.js application")

    # Data/ML patterns
    if "pandas" in all_imports or "numpy" in all_imports:
        patterns.append("Data processing pipeline")
    if "torch" in all_imports or "tensorflow" in all_imports:
        patterns.append("Machine learning project")

    # Architecture patterns
    if any("Repository" in c or "Service" in c or "Controller" in c for c in all_classes):
        patterns.append("Service/Repository pattern")
    if any("Middleware" in c for c in all_classes):
        patterns.append("Middleware pattern")
    if any("Schema" in c for c in all_classes):
        patterns.append("Schema validation")
    if any("Serializer" in c for c in all_classes):
        patterns.append("Serialization layer")

    # Testing
    if any("mock" in d.lower() or "patch" in d.lower() for d in all_decorators):
        patterns.append("Mock-based testing")

    return patterns


def _find_entry_points(
    source_files: list[FileInfo], modules: list[ModuleInfo]
) -> list[str]:
    """Identify likely entry points in the codebase."""
    entry_point_names = {
        "main.py", "app.py", "cli.py", "__main__.py", "server.py",
        "manage.py", "wsgi.py", "asgi.py",
        "index.js", "index.ts", "main.js", "main.ts",
        "main.go", "main.rs",
    }

    entry_points = []
    for fi in source_files:
        if fi.path.name in entry_point_names:
            entry_points.append(fi.relative_path)

    # Also check for scripts in pyproject.toml / package.json (handled by deps.py)
    return entry_points
