<div align="center">

# ai-context

### Stop re-explaining your codebase to AI. Every. Single. Time.

[![PyPI version](https://img.shields.io/pypi/v/ai-context.svg)](https://pypi.org/project/ai-context/)
[![Python](https://img.shields.io/pypi/pyversions/ai-context.svg)](https://pypi.org/project/ai-context/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Installation](#installation) • [Quick Start](#quick-start) • [How It Works](#how-it-works) • [Supported Tools](#supported-tools) • [Cost Savings](#cost-savings)

</div>

---

## The Problem

Every time you start a new Claude Code, Cursor, or Copilot session, the AI wastes **thousands of tokens** reading your codebase to understand:
- What the project does
- The architecture and directory structure
- Coding conventions and patterns
- Dependencies and how they're used
- Entry points and key files

**That's $0.03–$0.15+ per session in wasted tokens.** For a team of 10 developers, that adds up to **$100–500/month** in pure waste.

## The Solution

`ai-context` analyzes your codebase **once** and generates a compact, optimized context document (~800–1500 tokens) that tells the AI everything it needs to know — without reading a single source file.

```bash
# Install
pip install ai-context

# Generate context for Claude Code
ai-context generate

# Use with Cursor
ai-context generate --format cursor

# Use with GitHub Copilot
ai-context generate --format copilot
```

The generated file goes into your repo. Every AI session starts with full context instantly.

---

## Quick Start

### 1. Install

```bash
pip install ai-context
```

### 2. Generate

```bash
cd your-project
ai-context generate
```

### 3. Use

The generated `CLAUDE.md` (or `.cursorrules`, `.github/copilot-instructions.md`) is automatically picked up by your AI tool. That's it.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     ai-context generate                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SCAN ────────────────────────────────────────────────    │
│     Walk directory tree, respecting .gitignore               │
│     Categorize: source, config, test, docs                   │
│                                                              │
│  2. ANALYZE ─────────────────────────────────────────────    │
│     Extract code patterns (Python AST, JS regex)             │
│     Detect naming conventions, test framework                │
│     Identify entry points, architectural patterns            │
│                                                              │
│  3. GENERATE ────────────────────────────────────────────    │
│     Assemble into optimized markdown document                │
│     Prioritize: architecture > patterns > conventions        │
│     Token-budget aware: dense, no fluff                      │
│                                                              │
│  Output: CLAUDE.md / .cursorrules / CONTEXT.md              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### What's in the context document?

| Section | What it tells the AI |
|---|---|
| **Tech Stack** | Languages, frameworks, runtime versions |
| **Architecture** | Project size, patterns, structure |
| **Entry Points** | Where code execution starts |
| **Dependencies** | Core and dev dependencies with versions |
| **Conventions** | Naming, indentation, quotes, type hints |
| **Patterns** | Design patterns (MVC, DI, middleware, etc.) |
| **Gotchas** | Non-obvious things to watch out for |
| **Testing** | Framework, location, test-to-source ratio |

---

## Supported Tools

| Tool | Output File | Command |
|---|---|---|
| **Claude Code** | `CLAUDE.md` | `ai-context generate` |
| **Cursor** | `.cursorrules` | `ai-context generate --format cursor` |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `ai-context generate --format copilot` |
| **Any AI tool** | `CONTEXT.md` | `ai-context generate --format generic` |

---

## Cost Savings

Running `ai-context cost` shows exactly how much you save:

```
┌─────────────────────────────────────────────────────────────┐
│                  Cost Savings Estimate                        │
├─────────────────────────────────────────────────────────────┤
│ Tokens to explain codebase (without context): 12.4K          │
│ Tokens with ai-context:                        1.2K          │
│ Tokens saved per session:                     11.2K (90%)    │
├──────────────────────┬──────────┬───────────┬───────────────┤
│ Provider             │ Without  │ With      │ Monthly Saved │
├──────────────────────┼──────────┼───────────┼───────────────┤
│ Claude Sonnet 4      │ $0.0372  │ $0.0036   │ $3.36         │
│ GPT-4o               │ $0.0310  │ $0.0030   │ $2.80         │
│ Claude Opus 4        │ $0.1860  │ $0.0180   │ $16.80        │
│ Gemini 2.5 Pro       │ $0.0155  │ $0.0015   │ $1.40         │
└──────────────────────┴──────────┴───────────┴───────────────┘
```

### Team savings (10 devs, 50 sessions/month)

| Provider | Monthly Savings |
|---|---|
| Claude Sonnet 4 | **$168/mo** |
| Claude Opus 4 | **$840/mo** |
| GPT-4o | **$140/mo** |

---

## Commands

```bash
# Generate context (default: CLAUDE.md)
ai-context generate

# Generate for a specific tool
ai-context generate --format cursor
ai-context generate --format copilot
ai-context generate --format generic

# Custom output path
ai-context generate -o custom-context.md

# Analyze codebase (detailed report)
ai-context analyze
ai-context analyze --json

# Estimate cost savings
ai-context cost
ai-context cost --team  # Show team-wide estimates

# Check freshness (for CI)
ai-context check
```

---

## CI Integration

Add to your GitHub Actions to keep context fresh:

```yaml
# .github/workflows/ai-context.yml
name: AI Context Check
on:
  push:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ai-context
      - run: ai-context check
```

---

## Example Output

<details>
<summary>Click to see generated CLAUDE.md</summary>

```markdown
# my-api

A REST API for managing user accounts and authentication.

## Tech Stack
- **Python** (15 files)
- **TypeScript** (8 files)

## Architecture
Built with pip. Medium codebase (15 source files). Uses FastAPI web application.

## Key Entry Points
- `app/main.py`
- `cli.py`

## Project Structure
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   └── services/
├── tests/
├── pyproject.toml
└── README.md

## Dependencies
**pip** — 12 dependencies (3 dev)

### Core Dependencies
- `fastapi` >=0.100.0
- `uvicorn` >=0.20.0
- `sqlalchemy` >=2.0

## Code Conventions
- **Naming:** snake_case
- **Indentation:** 4 spaces
- **Quote style:** double
- **Type hints:** Yes
- **Docstrings:** Yes

## Patterns
- FastAPI web application
- Service/Repository pattern

## Testing
Framework: pytest
Test files: 12 files
Location: tests
```

</details>

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/your-username/ai-context.git
cd ai-context
pip install -e ".[dev]"
pytest
```

### Roadmap

- [ ] Incremental context updates (`--update` with diff-based merging)
- [ ] Language-specific deep analysis (Go, Rust, Java)
- [ ] VS Code extension
- [ ] GitHub Action for auto-updating context on push
- [ ] Team context sharing via registry
- [ ] Support for monorepo workspaces
- [ ] Context freshness scoring

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Stop wasting tokens. Start generating context.**

```bash
pip install ai-context
```

</div>
