# Hacker News — Show HN Post

## Title (copy this):
Show HN: ai-context – Stop re-explaining your codebase to AI every session (saves 95% on context tokens)

## Body (copy this):

Hey HN,

Every time I start a Claude Code / Cursor / Copilot session, the AI wastes thousands of tokens reading my codebase to understand what it does. That's real money every session, and for a team it adds up fast.

I built ai-context [0] to fix this. It scans your repo once and generates a compact context document (~300 tokens) that tells the AI everything it needs — architecture, entry points, conventions, dependencies, patterns, gotchas.

The generated file (CLAUDE.md, .cursorrules, etc.) goes in your repo and is automatically used by the AI tool.

What it does:
- Scans directory structure, respecting .gitignore
- AST-level code analysis (Python, JS, TS, Go, Rust, etc.)
- Detects naming conventions, test frameworks, patterns
- Generates tool-specific output for Claude Code, Cursor, Copilot
- Shows exact cost savings per provider

Install: `pip install ai-context`
Use: `ai-context generate`

Tested on itself: 295 context tokens vs 6,900 source tokens = 95.7% reduction.

Curious what HN thinks — especially about what else could reduce AI coding costs.

[0] https://github.com/sanyamk23/ai-context
