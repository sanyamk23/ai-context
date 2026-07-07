# Reddit — r/programming Post

## Title:
I built ai-context: a CLI that generates optimized context for AI coding tools, saving 95% on context tokens

## Body:

**The problem:** Every time you start a Claude Code, Cursor, or Copilot session, the AI wastes thousands of tokens reading your codebase to understand the architecture, conventions, and patterns. For a team of 10 developers, that's hundreds of dollars per month in pure waste.

**What ai-context does:**

1. Scans your codebase (respecting .gitignore)
2. Analyzes code patterns via AST (Python, JS, TS, Go, Rust...)
3. Detects conventions, test frameworks, dependencies
4. Generates a compact (~300 token) context document

**Supported tools:**
- `ai-context generate` → CLAUDE.md (for Claude Code)
- `ai-context generate --format cursor` → .cursorrules
- `ai-context generate --format copilot` → .github/copilot-instructions.md

**Other features:**
- `ai-context cost` — shows exact $ savings per AI provider
- `ai-context analyze` — detailed codebase analysis
- `ai-context check` — CI integration to verify context freshness

**Results on a real project:**
- Without context: ~6,900 tokens to explain codebase
- With ai-context: ~295 tokens
- **95.7% token reduction**

GitHub: https://github.com/sanyamk23/ai-context

Would appreciate feedback on:
1. What other AI coding cost problems should this solve?
2. Missing language support?
3. Any edge cases I'm missing?
