# 🤖 Chatbot RAG Local Personalizado

Sistema de Chatbot RAG (Retrieval-Augmented Generation) modular, extensível e testável em Python, com interface Streamlit.

## 📋 Visão Geral

Este projeto implementa um chatbot que responde perguntas baseadas em uma base de conhecimento privada (documentos locais), utilizando:

- **RAG (Retrieval-Augmented Generation)**: Combina busca semântica com geração de texto
- **LLM Local**: Usa Ollama para rodar modelos de linguagem localmente
- **Embeddings**: SentenceTransformers para vetorização de texto
- **Vector Store**: ChromaDB para armazenamento e busca eficiente
- **UI**: Interface web interativa com Streamlit

### Princípios de Design (SOLID)

O sistema foi construído seguindo os princípios SOLID:

- **[S] Single Responsibility**: Cada classe tem uma responsabilidade única
- **[O] Open/Closed**: Aberto para extensão, fechado para modificação
- **[L] Liskov Substitution**: Componentes são intercambiáveis via interfaces
- **[I] Interface Segregation**: Interfaces pequenas e focadas
- **[D] Dependency Inversion**: Dependência de abstrações, não implementações

## 🏗️ Estrutura do Projeto

```
/chatbot-rag-local/
│
├── /data/                   # (Ignorado) Documentos do usuário
├── /logs/                   # (Ignorado) Arquivos de log
│
├── /rag_chatbot/            # Pacote principal
│   ├── __init__.py
│   ├── interfaces.py        # Interfaces abstratas (ABC)
│   ├── core.py              # Orquestrador RAGChatbot
│   ├── config.py            # Configurações
│   └── /components/         # Implementações concretas
│       ├── loaders.py       # FolderLoader
│       ├── embedders.py     # MiniLMEmbedder
│       ├── vector_stores.py # ChromaVectorStore
│       └── llms.py          # OllamaLLM, MockLLM
│
├── /tests/                  # Testes
│   ├── test_core.py         # Testes do RAGChatbot
│   └── test_components.py   # Testes dos componentes
│
├── app.py                   # Aplicativo Streamlit
├── requirements.txt         # Dependências
├── README.md               # Esta documentação
└── .gitignore              # Arquivos ignorados
```

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/strondata/fastrag.git
cd fastrag
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar LLM Local (Ollama)

#### Instalar Ollama

- **Linux/Mac**: 
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- **Windows**: Baixar de [ollama.com](https://ollama.com)

#### Baixar um Modelo

```bash
ollama pull llama3
# Ou outros modelos: mistral, phi, gemma, etc.
```

#### Iniciar Ollama

```bash
ollama serve
```

## 📖 Uso

### Executar o Chatbot

```bash
streamlit run app.py
```

O aplicativo abrirá em `http://localhost:8501`

### Alimentar a Base de Conhecimento

1. **Adicionar Documentos**: Coloque seus arquivos `.txt` ou `.md` na pasta `./data/`
   
   ```bash
   mkdir -p data
   echo "O cachorro é marrom e amigável." > data/animais.txt
   ```

2. **No Streamlit**: Clique no botão **"Alimentar RAG"** na sidebar

3. **Fazer Perguntas**: Use o chat para interagir com sua base de conhecimento

### Exemplo de Uso

```
Usuário: Qual a cor do cachorro?
Bot: O cachorro é marrom.
```

## 🧪 Testes

### Executar Todos os Testes

```bash
pytest
```

### Executar Testes Específicos

```bash
# Testes do core
pytest tests/test_core.py

# Testes dos componentes
pytest tests/test_components.py

# Com verbosidade
pytest -v
```

### Executar Testes com Cobertura

```bash
# Gerar relatório de cobertura
pytest --cov=rag_chatbot

# Gerar relatório HTML detalhado
pytest --cov=rag_chatbot --cov-report=html

# O relatório HTML será gerado em htmlcov/index.html
```

### Cobertura Atual

**62.70% de cobertura de código** com 72+ testes passando!

- ✅ `core.py`: 100%
- ✅ `config.py`: 100%
- ✅ `components/embedders.py`: 100%
- ✅ `components/vector_stores.py`: 95.45%
- ✅ `components/loaders.py`: 90.16%
- ✅ `components/llms.py`: 83.33%

Ver [documentação completa de testes](docs/wiki/Testing.md) para mais detalhes.

## 📚 Documentação Completa

### Wiki Abrangente

Criamos uma wiki completa em `docs/wiki/` com documentação detalhada:

- **[Home](docs/wiki/Home.md)** - Visão geral do projeto
- **[Quick Start](docs/wiki/Quick-Start.md)** - Guia rápido de início
- **[Architecture](docs/wiki/Architecture.md)** - Arquitetura e princípios SOLID
- **[Components](docs/wiki/Components.md)** - Referência completa de componentes
- **[Testing](docs/wiki/Testing.md)** - Guia de testes e cobertura (62.70%)
- **[Advanced Features](docs/wiki/Advanced-Features.md)** - Técnicas avançadas de RAG

### Recursos Destacados

- ✅ **62.70% de cobertura de testes** (72+ testes passando)
- ✅ **Documentação completa** com exemplos de código
- ✅ **Guias de arquitetura** explicando princípios SOLID
- ✅ **Referência de API** para todos os componentes
- ✅ **Tutoriais avançados** sobre técnicas de RAG

## 🐳 Docker

### Executar com Docker Compose

A maneira mais fácil de rodar a aplicação completa (incluindo Ollama):

```bash
# Iniciar todos os serviços
docker-compose up -d

# Baixar modelo no container Ollama
docker exec -it fastrag-ollama ollama pull llama3

# Verificar logs
docker-compose logs -f app

# Parar serviços
docker-compose down
```

A aplicação estará disponível em `http://localhost:8501`

### Construir Apenas a Aplicação

```bash
# Construir imagem
docker build -t fastrag-app .

# Executar (assumindo Ollama já rodando)
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/chroma_data:/app/chroma_data \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  fastrag-app
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (use `.env.example` como template):

```bash
# Copiar exemplo
cp .env.example .env

# Editar conforme necessário
nano .env
```

Configurações disponíveis:

- `DEFAULT_LLM_MODEL`: Modelo LLM padrão (default: `llama3`)
- `OLLAMA_HOST`: URL do servidor Ollama (default: `http://localhost:11434`)
- `DEFAULT_EMBEDDING_MODEL`: Modelo de embedding (default: `all-MiniLM-L6-v2`)
- `DATA_DIR`: Diretório de dados (default: `./data`)
- `LOGS_DIR`: Diretório de logs (default: `./logs`)
- `CHROMA_PERSIST_DIRECTORY`: Diretório do ChromaDB (default: `./chroma_data`)
- `DEFAULT_COLLECTION_NAME`: Nome da coleção (default: `rag_store`)
- `DEFAULT_TOP_K`: Número de documentos a recuperar (default: `3`)
- `LOG_LEVEL`: Nível de log (default: `INFO`)

### Personalizar Modelo LLM

Via variável de ambiente:

```bash
export DEFAULT_LLM_MODEL="mistral"
streamlit run app.py
```

Ou configure na interface do Streamlit.

### Personalizar Template de Prompt

```python
from rag_chatbot.core import RAGChatbot

custom_template = """
Responda em português brasileiro:
CONTEXTO: {context}
PERGUNTA: {question}
RESPOSTA:
"""

chatbot = RAGChatbot(
    loader=loader,
    embedder=embedder,
    store=store,
    llm=llm,
    prompt_template=custom_template
)
```

### Usar Diferentes Componentes

```python
from rag_chatbot.components.loaders import FolderLoader
from rag_chatbot.components.embedders import MiniLMEmbedder
from rag_chatbot.components.vector_stores import ChromaVectorStore
from rag_chatbot.components.llms import OllamaLLM
from rag_chatbot.core import RAGChatbot

# Componentes customizados
loader = FolderLoader()
embedder = MiniLMEmbedder(model_name="paraphrase-multilingual-MiniLM-L12-v2")
store = ChromaVectorStore(collection_name="my_custom_rag")
llm = OllamaLLM(model_name="mistral")

chatbot = RAGChatbot(loader, embedder, store, llm)
```

## 📚 API Reference

### RAGChatbot

```python
chatbot = RAGChatbot(loader, embedder, store, llm)

# Alimentar com dados
num_docs = chatbot.ingest_data("/path/to/data")

# Fazer pergunta
response = chatbot.ask("Sua pergunta aqui", k=3)

# Obter documentos fonte
sources = chatbot.get_sources("Pergunta", k=3)
```

### Interfaces

- `IDocumentLoader`: Carrega documentos de uma fonte
- `IEmbeddingModel`: Gera embeddings de texto
- `IVectorStore`: Armazena e busca vetores
- `ILocalLLM`: Gera texto com LLM local

## 🐛 Troubleshooting

### Erro: "Pacote 'ollama' não encontrado"

```bash
pip install ollama
```

### Erro: "Ollama não está rodando"

```bash
ollama serve
```

### Erro: "Modelo não encontrado"

```bash
ollama pull llama3
```

### Logs

Verifique os logs em `./logs/rag_chatbot.log` para debugging detalhado.

### Persistência de Dados

Os dados do RAG são automaticamente salvos no diretório `./chroma_data/` e persistem entre reinicializações. Para limpar e recomeçar:

```bash
rm -rf ./chroma_data
```

## 🆕 Novidades v2.0

### Configuração via Variáveis de Ambiente
- Suporte a arquivo `.env` para configuração
- Não mais hardcoded - todas as configurações são customizáveis
- Persistência real do ChromaDB entre reinicializações

### Interface Melhorada
- UI reorganizada em abas: Chat, Gerenciar RAG, Ajuda
- Visualização de fontes utilizadas em cada resposta
- Inspeção de fontes sem chamar o LLM
- Melhor organização da sidebar

### Docker Support
- Dockerfile pronto para produção
- Docker Compose com Ollama integrado
- Volumes para persistência de dados
- Network configurada para comunicação entre serviços

### Qualidade de Código
- Cobertura de testes com pytest-cov
- Documentação completa
- Pronto para deploy

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Padrão de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `test:` Testes
- `refactor:` Refatoração de código

## 📄 Licença

Este projeto é de código aberto.

## 👥 Autores

- Desenvolvido seguindo especificações SOLID e boas práticas Python

## 🔗 Links Úteis

- [Ollama](https://ollama.com)
- [Streamlit](https://streamlit.io)
- [ChromaDB](https://www.trychroma.com)
- [SentenceTransformers](https://www.sbert.net)

---

**Nota**: Este é um projeto educacional que demonstra implementação de RAG com arquitetura modular e princípios SOLID.
