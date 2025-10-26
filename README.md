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

# Com cobertura
pytest --cov=rag_chatbot
```

## 🔧 Configuração Avançada

### Personalizar Modelo LLM

Edite `rag_chatbot/config.py`:

```python
DEFAULT_LLM_MODEL = "mistral"  # ou outro modelo
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
