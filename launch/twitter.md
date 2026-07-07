# Twitter/X Launch Thread

## Tweet 1 (hook):
I was wasting $50+/month on Claude Code tokens just re-explaining my codebase every session.

So I built ai-context — it scans your repo once and generates a ~300 token context file that tells the AI everything it needs.

95% fewer context tokens. `pip install ai-context`

🧵

## Tweet 2 (problem):
The problem every AI coder faces:

Every new Claude Code / Cursor / Copilot session starts with the AI reading 30+ files to understand your project.

That's 5,000-15,000 tokens of pure waste — every. single. time.

For a team of 10, that's $200-500/month in tokens doing nothing.

## Tweet 3 (solution):
ai-context analyzes your codebase ONCE and generates a compact context document:

• Architecture overview
• Entry points
• Code conventions (naming, style)
• Dependencies
• Design patterns
• Common gotchas

The file goes in your repo. Every AI session starts with full context instantly.

## Tweet 4 (demo):
How it works:

```bash
pip install ai-context
cd your-project
ai-context generate
```

That's it. Generates CLAUDE.md (or .cursorrules, or Copilot instructions).

On a real project: 295 context tokens vs 6,900 source tokens.

95.7% reduction. Same quality.

## Tweet 5 (multi-tool):
Works with:
• Claude Code → generates CLAUDE.md
• Cursor → generates .cursorrules
• GitHub Copilot → generates .github/copilot-instructions.md
• Any AI tool → generic CONTEXT.md

Also includes `ai-context cost` to show exact $ savings per provider.

## Tweet 6 (CTA):
Open source. MIT licensed. 30/30 tests passing.

Would love your feedback:
⭐ https://github.com/sanyamk23/ai-context

What other AI coding cost problems should I tackle next?
