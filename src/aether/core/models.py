"""
Este módulo define os modelos de dados Pydantic para os arquivos de configuração
do Aether, como `catalog.yml` e `pipeline.yml`.

Esses modelos garantem que as configurações sejam bem-formadas, validadas e
facilmente acessíveis no código.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DataSetConfig(BaseModel):
    """
    Define a configuração para um único DataSet no `catalog.yml`.
    """

    type: str = Field(
        ...,
        description="O tipo de DataSet, que corresponde a uma classe que implementa IDataSet.",
    )
    layer: str = Field(
        description="A camada do data mesh (ex: raw, staging, curated).",
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parâmetros de configuração específicos para o tipo de DataSet (ex: path, table_name).",
    )


class CatalogConfig(BaseModel):
    """
    Modelo para o arquivo `catalog.yml` completo.
    """

    datasets: Dict[str, DataSetConfig] = Field(
        ..., description="Um dicionário de todos os DataSets definidos."
    )


class JobConfig(BaseModel):
    """
    Define a configuração para um único Job no `pipeline.yml`.
    """

    description: Optional[str] = None
    inputs: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapeamento de nomes de entrada para nomes de DataSet no catálogo.",
    )
    outputs: List[str] = Field(
        default_factory=list,
        description="Lista de nomes de saída que este job produz.",
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parâmetros a serem passados para a instância do Job.",
    )


class PipelineConfig(BaseModel):
    """
    Modelo para o arquivo `pipeline.yml` completo.
    """

    description: Optional[str] = None
    jobs: Dict[str, JobConfig] = Field(
        ..., description="Um dicionário de todos os Jobs que compõem o pipeline."
    )
