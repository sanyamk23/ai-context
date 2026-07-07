# Hacker News — Show HN Post

## Title (copy this):
Show HN: contextly – Your AI tools are reading your entire codebase every session. Stop that.

## Body (copy this):

Hey HN,

I noticed something annoying: every time I start a Claude Code / Cursor / Copilot session, the AI wastes thousands of tokens reading my entire codebase to understand what it does. That's real money every session — $0.02-0.30 per session just on context loading. For a team of 10 devs, that adds up to hundreds per month in pure waste.

I built contextly [0] to fix this. It scans your repo once and generates a compact context document (~300 tokens) that tells the AI everything it needs — architecture, entry points, conventions, dependencies, patterns, gotchas.

```bash
pip install contextly
cd your-project
contextly generate
```

The generated file (CLAUDE.md, .cursorrules, etc.) goes in your repo and is automatically used by the AI tool.

Key features:
- AST-level code analysis (Python, JS, TS, Go, Rust...)
- Detects naming conventions, test frameworks, patterns
- Tool-specific output for Claude Code, Cursor, Copilot
- `contextly cost` shows exact $ savings per provider
- CI integration via `contextly check`

Tested on itself: 342 context tokens vs 24,100 source tokens = 98.6% reduction.

Curious what HN thinks — especially about what else could reduce AI coding costs.

[0] https://github.com/sanyamk23/contextly
