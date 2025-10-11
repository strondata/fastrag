"""
Este módulo define os contratos arquiteturais centrais do Framework Aether.

Ele emprega uma abordagem híbrida:
- Protocolos (Typing Nominal) são usados para interfaces de "plugin", como `IDataSet`,
  permitindo máxima flexibilidade e integração com sistemas externos.
- Classes Base Abstratas (ABCs) são usadas para o núcleo do framework, como
  `AbstractJob` e `AbstractPipeline`, para fornecer comportamento compartilhado e
  impor uma estrutura mais rígida.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, runtime_checkable

# --- Protocolo para o Ponto de Extensão Externo ---


@runtime_checkable
class IDataSet(Protocol):
    """
    Protocolo que define o contrato para todos os conectores de dados.

    Qualquer classe que implemente os métodos `load` e `save` com as assinaturas
    corretas é considerada um IDataSet válido. Isso permite uma integração
    desacoplada com bibliotecas de terceiros (ex: pandas, polars) sem
    a necessidade de herança explícita.
    """

    def load(self) -> Any:
        """
        Carrega dados da fonte e os retorna como um objeto em memória.

        Returns:
            Os dados carregados (ex: DataFrame, dicionário, etc.).
        """
        ...

    def save(self, data: Any) -> None:
        """
        Salva os dados em memória na fonte de destino.

        Args:
            data: O objeto de dados a ser salvo.
        """
        ...


# --- ABCs para Componentes Centrais do Framework ---


class AbstractJob(ABC):
    """
    Classe base abstrata para uma unidade de transformação (um "nó" no DAG).

    Jobs herdam desta classe para se integrarem ao ciclo de vida do orquestrador
    e para ganhar funcionalidades compartilhadas (ex: logging, manipulação de
    parâmetros).
    """

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}
        # Futuramente, um logger pode ser injetado aqui.
        print(f"Job '{self.name}' inicializado com parâmetros: {self.params}")

    def run(self, **inputs: IDataSet) -> Dict[str, Any]:
        """
        Método Template: Orquestra a execução do job. Não deve ser sobrescrito.

        Args:
            inputs: Um dicionário de `IDataSet` de entrada, cujas chaves
                    correspondem às entradas definidas no pipeline.yml.

        Returns:
            Um dicionário onde as chaves são os nomes das saídas e os valores
            são os dados transformados a serem salvos.
        """
        print(f"--- Iniciando Job: {self.name} ---")
        try:
            # Carrega todas as entradas antes da execução
            loaded_inputs = {key: dataset.load() for key, dataset in inputs.items()}

            # Executa a lógica de negócio principal
            outputs = self._execute(**loaded_inputs)

            print(f"--- Job '{self.name}' concluído com sucesso ---")
            return outputs
        except Exception as e:
            print(f"!!! Erro no Job '{self.name}': {e}")
            raise

    @abstractmethod
    def _execute(self, **loaded_inputs: Any) -> Dict[str, Any]:
        """
        Método abstrato contendo a lógica de negócio principal do job.
        Deve ser implementado pelas subclasses.

        Args:
            loaded_inputs: Um dicionário com os dados de entrada já carregados.

        Returns:
            Um dicionário com os dados de saída produzidos.
        """
        raise NotImplementedError


class AbstractPipeline(ABC):
    """
    Classe base abstrata para a orquestração de um DAG de Jobs.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def define_dag(self) -> Dict:
        """
        Define a estrutura do Grafo Acíclico Dirigido (DAG).

        Returns:
            Uma representação do DAG (ex: lista de nós e arestas).
        """
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        """
        Executa o pipeline completo.
        """
        raise NotImplementedError
