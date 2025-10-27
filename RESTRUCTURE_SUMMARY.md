# Estrutura de Pastas Otimizada - Clean Code (FastRAG)

## Resumo da Reestruturação

Este documento resume a reorganização do projeto FastRAG seguindo princípios de Clean Code, incluindo Separação de Responsabilidades e Alta Coesão.

## Nova Estrutura

```
/fastrag/
├── .github/              # Workflows do GitHub Actions (CI/CD, Avaliação RAG)
│   └── workflows/
│       ├── test.yml
│       └── rag_evaluation.yml
├── .ci/                  # Configurações gerais de CI
├── docs/                 # Documentação (Wiki gerada, Relatórios)
│   └── wiki/
│       ├── Home.md
│       ├── Architecture.md
│       ├── Components.md
│       ├── Quick-Start.md
│       └── ...
├── data/                 # Documentos fornecidos pelo usuário (ignorado pelo Git)
├── logs/                 # Logs da aplicação (ignorado pelo Git)
├── chroma_data/          # Dados persistentes do ChromaDB (ignorado pelo Git)
├── sample_data/          # Documentos de exemplo para teste/demo
│
├── src/                  # Pasta principal para o código fonte
│   └── rag_chatbot/        # Pacote Python para o sistema RAG
│       ├── __init__.py
│       ├── interfaces.py     # Interfaces Core (IDocumentLoader, IEmbeddingModel, etc.)
│       ├── config.py         # Carregamento de configuração (.env)
│       ├── core.py           # RAGChatbot original
│       ├── base.py           # Classes base para componentes avançados
│       │
│       ├── components/       # Componentes Fundamentais (Blocos de construção básicos)
│       │   ├── __init__.py
│       │   ├── loaders.py      # UniversalLoader (TXT, PDF, DOCX, MD)
│       │   ├── embedders.py    # MiniLMEmbedder
│       │   ├── vector_stores.py# ChromaVectorStore
│       │   ├── llms.py         # OllamaLLM, MockLLM
│       │   └── text_splitters.py # RecursiveCharacterTextSplitter
│       │
│       ├── advanced_rag/     # Agrupamento para técnicas de melhoria do RAG
│       │   ├── __init__.py
│       │   ├── chunking.py     # SemanticChunker, split_into_sentences
│       │   ├── retrieval.py    # HybridRetriever, VectorRetriever, BM25Retriever
│       │   ├── reranking.py    # CrossEncoderReRanker, MockReRanker
│       │   ├── query_transform.py # QueryTransformer (MultiQuery, StepBack, HyDE)
│       │   └── compression.py  # PromptCompressor (Heuristic, Summarization)
│       │
│       ├── agents/           # Agrupamento para capacidades de Agente
│       │   ├── __init__.py
│       │   ├── agent.py        # Lógica do Agente ReAct
│       │   ├── tools.py        # BaseTool, RAGTool, CalculatorTool, MockSearchTool
│       │   ├── memory.py       # MemoryStream, Memory (Importância, Recência, Relevância)
│       │   └── crew.py         # Crew, CrewAgent, Task (Orquestração Multi-Agente)
│       │
│       └── orchestration/    # Agrupamento para gerenciamento de fluxo
│           ├── __init__.py
│           ├── pipeline.py     # Pipeline declarativo (Pipeline)
│           └── routing.py      # Roteador de LLM (Router, RoutingStrategy)
│
├── tests/                # Testes unitários e de integração
│   ├── __init__.py
│   ├── test_phase1.py    # Testes de componentes base
│   ├── test_phase2.py    # Testes de técnicas avançadas
│   ├── test_phase3.py    # Testes de agentes
│   ├── test_phase4.py    # Testes de orquestração
│   ├── test_core.py      # Testes do core
│   └── ...
│
├── entrypoints/          # Para múltiplos pontos de entrada
│   ├── __init__.py
│   ├── app.py            # Aplicação Streamlit UI
│   ├── demo.py           # Demo via linha de comando
│   └── validate.py       # Scripts de validação
│
├── app.py                # Aplicação Streamlit principal (raiz para compatibilidade)
├── demo.py               # Demo script (raiz para compatibilidade)
├── validate.py           # Validação (raiz para compatibilidade)
├── .coveragerc           # Configuração da cobertura de testes
├── .env.example          # Template para variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo Git
├── Dockerfile            # Instruções de build Docker
├── docker-compose.yml    # Docker Compose para desenvolvimento
├── docker-compose.production.yml # Docker Compose para produção
├── LICENSE               # Licença do projeto
├── pytest.ini            # Configuração do Pytest
├── README.md             # README principal do projeto
└── requirements.txt      # Dependências Python
```

## Mudanças Principais

### 1. Criação da pasta `src/`
- Todo o código fonte agora está organizado em `src/rag_chatbot/`
- Facilita a distinção entre código fonte e outros arquivos do projeto
- Permite melhor empacotamento e distribuição

### 2. Organização em Módulos Temáticos

#### `components/`
Componentes fundamentais do sistema RAG:
- Carregadores de documentos (loaders.py)
- Modelos de embedding (embedders.py)
- Vector stores (vector_stores.py)
- LLMs (llms.py)
- Text splitters (text_splitters.py)

#### `advanced_rag/`
Técnicas avançadas de RAG:
- Chunking semântico (chunking.py)
- Retrieval híbrido (retrieval.py)
- Re-ranking (reranking.py)
- Query transformation (query_transform.py)
- Prompt compression (compression.py)

#### `agents/`
Funcionalidades de agentes:
- Agente ReAct (agent.py)
- Ferramentas para agentes (tools.py)
- Sistema de memória (memory.py)
- Orquestração multi-agente (crew.py)

#### `orchestration/`
Gerenciamento de fluxo:
- Pipeline declarativo (pipeline.py)
- Roteamento de LLM (routing.py)

### 3. Entrypoints
Scripts de entrada da aplicação organizados em `entrypoints/`:
- `app.py` - Interface Streamlit
- `demo.py` - Demonstração via CLI
- `validate.py` - Validação do sistema

**Nota:** Os mesmos arquivos foram mantidos na raiz para compatibilidade com comandos como `streamlit run app.py`.

## Importações

### Estrutura de Importações

#### De fora do pacote (ex: tests, entrypoints):
```python
from src.rag_chatbot.core import RAGChatbot
from src.rag_chatbot.components.loaders import UniversalLoader
from src.rag_chatbot.advanced_rag.chunking import SemanticChunker
from src.rag_chatbot.agents.agent import Agent
from src.rag_chatbot.orchestration.pipeline import Pipeline
```

#### Dentro do pacote src/rag_chatbot:
```python
# Importações relativas
from .interfaces import Documento
from .config import DEFAULT_LLM_MODEL
from ..base import BaseComponent
from ..interfaces import ILocalLLM
```

## Benefícios da Nova Estrutura

1. **Separação de Responsabilidades**: Cada módulo tem uma responsabilidade clara
2. **Alta Coesão**: Componentes relacionados estão agrupados
3. **Baixo Acoplamento**: Interfaces bem definidas entre módulos
4. **Facilidade de Navegação**: Estrutura intuitiva para encontrar código
5. **Escalabilidade**: Fácil adicionar novos componentes sem afetar outros
6. **Testabilidade**: Testes organizados seguindo a mesma estrutura
7. **Documentação**: Estrutura autodocumentada

## Validação

### Testes
Todos os 72 testes continuam passando após a reestruturação:
- test_phase1.py: 12 testes ✅
- test_phase2.py: 15 testes ✅
- test_phase3.py: 22 testes ✅
- test_phase4.py: 15 testes ✅
- test_core.py: 8 testes ✅

### Scripts de Validação
- `validate.py`: Verifica a estrutura e importações ✅
- `demo.py`: Demonstração funcional ✅

## Compatibilidade

A reestruturação mantém compatibilidade com:
- Comandos existentes (`streamlit run app.py`, `python demo.py`)
- Dockerfiles
- Docker Compose
- GitHub Actions
- Estrutura de testes

## Próximos Passos

Para desenvolvedores que desejam contribuir:

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute os testes: `pytest`
4. Rode a validação: `python validate.py`
5. Execute a aplicação: `streamlit run app.py`

## Conclusão

A nova estrutura segue as melhores práticas de Clean Code e facilita a manutenção, evolução e compreensão do projeto FastRAG.
