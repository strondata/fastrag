from pathlib import Path

import pytest

from aether.core.config_loader import AetherConfigError, load_config
from aether.core.models import CatalogConfig, PipelineConfig


def test_load_catalog_success(tmp_path: Path):
    """Verifica o carregamento de um catalog.yml válido."""
    content = """
    datasets:
      raw_customers:
        type: "ParquetDataSet"
        layer: "raw"
        options:
          path: "data/raw/customers.parquet"
      processed_customers:
        type: "PandasDataSet"
        layer: "processed"
    """
    config_file = tmp_path / "catalog.yml"
    config_file.write_text(content)

    catalog = load_config(config_file, CatalogConfig)
    assert "raw_customers" in catalog.datasets
    assert catalog.datasets["raw_customers"].type == "ParquetDataSet"
    assert (
        catalog.datasets["raw_customers"].options["path"]
        == "data/raw/customers.parquet"
    )


def test_load_pipeline_success(tmp_path: Path):
    """Verifica o carregamento de um pipeline.yml válido."""
    content = """
    description: "Um pipeline de exemplo."
    jobs:
      job_a:
        type: "some.job.type"
        description: "Primeiro job."
        inputs:
          customers: "raw_customers"
        outputs:
          output: "intermediate_table"
        params:
          param1: "value1"
      job_b:
        type: "another.job.type"
        inputs:
          source_data: "intermediate_table"
        outputs:
          output: "final_output"
    """
    config_file = tmp_path / "pipeline.yml"
    config_file.write_text(content)

    pipeline = load_config(config_file, PipelineConfig)
    assert pipeline.description == "Um pipeline de exemplo."
    assert "job_a" in pipeline.jobs
    assert pipeline.jobs["job_a"].inputs["customers"] == "raw_customers"


def test_load_config_not_found():
    """Verifica se AetherConfigError é levantado para arquivo inexistente."""
    with pytest.raises(
        AetherConfigError, match="Arquivo de configuração não encontrado"
    ):
        load_config(Path("non_existent_file.yml"), CatalogConfig)


def test_load_config_invalid_yaml(tmp_path: Path):
    """Verifica se AetherConfigError é levantado para YAML inválido."""
    config_file = tmp_path / "invalid.yml"
    config_file.write_text("datasets: { raw_data: [}")

    with pytest.raises(AetherConfigError, match="Erro ao analisar o YAML"):
        load_config(config_file, CatalogConfig)


def test_load_config_validation_error(tmp_path: Path):
    """Verifica se AetherConfigError é levantado para dados que falham na validação Pydantic."""
    content = """
    datasets:
      my_dataset:
        # 'type' é um campo obrigatório, sua falta deve causar erro.
        layer: "raw"
    """
    config_file = tmp_path / "invalid_data.yml"
    config_file.write_text(content)

    with pytest.raises(AetherConfigError, match="Erro de validação de configuração"):
        load_config(config_file, CatalogConfig)
