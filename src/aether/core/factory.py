"""
Este módulo contém a DataSetFactory, responsável por instanciar
DataSets com base na configuração do catálogo.
"""

import importlib
from typing import Dict, Type

from aether.core.interfaces import IDataSet
from aether.core.models import CatalogConfig


class DataSetFactoryError(Exception):
    """Exceção base para erros da DataSetFactory."""


class DataSetFactory:
    """
    Uma factory para criar instâncias de IDataSet a partir da configuração.

    Esta factory mantém um registro de tipos de DataSet disponíveis e os
    instancia com base no campo 'type' do `catalog.yml`.
    """

    def __init__(self):
        self._registry: Dict[str, Type[IDataSet]] = {}

    def register(self, dataset_type: str, dataset_class: Type[IDataSet]):
        """Registra um novo tipo de IDataSet."""
        if dataset_type in self._registry:
            raise DataSetFactoryError(
                f"Tipo de DataSet '{dataset_type}' já registrado."
            )
        self._registry[dataset_type] = dataset_class

    def create(self, name: str, catalog: CatalogConfig) -> IDataSet:
        """
        Cria uma instância de IDataSet a partir do catálogo.

        Args:
            name: O nome (chave) do DataSet no catálogo.
            catalog: O objeto de configuração do catálogo carregado.

        Returns:
            Uma instância do IDataSet configurado.

        Raises:
            DataSetFactoryError: Se o DataSet não for encontrado no catálogo ou
                                 se o tipo não estiver registrado.
        """
        if name not in catalog.datasets:
            raise DataSetFactoryError(f"DataSet '{name}' não encontrado no catálogo.")

        config = catalog.datasets[name]
        dataset_type = config.type

        if dataset_type not in self._registry:
            self._lazy_load(dataset_type)

        if dataset_type not in self._registry:
            raise DataSetFactoryError(
                f"Tipo de DataSet '{dataset_type}' não registrado."
            )

        dataset_class = self._registry[dataset_type]
        return dataset_class(**config.options)

    def _lazy_load(self, dataset_type: str):
        """
        Tenta carregar dinamicamente um tipo de dataset se não estiver registrado.
        Assume uma convenção onde 'TypeName' corresponde a 'aether.datasets.typename.TypeName'.
        """
        try:
            # Converte 'TypeName' para 'typename' para o nome do módulo
            module_name = "".join(
                ["_" + i.lower() if i.isupper() else i for i in dataset_type]
            ).lstrip("_")
            module_path = f"aether.datasets.{module_name}"

            module = importlib.import_module(module_path)

            # A classe deve ter o mesmo nome que o tipo
            class_name = dataset_type
            dataset_class = getattr(module, class_name)

            if isinstance(dataset_class, type) and issubclass(dataset_class, IDataSet):
                self.register(dataset_type, dataset_class)
        except (ImportError, AttributeError, ValueError):
            # Falha silenciosamente, o erro será levantado no `create` se o registro falhar.
            pass
