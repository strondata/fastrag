# Blueprint Técnico para um Framework Moderno de Engenharia de Dados

## Parte I. Filosofia Arquitetural Fundamental

### Seção 1. Paradigma de Orquestração

A decisão entre um modelo centrado em tarefas (ex.: Kedro, Airflow) e um modelo centrado em ativos (ex.: Dagster) impacta controle, transparência e governança. A abordagem recomendada é híbrida e orientada a ativos:

- **Ativo como primeira classe**: representa produtos de dados persistidos.
- **Pipelines** encapsulam a lógica de materialização de ativos.
- **Nós** mantêm a familiaridade com fluxos de computação.

| Característica | Task-Centric (Kedro) | Asset-Centric (Dagster) | Híbrido Recom. |
| --- | --- | --- | --- |
| Abstração | Nó | Ativo | Ativo + Nós |
| Linhagem | Inferida | Nativa | Nativa |
| Observabilidade | Execução | Estado do ativo | Execução + Ativo |
| Integração dbt | Tarefa | Ativo | Ativo |

### Seção 2. Princípios Orientadores

- **Design orientado a interfaces**: contratos formais (`IAsset`, `IPipeline`, `INode`, `IDataSet`, `IResource`).
- **Inversão de controle e injeção de dependências**: dependências são declaradas e injetadas pelo framework, habilitando testes locais.
- **Configuração declarativa**: componentes descritos em YAML para suportar múltiplos ambientes.

## Parte II. Arquitetura e Componentes

### Seção 3. Contratos Principais

| Interface | Responsabilidade | Destaques |
| --- | --- | --- |
| `IAsset` | Produto de dados persistido | Metadados, tags, domínio |
| `IPipeline` | DAG de nós | Fatiamento, ordenação topológica |
| `INode` | Unidade de computação | `run(context, **inputs)`; DI |
| `IDataSet` | Abstração de I/O | `_load`, `_save`, `_exists` |
| `IIO` | Registro de datasets | Similar ao DataCatalog |
| `IResource` | Serviços externos | `setup`, `teardown` |

Interfaces organizacionais (domínio, grupo, tags) tornam-se metadados flexíveis dentro de `IAsset`.

### Seção 4. Subsistema de I/O

- Definições em `catalog.yml` com suporte a overrides (`conf/base`, `conf/local`).
- Implementações extensíveis (`pandas`, `spark`, `delta`, APIs, bancos de dados).
- Integração com gerenciadores de credenciais.
- Uso recomendado do OmegaConf para carregamento dinâmico.

### Seção 5. Motor de Execução

- **BaseNode**: invólucro de função com entradas, saídas, tags e resolução de dependências.
- **BasePipeline**: constrói e ordena grafo, permite composição e slicing (`from_nodes`, `with_tags`).
- **Runners**: `SequentialRunner` (padrão), `ParallelRunner/ThreadRunner` para paralelismo.

### Seção 6. Recursos Externos (`IResource`)

- Configurados em `resources.yml` e injetados via contexto.
- Solução para `dbutils`: `DatabricksUtilsResource` em produção e `MockDatabricksUtilsResource` para testes.

## Parte III. Experiência do Desenvolvedor

### Seção 7. Ambiente Local

- VSCode com extensão Databricks, ambiente virtual Python e Databricks Connect.
- Estrutura gerada por `framework new` inclui `conf/`, `src/`, `tests/`, `databricks.yml`.
- Fluxo de desenvolvimento em duas camadas:
  1. **Totalmente local** com mocks e dados amostra.
  2. **Interativo-remoto** usando Databricks Connect para alta fidelidade.

### Seção 8. Estratégia de Testes

- Padrão `pytest` com fixtures para `SparkSession` e recursos mockados.
- Comparação de DataFrames com `chispa` ou `pandas.testing`.
- `pysparkdt` para simular Unity Catalog localmente.
- Testes de integração locais (pysparkdt) e remotos (Databricks Connect).

### Seção 9. CLI com Typer

Comandos principais:

- `framework new`
- `framework run --env <env> --assets <lista> --tags <tags>`
- `framework test`
- `framework viz`
- `framework package`
- `framework catalog list`

## Parte IV. Observabilidade, Governança e Deploy

### Seção 10. Interação Programática

- `FrameworkContext` como ponto de entrada único para CLI, notebooks e jobs.
- SDK Python para automação e integração (ex.: `FrameworkSession.create(...).run(...)`).

### Seção 11. Transparência e Linhagem

- `framework viz` inspirado no Kedro-Viz.
- Linhagem recomendada via Unity Catalog; suporte opcional ao OpenLineage.
- Logging estruturado (JSON) com contexto (`run_id`, `pipeline`, `node`).

### Seção 12. Empacotamento e Reuso

- `pyproject.toml` com backend moderno (hatchling/setuptools).
- `project.scripts` registra `framework`.
- Dependências opcionais via extras (`framework[viz,gcp]`).
- Micro-packaging: pipelines distribuídas como pacotes reutilizáveis.

## Parte V. Roteiro de Implementação

### Seção 13. Resumo das Recomendações

1. Paradigma híbrido orientado a ativos.
2. Interfaces explícitas + DI.
3. DataCatalog declarativo e sistema de recursos.
4. DX em duas camadas com VSCode e Databricks Connect.
5. Testes robustos com pytest + pysparkdt.
6. CLI com Typer e visualização integrada.
7. Linhagem nativa e logging estruturado.
8. Empacotamento moderno e micro-reuso.

### Seção 14. Fases de Implementação

- **Fase 1**: Walking skeleton (interfaces, DataCatalog básico, CLI mínima, template inicial).
- **Fase 2**: Foco na DX (guia VSCode/Connect, sistema de recursos, integração notebooks, testes com pysparkdt).
- **Fase 3**: Observabilidade avançada (`framework viz`, linhagem, parallel runner, logging JSON).
- **Fase 4**: Endurecimento (release em PyPI interno, documentação, projeto piloto, governança).
