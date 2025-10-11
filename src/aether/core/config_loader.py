"""
Este módulo fornece funcionalidades para carregar e validar arquivos de
configuração YAML usando modelos Pydantic.
"""

from pathlib import Path
from typing import Type, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class AetherConfigError(Exception):
    """Exceção base para erros de configuração no Aether."""


def load_config(config_path: Path, model: Type[T]) -> T:
    """
    Carrega um arquivo de configuração YAML, valida-o com um modelo Pydantic
    e retorna uma instância do modelo.

    Args:
        config_path: O caminho para o arquivo de configuração YAML.
        model: A classe do modelo Pydantic para usar na validação.

    Returns:
        Uma instância do modelo Pydantic preenchida com os dados do arquivo.

    Raises:
        AetherConfigError: Se o arquivo não for encontrado, for inválido como YAML
                           ou não passar na validação do Pydantic.
    """
    if not config_path.is_file():
        raise AetherConfigError(
            f"Arquivo de configuração não encontrado: {config_path}"
        )

    try:
        with open(config_path, "r") as f:
            raw_config = yaml.safe_load(f)
        return model.model_validate(raw_config)
    except yaml.YAMLError as e:
        raise AetherConfigError(f"Erro ao analisar o YAML em {config_path}: {e}") from e
    except ValidationError as e:
        raise AetherConfigError(
            f"Erro de validação de configuração em {config_path}:\n{e}"
        ) from e
