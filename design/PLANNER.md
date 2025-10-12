# Arquitetando "Aether": Um Framework Unificado e Centrado em Produto

## Parte 1. Visão Executiva: Engenharia de Dados como Produto

### 1.1 Declaração de Missão

- Migrar do modelo "service desk" para uma equipe de produto proativa.
- Capacitar profissionais de dados com uma plataforma padronizada, confiável e eficiente.
- Medir sucesso em termos de impacto de negócio, não apenas entregas técnicas.
- Adotar a pergunta JTBD: *"Que progresso você tenta alcançar?"* em vez de *"Qual pipeline você quer?"*

### 1.2 Aplicando Jobs-to-be-Done (JTBD)

Processo de descoberta:

1. Conduzir entrevistas semi-estruturadas com engenheiros, cientistas e analistas.
2. Mapear trabalhos funcionais, emocionais e sociais de cada persona.
3. Derivar decisões de arquitetura a partir desses trabalhos.

#### Tabela 1. Resumo JTBD por Persona

| Persona | Trabalhos | Dificuldades | Resultados desejados |
| --- | --- | --- | --- |
| Engenheiro de Dados | **Funcional:** construir pipelines reutilizáveis e confiáveis.<br>**Emocional:** reduzir manutenção reativa.<br>**Social:** ser visto como habilitador. | Código repetitivo, falta de padrões, depuração difícil, inconsistência de logging e configuração. | Framework padronizado, orquestração central, linhagem clara, testes automatizados. |
| Cientista de Dados | **Funcional:** acessar dados limpos e versionados.<br>**Emocional:** confiar nas fontes.<br>**Social:** provar valor dos modelos. | Dados inconsistentes, dificuldade de reproduzir experimentos, pouca visibilidade da origem dos dados. | Catálogo de dados, pipelines versionadas, acesso rápido a dados tratados, integração de features. |
| Analista / Negócios | **Funcional:** obter dados atualizados para dashboards.<br>**Emocional:** confiar nas métricas.<br>**Social:** ser referência confiável para liderança. | "Várias versões da verdade", atrasos, falta de contexto, medo de decisões erradas. | Monitoramento de qualidade, glossário único, linhagem visual, alertas proativos. |

### 1.3 Princípios Fundacionais

- **Dados como Produto (DaaP):** ativos detectáveis, endereçáveis, confiáveis e seguros.
- **Data Mesh:** propriedade orientada a domínio + plataforma central habilitadora.
- **Self-Service:** abstrair infraestrutura para permitir autonomia das equipes.
- **Governança Computacional Federada:** padrões de qualidade e acesso incorporados ao pipeline.

### 1.4 Medindo Sucesso: Pirâmide de ROI de Dados

- **Valor do Produto:** adoção, alcance e velocidade de entrega de novos produtos de dados.
- **Tempo de Inatividade (Data Downtime):** reduzir incidentes com observabilidade e qualidade.
- **Investimento:** custos de equipe e plataforma; justificar com retorno mensurável.

## Parte 2. Arquitetura Fundamental e Blueprint de Tecnologia

### 2.1 Fluxograma Geral

Camadas principais:

1. **Developer Experience:** VSCode + Extensão Aether, CLI Typer, documentação (MkDocs).
2. **Versionamento & CI/CD:** GitHub + GitHub Actions (build, lint, test, release).
3. **Núcleo do Framework:** pacote Python com carregadores de configuração, catálogo, pipelines, orquestrador.
4. **Execução:** Python local, Docker, Spark/Databricks.
5. **Dados & Serviços:** S3, bancos SQL/NoSQL, APIs, warehouses.

### 2.2 Fluxo de Identidade e Acesso (IAM)

- **Usuários:** GitHub + políticas de repositório.
- **CI/CD:** OpenID Connect para acesso seguro a nuvem e segredos.
- **Dados:** `credentials.yml` e gerenciadores de segredos; credenciais injetadas em runtime.
- **Separação de Identidades:** desenvolvedor x serviço x pipeline.

### 2.3 Pilha Tecnológica

| Categoria | Tecnologia | Justificativa |
| --- | --- | --- |
| Framework | Python 3.10+ | Ecossistema dominante em dados. |
| Dependências | `pyproject.toml` + uv | Resolução rápida e declarativa. |
| CLI | Typer | Sintaxe moderna com type hints; base em Click. |
| Scaffolding | Cookiecutter | Projetos consistentes e rápidos. |
| Documentação | MkDocs + Material | Site estático, pesquisável, fácil de publicar. |
| CI/CD | GitHub Actions | Integração nativa, marketplace amplo, OIDC. |
| Automação local | Makefile | Documentação executável de comandos. |
| IDE | VSCode Extension API | Experiência integrada, webviews e tasks. |
| Testes | pytest + pytest-mock | Fixtures poderosas e mocking simples. |

## Parte 3. Esqueleto do Framework: Blueprint Orientado a Código

### 3.1 Scaffolding com Cookiecutter

Estrutura padrão:

```
my-aether-project/
├── .github/workflows/
├── conf/
│   ├── base/
│   └── local/
├── data/
├── docs/
├── src/my_aether_project/
│   ├── pipelines/
│   └── nodes/
├── tests/
├── Makefile
└── pyproject.toml
```

### 3.2 Camada de Contratos (SOLID)

- `AbstractDataSet`: define `_load`, `_save`, `_exists`.
- `AbstractTransformation`: padrão Strategy para lógica de negócios (`run(**inputs)`).
- Orquestrador depende apenas de abstrações, permitindo extensibilidade via novas implementações.

### 3.3 Motor Orientado a Metadados

- `catalog.yml`: registro de datasets, tipos e credenciais.
- `credentials.yml`: segredos fora do versionamento.
- `pipeline.yml`: DAG declarativo (inputs -> transformação -> outputs).
- Configuração sobre código para reduzir fricção e suportar múltiplos ambientes.

### 3.4 Orquestração Centrada em Ativos

- Ativos definidos por software (SDAs) a partir de `catalog.yml`.
- Linhagem derivada de `pipeline.yml` + catálogo.
- Ciclo de reconciliação: detectar ativos obsoletos e re-materializar quando necessário.

### 3.5 Padrões de Projeto

| Padrão | Componente | Benefícios |
| --- | --- | --- |
| Fábrica | `DataSetFactory` | Criação dinâmica de datasets sem acoplamento. |
| Estratégia | `AbstractTransformation` | Lógicas intercambiáveis e testáveis. |
| Injeção de Dependência | Orquestrador | Dependências explícitas, melhor testabilidade. |
| Singleton (controlado) | `AetherContext` | Configuração única por execução. |

## Parte 4. Implementação, QA e Testes

### 4.1 Componentes-Chave

- `PandasCsvDataSet`: exemplo completo de `_load/_save/_exists`.
- Orquestrador: ciclo de reconciliação com timestamps e marcação de ativos stale.
- `run_pipeline`: integra fábrica, transformações e ordem topológica.

### 4.2 Pirâmide de Testes

- **Unitários:** transformações isoladas com `pytest`; mocks apenas nas bordas.
- **Integração:** catálogo + datasets operando em recursos temporários.
- **E2E:** execução completa do pipeline com dados reais de teste e validação de resultados.

### 4.3 Estratégias de Mocking

- `dbutils`: injetar dependência e usar `MagicMock`/fixtures.
- APIs externas: `mocker.patch` para respostas determinísticas.
- Bancos de dados: mocks para unit tests; SQLite/containers para integração.

## Parte 5. Experiência do Desenvolvedor e Operacionalização

### 5.1 Extensão VSCode do Aether

- Webview para visualização de DAG (JSON gerado por `aether viz`).
- TaskProvider integra comandos (`run`, `test`, `lint`) ao VSCode.
- CLI opera como backend da extensão.

### 5.2 Documentação como Código

- MkDocs + Material com seções de tutoriais, guias e referência (mkdocstrings).
- Pipeline `docs.yml` publica automaticamente no GitHub Pages.

### 5.3 CI/CD com GitHub Actions

- `pr_checks.yml`: lint, test, build a cada PR.
- `publish.yml`: release automatizada com Trusted Publishing (PyPI).
- `docs.yml`: build e deploy do site.

## Parte 6. Aether em Ação e Adoção

### 6.1 Exemplo de Pipeline ETL

1. Definir `catalog.yml` (CSV -> Parquet).
2. Implementar transformação em `src/.../nodes/`.
3. Declarar DAG em `pipeline.yml`.
4. Executar com `aether run --pipeline=<nome>`.

### 6.2 CLI do Aether (Typer)

- `aether new`
- `aether run --pipeline --params`
- `aether test`
- `aether lint`
- `aether docs`
- `aether viz`

### 6.3 Onboarding e Comunidade

- Guia de onboarding com setup em < 15 minutos.
- `CONTRIBUTING.md` define processo de PR e atualização de docs.
- Centro de Habilitação (C4E) para evangelizar, suportar e evoluir o framework.

## Conclusões

1. **Mentalidade de Produto:** foco em necessidades de usuários internos com JTBD e DaaP.
2. **Arquitetura Descentralizada:** Data Mesh para escalar com autonomia de domínio.
3. **Engenharia Robusta:** princípios SOLID e padrões de projeto garantem sustentabilidade.
4. **Automação Completa:** Makefile, Actions e MkDocs criam ciclo eficiente e confiável.
5. **DevEx como Diferencial:** extensão VSCode, CLI intuitiva e documentação viva impulsionam adoção.

Aether combina tecnologia, processos e cultura para entregar produtos de dados confiáveis, detectáveis e valiosos, habilitando decisões mais rápidas e seguras em toda a organização.
