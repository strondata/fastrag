# FastRAG

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

O seu consagrado sistema de Retrieval-Augmented Generation (RAG)

## 📋 Visão Geral

FastRAG é uma biblioteca Python para construir sistemas eficientes de RAG (Retrieval-Augmented Generation). Este projeto fornece ferramentas e utilitários para implementar pipelines de recuperação e geração de informações.

## 🚀 Instalação

### Instalação Básica

```bash
pip install -e .
```

### Instalação para Desenvolvimento

```bash
pip install -e ".[dev]"
```

Ou usando os arquivos de requisitos:

```bash
pip install -r requirements.txt  # Dependências básicas
pip install -r requirements-dev.txt  # Dependências de desenvolvimento
```

## 💡 Uso Rápido

```python
from fastrag import RAGSystem

# Inicializar o sistema
rag = RAGSystem()

# Adicionar documentos
rag.add_document("Python é uma linguagem de programação de alto nível.")
rag.add_document("FastRAG é uma biblioteca para sistemas RAG.")

# Fazer uma consulta
resposta = rag.query("O que é FastRAG?")
print(resposta)
```

## 📁 Estrutura do Projeto

```
fastrag/
├── src/
│   └── fastrag/           # Código fonte principal
│       ├── __init__.py
│       ├── core.py        # Sistema RAG principal
│       └── utils.py       # Funções utilitárias
├── tests/                 # Testes
│   ├── test_core.py
│   └── test_utils.py
├── examples/              # Exemplos de uso
│   ├── basic_usage.py
│   └── utils_example.py
├── docs/                  # Documentação
│   └── README.md
├── pyproject.toml         # Configuração do projeto
├── requirements.txt       # Dependências
└── README.md             # Este arquivo
```

## 🧪 Executando Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=fastrag --cov-report=term-missing

# Teste específico
pytest tests/test_core.py
```

## 🛠️ Desenvolvimento

### Formatação de Código

```bash
# Formatar código
black src/ tests/

# Ordenar imports
isort src/ tests/
```

### Linting

```bash
# Verificar estilo
flake8 src/ tests/

# Verificar tipos
mypy src/
```

## 📖 Documentação

Para documentação detalhada, veja o diretório [docs/](docs/README.md).

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ✨ Exemplos

Veja o diretório [examples/](examples/) para exemplos de uso:

- `basic_usage.py` - Uso básico do sistema RAG
- `utils_example.py` - Uso de funções utilitárias

## 🔧 Requisitos

- Python 3.8+
- numpy >= 1.20.0
- requests >= 2.25.0

## 📞 Suporte

Para questões e suporte, abra uma [issue](https://github.com/strondata/fastrag/issues) no GitHub.
