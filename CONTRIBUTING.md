# Contributing to ai-context

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/sanyamk23/ai-context.git
cd ai-context
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest                    # run all tests
pytest tests/test_cli.py  # run specific test file
pytest -v                 # verbose output
```

## Project Structure

```
ai_context/
├── analyzer/       # Code analysis (scanner, AST, deps, patterns)
├── generator/      # Context document generation + templates
├── cost/           # Token cost estimation
├── utils/          # Git helpers, file filtering
└── cli.py          # Click-based CLI
```

## Adding a New Output Format

1. Create a new Jinja2 template in `ai_context/generator/templates/`
2. Add the format to `TEMPLATE_MAP` and `OUTPUT_MAP` in `generator/context.py`
3. Add a Click choice in `cli.py`
4. Add tests

## Adding Language Support

1. Add file extensions to `EXTENSION_LANG` in `analyzer/scanner.py`
2. Add analysis logic in `analyzer/ast_analyzer.py` if needed
3. Add test fixtures

## Reporting Issues

Open an issue with:
- Your OS and Python version
- The command you ran
- The output or error message
- A minimal reproduction if possible

## Code Style

- Follow the existing patterns
- Keep functions focused and small
- Add type hints where practical
- Tests for new features
