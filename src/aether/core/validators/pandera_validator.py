"""Implementação de validador baseado em Pandera."""

from __future__ import annotations

import importlib
from typing import Any

from aether.core.quality import IQualityValidator, QualityCheckError


class PanderaValidator(IQualityValidator):
    """Valida objetos do Pandas usando um schema Pandera."""

    def __init__(self, schema: str):
        if not schema:
            raise QualityCheckError("O parâmetro 'schema' é obrigatório para o PanderaValidator.")

        try:
            import pandera as pa  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - depende de instalação opcional
            raise QualityCheckError(
                "Pandera não está instalado. Instale o extra 'quality' para utilizar este validador."
            ) from exc

        self._pandera = pa
        self._schema = self._load_schema(schema)

    def validate(self, data: Any) -> None:
        try:
            self._schema.validate(data)
        except self._pandera.errors.SchemaError as exc:
            raise QualityCheckError(f"Falha na validação Pandera: {exc}") from exc

    def _load_schema(self, schema_path: str):
        try:
            module_path, attribute_name = schema_path.rsplit(".", 1)
        except ValueError as exc:
            raise QualityCheckError(
                "O caminho do schema deve estar no formato 'modulo.objeto'."
            ) from exc

        try:
            module = importlib.import_module(module_path)
            schema_obj = getattr(module, attribute_name)
        except (ImportError, AttributeError) as exc:
            raise QualityCheckError(
                f"Não foi possível carregar o schema Pandera '{schema_path}'."
            ) from exc

        if isinstance(schema_obj, self._pandera.DataFrameSchema):
            return schema_obj
        if isinstance(schema_obj, self._pandera.SeriesSchema):
            return schema_obj

        schema_model = getattr(self._pandera.api.pandas.model, "SchemaModel", None)
        if schema_model and isinstance(schema_obj, type) and issubclass(schema_obj, schema_model):
            return schema_obj.to_schema()

        raise QualityCheckError(
            "O schema deve ser uma instância de DataFrameSchema, SeriesSchema ou uma SchemaModel Pandera."
        )
