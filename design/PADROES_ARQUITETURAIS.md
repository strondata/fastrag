# Padrões Arquiteturais para Frameworks de Engenharia de Dados

## Capítulo 1. O Imperativo da Abstração em Plataformas de Dados Modernas

### 1.1 Introdução: Além dos Scripts Ad-Hoc

A engenharia de dados evoluiu de tarefas isoladas de ETL para plataformas interconectadas que precisam escalar e manter confiabilidade. A proliferação de fontes, o processamento híbrido (batch e streaming) e a exigência de dados confiáveis tornam indispensável uma base arquitetural sólida. Definir contratos claros para componentes como `IDataSet`, `IJob` e `IPipeline` é peça central dessa transformação.

### 1.2 Princípios SOLID como Fundação

- **SRP**: `IDataSet`, `IJob` e `IPipeline` possuem responsabilidades distintas, isolando mudanças.
- **OCP**: Novos conectores ou jobs devem ser adicionados sem modificar o núcleo do framework.
- **DIP e ISP**: A orquestração depende de abstrações, permitindo extensão segura e desacoplada.

### 1.3 Abstração, DIP e ISP em Ação

O DIP estabelece que módulos de alto nível dependem de abstrações, não de implementações. Assim, `Pipeline -> IDataSet <- CsvDataSet` viabiliza extensibilidade. O ISP evita interfaces "gordas", garantindo que componentes dependam apenas de contratos relevantes.

## Capítulo 2. Tipagem Nominal vs. Estrutural em Python

### 2.1 Tipagem Nominal (ABCs) x Estrutural (Protocol)

- **ABCs**: Subtipagem por herança explícita (`class CsvDataSet(AbstractDataSet)`).
- **Protocolos**: Compatibilidade determinada pela estrutura (duck typing formalizado).

### 2.2 Evolução do Python

Python historicamente adotou duck typing. A introdução de `abc` (PEP 3119) trouxe verificação em tempo de execução. O `typing.Protocol` (PEP 544) formalizou tipagem estrutural para análise estática.

## Capítulo 3. Classes Base Abstratas (ABCs)

### 3.1 Contratos em Tempo de Execução

```python
from abc import ABC, abstractmethod

class IDataSet(ABC):
    @abstractmethod
    def load(self):
        ...

    @abstractmethod
    def save(self, data):
        ...

class CsvDataSet(IDataSet):
    def save(self, data):
        print("Salvando dados em CSV...")

try:
    CsvDataSet()
except TypeError as exc:
    print(exc)
```

A exceção no instante da instanciação impede objetos incompletos de entrar no sistema.

### 3.2 Estudo de Caso: `kedro.io.AbstractDataSet`

- **Contrato**: `_load()` e `_save()` são obrigatórios.
- **Ecossistema**: `DataCatalog` opera polimorficamente ignorando detalhes de armazenamento.
- **Herança útil**: Métodos concretos compartilhados (ex.: `exists()`) garantem coerência.

## Capítulo 4. `typing.Protocol`

### 4.1 Duck Typing Formalizado

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class IReadable(Protocol):
    def read(self) -> str:
        ...
```

Protocolos descrevem requisitos estruturais. A análise estática (Mypy, Pyright) garante conformidade.

### 4.2 Retroatividade e Desacoplamento

```python
class FileReader:
    def read(self) -> str:
        ...

class WebReader:
    def read(self) -> str:
        ...

def process_data(source: IReadable):
    content = source.read()
    print(len(content))
```

Nenhuma herança explícita é necessária, facilitando integração com bibliotecas de terceiros.

## Capítulo 5. Arquitetando um Framework de Dados

### 5.1 Componentes Principais

`IDataSet`, `IJob`, `IPipeline` compõem o núcleo. Outros contratos fornecem metadados e governança.

### 5.2 Blueprint ABC (Modelo Kedro)

- **Prós**: Segurança em tempo de execução, comportamento compartilhado.
- **Contras**: Rigidamente acoplado, necessidade de wrappers.

### 5.3 Blueprint Protocol (Modelo Flexível)

- **Prós**: Desacoplado, fácil integração com softwares externos.
- **Contras**: Exige análise estática; não compartilha lógica comum.

### 5.4 Blueprint Híbrido (Recomendado)

- **ABCs** para núcleo (`AbstractJob`, `AbstractPipeline`).
- **Protocolos** para pontos de extensão externos (`IDataSet`).
- **Resultado**: Núcleo robusto com bordas flexíveis.

## Capítulo 6. Recomendações e Estrutura de Decisão

### 6.1 Resumo

ABCs impõem contratos rígidos com possibilidade de comportamento padrão. Protocolos fornecem flexibilidade estrutural e integração retroativa.

### 6.2 Perguntas Norteadoras

1. Precisa fornecer implementação base?  Use ABC.
2. A interface mira componentes externos?  Use Protocol.
3. É vital falhar cedo em runtime?  Prefira ABC.
4. Deseja análise estática sem custo?  Prefira Protocol.
5. Criando sistema de plugins?  Protocol nos pontos de extensão.

### 6.3 Comparativo

| Característica | Classe Base Abstrata | `typing.Protocol` |
| --- | --- | --- |
| Modelo de Tipagem | Subtipagem nominal | Subtipagem estrutural |
| Imposição | Runtime (`TypeError`) | Estática; runtime opcional (`@runtime_checkable`) |
| Herança | Obrigatória | Opcional |
| Retroatividade | Não | Sim |
| Implementação compartilhada | Sim | Não |
| Caso principal | Núcleo de framework | Pontos de extensão / plugins |

### 6.4 Conclusão

A estratégia híbrida alinha rigor interno com flexibilidade externa. ABCs estruturam o coração do framework; Protocolos habilitam um ecossistema de plugins desacoplado. A combinação entrega estabilidade, extensibilidade e adoção facilitada.
