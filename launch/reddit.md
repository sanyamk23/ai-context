# Reddit — r/programming Post

## Title:
I built contextly: your AI tools are reading your entire codebase every session. That's expensive. Here's a fix.

## Body:

**The problem:** Every time you start a Claude Code, Cursor, or Copilot session, the AI wastes 5,000-25,000 tokens reading your codebase to understand the architecture, conventions, and patterns. For a solo developer, that's $15-30/month. For a team of 10, it's $300-800/month — just for context loading.

**What contextly does:**

1. Scans your codebase (respecting .gitignore)
2. Analyzes code patterns via AST (Python, JS, TS, Go, Rust...)
3. Detects conventions, test frameworks, dependencies, patterns
4. Generates a compact (~300 token) context document

**Supported tools:**
- `contextly generate` → CLAUDE.md (for Claude Code)
- `contextly generate --format cursor` → .cursorrules
- `contextly generate --format copilot` → .github/copilot-instructions.md

**What gets detected:**
- Tech stack and architecture patterns (MVC, Service/Repository, etc.)
- Code conventions (naming, indentation, quotes, type hints)
- Dependencies with versions (pyproject.toml, package.json, Cargo.toml, go.mod)
- Entry points and project structure
- Test framework and location
- Gotchas (missing tests, large files, multi-language complexity)

**Results on a real project:**
- Without context: ~24,100 tokens to explain codebase
- With contextly: ~342 tokens
- **98.6% token reduction**

**Other features:**
- `contextly cost` — shows exact $ savings per AI provider
- `contextly analyze` — detailed codebase analysis
- `contextly check` — CI integration to verify context freshness
- GitHub Action included for auto-updating context on push

GitHub: https://github.com/sanyamk23/contextly

Would appreciate feedback on:
1. What other AI coding cost problems should this solve?
2. Missing language support?
3. Any edge cases I'm missing?
