.PHONY: help install install-dev install-llm-cuda install-llm-metal sync test lint format pre-commit run clean

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install dependencies with uv (without llama-cpp-python, check readme for llama)
	@echo "Installing core dependencies..."
	uv sync
	@echo ""
	@echo "Note: llama-cpp-python requires custom installation for GPU support."
	@echo "Run 'make install-llm-cuda' for NVIDIA GPUs or 'make install-llm-metal' for Apple Silicon."
	@echo "Or use OpenAI API (already configured) by setting OPENAI_API_KEY."

install-llm-cuda: ## Install llama-cpp-python with CUDA support (NVIDIA GPUs)
	uv pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

install-llm-metal: ## Install llama-cpp-python with Metal support (Apple Silicon)
	CMAKE_ARGS="-DLLAMA_METAL=on" uv pip install llama-cpp-python

install-dev: ## Install dependencies including dev tools
	uv sync --all-groups

sync: ## Sync dependencies (update lockfile)
	uv sync --upgrade

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linter
	uv run ruff check .

lint-fix: ## Run linter with auto-fix
	uv run ruff check --fix .

format: ## Format code
	uv run ruff format .

pre-commit: ## Run pre-commit hooks on all files
	uv run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	uv run pre-commit install

run: ## Run the application (use LLM_BACKEND=llama-cpp to use local LLM)
	uv run python main.py

clean: ## Clean up cache and build artifacts
	rm -rf .pytest_cache .ruff_cache __pycache__ .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
