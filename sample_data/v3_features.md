# FastRAG v3.0 - Guia de Funcionalidades

## Visão Geral

O FastRAG v3.0 introduz capacidades avançadas de processamento e análise, transformando o chatbot de um simples sistema Q&A para um assistente de análise inteligente.

## Principais Funcionalidades

### 1. Divisão Inteligente de Documentos

O sistema agora divide automaticamente documentos grandes em chunks (fragmentos) menores, melhorando significativamente a precisão das respostas:

- **Chunk Size**: 1000 caracteres por padrão (configurável via `CHUNK_SIZE`)
- **Overlap**: 200 caracteres de sobreposição entre chunks (configurável via `CHUNK_OVERLAP`)
- **Algoritmo**: Divisão recursiva por parágrafos, linhas e espaços
- **Rastreamento**: Cada chunk mantém referência ao documento original

**Benefícios**:
- Respostas mais precisas e contextualizadas
- Melhor recuperação de informações específicas
- Fontes mais granulares e rastreáveis

### 2. Suporte Multi-Formato

Além de arquivos de texto (.txt) e Markdown (.md), agora suportamos:

- **PDF**: Extração de texto de documentos PDF com preservação de páginas
- **DOCX**: Processamento de documentos Microsoft Word

**Formatos Suportados**:
- `.txt` - Arquivos de texto simples
- `.md` - Markdown
- `.pdf` - Adobe PDF
- `.docx` - Microsoft Word

### 3. Análise Multimodal

O chatbot agora pode analisar imagens junto com texto:

- **Modelo**: llava (modelo multimodal do Ollama)
- **Formatos de Imagem**: PNG, JPG, JPEG
- **Casos de Uso**: Análise de gráficos, diagramas, capturas de tela, infográficos

**Como Usar**:
1. Faça upload de uma imagem na interface do chat
2. Escreva sua pergunta sobre a imagem
3. O sistema combina a análise visual com o contexto do RAG

### 4. Memória Conversacional

O chatbot agora mantém contexto da conversa:

- **Histórico**: Todas as mensagens anteriores são consideradas
- **Perguntas de Acompanhamento**: Faça perguntas complementares sem repetir contexto
- **Template Especial**: Prompt formatado com histórico + contexto + pergunta atual

**Exemplo de Conversa**:
```
Usuário: Quais são as principais funcionalidades do v3.0?
Assistente: [Lista as funcionalidades]
Usuário: E qual delas você acha mais importante?
Assistente: [Responde baseado na conversa anterior]
```

## Arquitetura Técnica

### Pipeline de Ingestão

1. **Carregar**: UniversalLoader detecta e processa múltiplos formatos
2. **Dividir**: RecursiveCharacterTextSplitter cria chunks inteligentes
3. **Embedar**: Modelo de embedding transforma chunks em vetores
4. **Armazenar**: ChromaDB persiste embeddings para busca rápida

### Pipeline de Resposta

1. **Query**: Pergunta do usuário (+ imagem opcional)
2. **Embed**: Transformar pergunta em vetor
3. **Buscar**: Encontrar top-k chunks mais relevantes
4. **Contextualizar**: Combinar chunks + histórico + pergunta
5. **Gerar**: LLM gera resposta baseada no contexto completo

## Configurações

### Variáveis de Ambiente

```
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEFAULT_MULTIMODAL_LLM_MODEL=llava
DEFAULT_LLM_MODEL=llama3
```

### Otimização

Para documentos muito grandes:
- Aumente CHUNK_SIZE para reduzir número de chunks
- Ajuste CHUNK_OVERLAP para melhor continuidade

Para perguntas mais precisas:
- Diminua CHUNK_SIZE para chunks mais específicos
- Aumente DEFAULT_TOP_K para considerar mais fontes

## Casos de Uso

1. **Análise de Documentação Técnica**: PDFs de manuais com diagramas
2. **Processamento de Relatórios**: DOCXs com gráficos e tabelas
3. **Base de Conhecimento Empresarial**: Mix de formatos com contexto conversacional
4. **Suporte ao Cliente**: Respostas contextualizadas com histórico de conversa
