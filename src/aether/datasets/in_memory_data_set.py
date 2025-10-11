"""
Implementação de um IDataSet que armazena dados em memória.
Ideal para testes e prototipagem.
"""

from typing import Any


class InMemoryDataSet:
    """
    Um IDataSet que cumpre o protocolo e armazena dados em uma variável.
    """

    def __init__(self, initial_data: Any = None):
        self._data = initial_data
        print(f"InMemoryDataSet inicializado com dados: {self._data}")

    def load(self) -> Any:
        """Carrega dados da memória."""
        print(f"Carregando dados da memória: {self._data}")
        return self._data

    def save(self, data: Any) -> None:
        """Salva dados na memória."""
        print(f"Salvando dados na memória: {data}")
        self._data = data

    def __eq__(self, other):
        if not isinstance(other, InMemoryDataSet):
            return NotImplemented
        return self._data == other._data
