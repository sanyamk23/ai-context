# contextly

Generate optimized AI context for your codebase. Save 60-80% on AI coding costs.

## Tech Stack
- **Python** (20 files)
## Architecture
Built with pip. Small codebase (15 source files). Has 5 test files (3:1 source-to-test ratio).

## Key Entry Points
- `contextly/cli.py`

## Project Structure
```
├── .editorconfig
├── .github
│   ├── copilot-instructions.md
│   └── workflows
│       └── update-context.yml
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── contextly
│   ├── __init__.py
│   ├── analyzer
│   │   ├── __init__.py
│   │   ├── ast_analyzer.py
│   │   ├── deps.py
│   │   ├── patterns.py
│   │   └── scanner.py
│   ├── cli.py
│   ├── cost
│   │   ├── __init__.py
│   │   └── estimator.py
│   ├── generator
│   │   ├── __init__.py
│   │   ├── context.py
│   │   ├── templates
│   │   │   ├── claude.md.j2
│   │   │   ├── copilot.j2
│   │   │   ├── cursor.j2
│   │   │   └── generic.j2
│   │   └── token_counter.py
│   └── utils
│       ├── __init__.py
│       ├── git.py
│       └── ignore.py
├── examples
│   └── sample_output.md
├── launch
│   ├── devto.md
  ... and 10 more
```

## Dependencies
**pip** — 4 dependencies
### Core Dependencies
- `click` >=8.0
- `jinja2` >=3.0
- `rich` >=13.0
- `pathspec` >=0.11

## Code Conventions
- **Naming:** PascalCase
- **Indentation:** 4 spaces
- **Quote style:** double
- **Type hints:** Yes
- **Docstrings:** Yes
- **Testing:** jest-style

## Patterns
- General purpose project


## Testing
Test files: 5 files
Location: `tests`