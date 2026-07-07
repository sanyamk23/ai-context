# Twitter/X Launch Thread

## Tweet 1 (hook):
Your AI coding tool is reading your ENTIRE codebase every session.

That's 5,000-25,000 tokens of pure waste — every. single. time.

I built contextly to fix this:
`pip install contextly`

One scan. One file. 98% fewer tokens. Same quality.

🧵

## Tweet 2 (problem):
Here's what happens every time you start a Claude Code session:

1. AI reads your config files
2. AI reads your main modules
3. AI reads your tests
4. AI reads your dependencies
5. AI finally understands your project
6. You ask your question

Steps 1-5: $0.03-0.30 of tokens doing nothing useful.

## Tweet 3 (solution):
contextly analyzes your codebase ONCE and generates a ~300 token context file:

• Architecture overview
• Entry points
• Code conventions (naming, style)
• Dependencies with versions
• Design patterns (FastAPI, Express, etc.)
• Common gotchas

The file goes in your repo. Every AI session starts instantly.

## Tweet 4 (demo):
```bash
pip install contextly
cd your-project
contextly generate
```

Output on a real project:
- Context tokens: 342
- Source tokens it replaces: 24,100
- Reduction: 98.6%

Run `contextly cost` to see exact $ savings per provider.

## Tweet 5 (multi-tool):
Works with everything:
• Claude Code → CLAUDE.md
• Cursor → .cursorrules
• GitHub Copilot → .github/copilot-instructions.md
• Any AI tool → CONTEXT.md

Also detects: naming conventions, test frameworks, dependencies, patterns, gotchas.

## Tweet 6 (CTA):
Open source. MIT licensed. 30/30 tests passing.

⭐ https://github.com/sanyamk23/contextly

What other AI coding cost problems should I tackle next?
