# Dev.to Article

## Title:
Your AI Tools Are Reading Your Entire Codebase Every Session. That's Expensive.

## Tags:
python, ai, productivity, open-source

## Body:

If you use Claude Code, Cursor, or Copilot, you've probably noticed something annoying: every new session starts with the AI spending thousands of tokens reading your entire codebase.

For me, that was ~24,000 tokens of waste — every single session. At Claude Sonnet 4 pricing, that's $0.07 per session just for the AI to "remember" what my project is. Multiply that by 20 sessions a day and a team of 5, and you're looking at $700/month in pure token waste.

I got tired of this, so I built **contextly** — a CLI tool that analyzes your codebase once and generates a compact context document that the AI tool reads instead of re-scanning everything.

### How It Works

```bash
pip install contextly
cd your-project
contextly generate
```

That's it. It scans your project, analyzes the code, and generates a `CLAUDE.md` (or `.cursorrules` for Cursor, or `.github/copilot-instructions.md` for Copilot).

### What Gets Analyzed

The tool does real analysis, not just file listing:

- **AST-level code parsing** — finds classes, functions, decorators, imports
- **Convention detection** — naming style, indentation, quote style, type hints
- **Dependency analysis** — reads pyproject.toml, package.json, Cargo.toml, go.mod, Gemfile
- **Pattern recognition** — detects frameworks (Flask, FastAPI, Express), architecture patterns (Service/Repository, Middleware)
- **Entry point detection** — identifies main files, CLI entry points, server files
- **Gotcha detection** — flags missing tests, large files, multi-language complexity

### The Output

The generated context document includes:

1. Project overview and tech stack
2. Architecture summary
3. Entry points
4. Directory structure
5. Dependencies with versions
6. Code conventions
7. Detected patterns
8. Important gotchas
9. Testing information

### Results

On a real project:

| Metric | Value |
|---|---|
| Source tokens to read | 24,100 |
| Context file tokens | 342 |
| Reduction | 98.6% |
| Monthly savings (1 dev, 20 sessions) | ~$14 |
| Monthly savings (10 devs, 20 sessions) | ~$142 |

For larger projects, the savings are even more dramatic.

### Cost Breakdown by Provider

| Provider | Without Context | With Context | Saved |
|---|---|---|---|
| Claude Opus 4 | $0.3615 | $0.0051 | 99% |
| Claude Sonnet 4 | $0.0723 | $0.0010 | 99% |
| GPT-4o | $0.0603 | $0.0009 | 99% |
| Gemini 2.5 Pro | $0.0301 | $0.0004 | 99% |

### CI Integration

Add a GitHub Action to auto-update context files on every push:

```yaml
# .github/workflows/update-context.yml
name: Update AI Context
on:
  push:
    branches: [main]
permissions:
  contents: write
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install contextly
      - run: contextly generate
      - run: contextly generate --format cursor
      - name: Commit if changed
        run: |
          git config user.name "github-actions[bot]"
          git add CLAUDE.md .cursorrules
          git diff --cached --quiet || git commit -m "chore: update context [skip ci]"
          git push
```

### What's Next

Roadmap items I'm considering:
- Incremental context updates (only re-analyze changed files)
- Language-specific deep analysis (Go, Rust, Java)
- VS Code extension
- Monorepo workspace support
- Team context sharing registry

### Try It Out

```bash
pip install contextly
cd your-project
contextly generate
contextly cost    # see your exact savings
```

GitHub: https://github.com/sanyamk23/contextly

Would love feedback — what other AI coding cost problems should I tackle next?
