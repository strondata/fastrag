# Makefile for aether-framework

# Define o diretório de origem para as verificações
SRC_DIR = src/aether tests

# --- Comandos de Qualidade de Código ---

.PHONY: lint
lint:
	@echo "--- 🎨 Executando linters (Ruff e Black) ---"
	ruff check $(SRC_DIR)
	black --check $(SRC_DIR)

.PHONY: format
format:
	@echo "--- 🎨 Formatando código com Black e Ruff ---"
	ruff check --fix $(SRC_DIR)
	black $(SRC_DIR)

.PHONY: type-check
type-check:
	@echo "--- 🔎 Verificando tipos com MyPy ---"
	mypy $(SRC_DIR)

# --- Comandos de Teste ---

.PHONY: test
test:
	@echo "--- 🧪 Executando testes com Pytest ---"
	pytest

# --- Setup do Ambiente ---

.PHONY: setup-dev
setup-dev:
	@echo "--- 📦 Configurando ambiente de desenvolvimento com uv ---"
	uv venv
	uv pip install -e ".[dev]"
	@echo "\n>>> Ambiente pronto! Ative com: source .venv/bin/activate"

.PHONY: all
all: lint type-check test