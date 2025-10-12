"""
Ferramentas centrais para validação de qualidade de dados no Aether.

Este módulo define a interface `IQualityValidator`, a exceção específica
`QualityCheckError` e uma factory para resolver validadores com base na
configuração declarativa (`catalog.yml`).
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Dict, Optional, Protocol, runtime_checkable

from aether.core.models import DataSetConfig


class QualityCheckError(Exception):
    """Exceção levantada quando uma validação de qualidade falha."""


@runtime_checkable
class IQualityValidator(Protocol):
    """Contrato mínimo para validadores de qualidade plugáveis."""

    def validate(self, data) -> None:
        """Valida o objeto informado ou levanta `QualityCheckError`."""


@dataclass
class _QualityValidatorEntry:
    validator: Optional[IQualityValidator]


class QualityValidatorFactoryError(Exception):
    """Exceção base para problemas na resolução de validadores de qualidade."""


class QualityValidatorFactory:
    """Factory responsável por materializar validadores de qualidade."""

    def __init__(self) -> None:
        self._registry: Dict[str, type[IQualityValidator]] = {}
        self._cache: Dict[str, _QualityValidatorEntry] = {}

    def register(self, validator_type: str, validator_cls: type[IQualityValidator]):
        """Registra explicitamente um novo tipo de validador."""
        if validator_type in self._registry:
            raise QualityValidatorFactoryError(
                f"Tipo de validador '{validator_type}' já registrado."
            )
        self._registry[validator_type] = validator_cls

    def resolve(self, dataset_name: str, dataset_config: DataSetConfig) -> Optional[IQualityValidator]:
        """Obtém (com cache) o validador associado a um dataset."""
        if dataset_name in self._cache:
            return self._cache[dataset_name].validator

        validator = self._create(dataset_config)
        self._cache[dataset_name] = _QualityValidatorEntry(validator=validator)
        return validator

    def _create(self, dataset_config: DataSetConfig) -> Optional[IQualityValidator]:
        quality_config = dataset_config.quality
        if not quality_config:
            return None

        validator_type = quality_config.type
        if validator_type not in self._registry:
            self._lazy_load(validator_type)

        if validator_type not in self._registry:
            raise QualityValidatorFactoryError(
                f"Tipo de validador '{validator_type}' não está registrado."
            )

        validator_cls = self._registry[validator_type]
        try:
            return validator_cls(**quality_config.options)
        except TypeError as exc:
            raise QualityValidatorFactoryError(
                f"Falha ao instanciar o validador '{validator_type}': {exc}"
            ) from exc

    def _lazy_load(self, validator_type: str) -> None:
        """Carrega dinamicamente um validador seguindo convenção CamelCase -> snake_case."""
        module_name = "".join(
            ["_" + char.lower() if char.isupper() else char for char in validator_type]
        ).lstrip("_")
        module_path = f"aether.core.validators.{module_name}"

        try:
            module = importlib.import_module(module_path)
            validator_cls = getattr(module, validator_type)
        except (ImportError, AttributeError) as exc:
            raise QualityValidatorFactoryError(
                f"Não foi possível carregar o validador '{validator_type}'."
            ) from exc

        if not isinstance(validator_cls, type):
            raise QualityValidatorFactoryError(
                f"O símbolo '{validator_type}' em '{module_path}' não é uma classe."
            )

        self._registry[validator_type] = validator_cls