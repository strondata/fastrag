# RAG (Retrieval-Augmented Generation) - Conceitos Fundamentais

## O que é RAG?

RAG é uma técnica que combina a recuperação de informações com a geração de texto por modelos de linguagem. Em vez de depender apenas do conhecimento pré-treinado do modelo, o RAG busca informações relevantes em uma base de conhecimento externa antes de gerar a resposta.

## Componentes Principais

### 1. Document Loader (Carregador de Documentos)

Responsável por importar documentos de várias fontes:
- Arquivos locais (txt, md, pdf, docx)
- Bases de dados
- APIs e web scraping
- Sistemas de arquivos distribuídos

### 2. Text Splitter (Divisor de Texto)

Divide documentos grandes em chunks (fragmentos) gerenciáveis:
- Mantém contexto semântico
- Respeita limites de tamanho
- Cria sobreposição entre chunks
- Preserva estrutura do documento

### 3. Embedding Model (Modelo de Embedding)

Converte texto em representações vetoriais:
- Captura significado semântico
- Permite comparação de similaridade
- Dimensão típica: 384 a 1536 dimensões
- Exemplos: sentence-transformers, OpenAI embeddings

### Vector Stores

Banco de dados otimizado para busca de similaridade:
- Indexação eficiente de vetores
- Busca rápida por proximidade
- Persistência de dados
- **FastRAG usa**: ChromaDB
- **Outras opções no ecossistema**: Pinecone, Weaviate, FAISS

### 5. LLM (Large Language Model)

Modelo de linguagem que gera respostas:
- Processa prompt com contexto
- Gera texto natural e fluente
- Pode ser local (Ollama) ou remoto (OpenAI)
- Versões multimodais processam imagens

## Fluxo de Trabalho RAG

### Fase de Ingestão (Offline)

```
Documentos → Loader → Text Splitter → Embedding → Vector Store
```

1. Documentos são carregados do sistema de arquivos
2. Divididos em chunks otimizados
3. Transformados em vetores (embeddings)
4. Armazenados em banco vetorial com metadados

### Fase de Consulta (Online)

```
Pergunta → Embedding → Busca Vetorial → Contexto → LLM → Resposta
```

1. Pergunta do usuário é convertida em vetor
2. Vector store busca chunks mais similares
3. Chunks recuperados formam o contexto
4. LLM gera resposta baseada no contexto

## Vantagens do RAG

### 1. Conhecimento Atualizado
- Não depende apenas de dados de treinamento
- Fácil atualização da base de conhecimento
- Incorpora informações recentes

### 2. Rastreabilidade
- Cada resposta tem fontes identificáveis
- Auditoria de informações
- Verificação de fatos

### 3. Redução de Alucinações
- Respostas ancoradas em documentos reais
- Menor chance de informações inventadas
- Modelo pode admitir quando não sabe

### 4. Privacidade
- Dados ficam locais
- Não precisa treinar modelos
- Controle total sobre informações sensíveis

### 5. Especialização
- Adapta modelo geral a domínio específico
- Sem necessidade de fine-tuning
- Custos muito menores

## Desafios do RAG

### 1. Qualidade da Recuperação
- Busca pode não encontrar informação relevante
- Chunks podem quebrar contexto importante
- Similaridade semântica nem sempre perfeita

### 2. Tamanho do Contexto
- LLMs têm limite de tokens
- Muitos chunks podem exceder limite
- Trade-off entre quantidade e qualidade

### 3. Latência
- Busca vetorial adiciona overhead
- Embedding da query leva tempo
- Geração do LLM pode ser lenta

### 4. Consistência
- Diferentes perguntas sobre mesmo tópico podem recuperar chunks diferentes
- Respostas podem variar mesmo com mesma informação

## Métricas de Avaliação

### Retrieval (Recuperação)

- **Precision**: % de documentos recuperados que são relevantes
- **Recall**: % de documentos relevantes que foram recuperados
- **MRR** (Mean Reciprocal Rank): Posição média do primeiro resultado relevante

### Generation (Geração)

- **Faithfulness**: Resposta é fiel aos documentos recuperados?
- **Answer Relevancy**: Resposta é relevante para a pergunta?
- **Context Relevancy**: Contexto recuperado é relevante?

## Melhores Práticas

### 1. Chunking Estratégico
- Escolher tamanho de chunk apropriado ao domínio
- Manter overlap para preservar contexto
- Respeitar estrutura lógica (parágrafos, seções)

### 2. Metadados Ricos
- Incluir fonte, data, autor, categoria
- Facilita filtragem e rastreamento
- Melhora interpretabilidade

### 3. Híbrido: Denso + Esparso
- Combinar busca semântica (embedding) com busca léxica (BM25)
- Melhora recall e precision
- Captura tanto conceito quanto termos exatos

### 4. Prompt Engineering
- Instruir modelo a usar contexto
- Pedir citações de fontes
- Especificar quando admitir desconhecimento

### 5. Iteração e Refinamento
- Monitorar qualidade das respostas
- Ajustar parâmetros (chunk size, top-k)
- Melhorar documentação base

## Ferramentas e Frameworks

### Frameworks RAG
- **LangChain**: Framework completo para aplicações LLM
- **LlamaIndex**: Focado em indexação e recuperação
- **Haystack**: Pipeline de NLP e RAG

### Vector Stores
- **ChromaDB**: Simples, embedding-native
- **Pinecone**: Gerenciado, escalável
- **Weaviate**: Open-source, GraphQL
- **FAISS**: Facebook AI, muito rápido

### Embedding Models
- **sentence-transformers**: Vários modelos otimizados
- **OpenAI embeddings**: Alta qualidade, API
- **Cohere**: Especializado em busca

### LLMs Locais
- **Ollama**: Execução local fácil
- **LM Studio**: Interface gráfica
- **llama.cpp**: Performance otimizada
