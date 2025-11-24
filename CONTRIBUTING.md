# Contributing to LLM Agent RAG System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Getting Started

1. Fork and clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/llm-agent-rag-system.git
cd llm-agent-rag-system
```

2. Install uv if you haven't already:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Set up your development environment:

```bash
# Install all dependencies including dev tools
make install-dev

# Or manually
uv sync --all-groups

# Set up pre-commit hooks
make pre-commit-install

# Or manually
uv run pre-commit install
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

Write your code following the project's style guidelines (enforced by ruff).

### 3. Run Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Or manually
uv run pytest
```

### 4. Check Code Quality

```bash
# Run linter
make lint

# Auto-fix linting issues
make lint-fix

# Format code
make format

# Run all pre-commit hooks
make pre-commit
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature"
```

Pre-commit hooks will automatically run and check your code. If they fail:

- Fix the issues reported
- Stage the changes again
- Retry the commit

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

This project uses:

- **ruff** for linting and formatting
- **type hints** where appropriate
- **docstrings** for public functions and classes

### Commit Message Convention

Follow conventional commits format:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `style:` formatting, missing semicolons, etc.
- `refactor:` code restructuring
- `test:` adding tests
- `chore:` maintenance tasks

Examples:

```
feat: add vector store memory retrieval
fix: correct ChromaDB embedding format
docs: update installation instructions
```

## Testing

### Writing Tests

- Place tests in the `test/` directory
- Follow the naming convention: `test_*.py`
- Use descriptive test names

Example:

```python
def test_vector_store_saves_message_correctly():
    # Arrange
    memory = VectorStoreMemory(num_query_results=2, character_name="Test")

    # Act
    memory.save_initial_lines_as_vectors(
        character_greeting={"role": "assistant", "content": "Hello!"},
        character_name="Test"
    )

    # Assert
    assert memory.collection.count() == 1
```

### Running Specific Tests

```bash
# Run specific test file
uv run pytest test/unit/test_memory.py

# Run specific test function
uv run pytest test/unit/test_memory.py::test_vector_store_saves_message_correctly
```

## Project Structure

```
llm-agent-rag-system/
├── src/
│   └── llm_agent_gui/          # Main application code
│       ├── agent.py            # Agent logic and ReAct framework
│       ├── memory.py           # Memory systems (buffer, summary, vector)
│       ├── llm_backend.py      # LLM inference backends
│       ├── app.py              # GUI application
│       ├── games.py            # Game tools (Tic-Tac-Toe)
│       └── utils/              # Helper modules
├── test/                       # Test files
├── main.py                     # Application entry point
├── pyproject.toml              # Project configuration
├── Makefile                    # Development shortcuts
└── README.md                   # Documentation
```

## Adding Dependencies

### Runtime Dependencies

```bash
uv add <package-name>
```

### Development Dependencies

```bash
uv add --dev <package-name>
```

### Test Dependencies

```bash
uv add --group test <package-name>
```

## Common Issues

### Pre-commit Hooks Fail

If pre-commit hooks fail on commit:

1. Run `make lint-fix` to auto-fix issues
2. Run `make format` to format code
3. Stage changes and commit again

### Tests Fail Locally

Ensure all dependencies are up to date:

```bash
uv sync --upgrade
```

### Import Errors

Make sure you're running commands with `uv run`:

```bash
uv run python main.py
uv run pytest
```

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Be descriptive in your issue reports

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
