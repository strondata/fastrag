from pathlib import Path

import pytest

from aether.core.config_loader import load_config
from aether.core.models import CatalogConfig, PipelineConfig
from aether.core.orchestrator import AssetOrchestrator, OrchestratorError
from aether.datasets.in_memory_data_set import InMemoryDataSet


@pytest.fixture
def test_pipeline_path(tmp_path: Path) -> Path:
    """Cria um diretório de projeto de pipeline de teste com catalog e pipeline yml."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    catalog_content = """
    datasets:
      raw_string:
        type: InMemoryDataSet
        layer: raw
        options:
          initial_data: "hello world"
      punctuation_source:
        type: InMemoryDataSet
        layer: raw
        options:
          initial_data: "!"
      uppercased_string:
        type: InMemoryDataSet
        layer: processed
      final_string:
        type: InMemoryDataSet
        layer: curated
    """
    (project_dir / "catalog.yml").write_text(catalog_content)

    pipeline_content = """
    description: "Pipeline de teste para o orquestrador."
    jobs:
      uppercase_job:
        type: aether.jobs.sample_jobs.UpperCaseJob
        inputs:
          input_str: raw_string
        outputs: [uppercased_string]

      uppercase_job:
        type: aether.jobs.sample_jobs.UpperCaseJob
        inputs:
          input_str: raw_string
        outputs:
          output_str: uppercased_string

      add_punctuation_job:
        type: aether.jobs.sample_jobs.ConcatJob
        inputs:
          str_a: uppercased_string
          str_b: punctuation_source
        outputs:
          output_str: final_string
    """
    (project_dir / "pipeline.yml").write_text(pipeline_content)

    return project_dir


def test_orchestrator_e2e_success(test_pipeline_path: Path):
    """Teste de ponta a ponta que executa um pipeline simples."""
    catalog_path = test_pipeline_path / "catalog.yml"
    pipeline_path = test_pipeline_path / "pipeline.yml"

    catalog_config = load_config(catalog_path, CatalogConfig)
    pipeline_config = load_config(pipeline_path, PipelineConfig)

    orchestrator = AssetOrchestrator(pipeline_config, catalog_config)
    orchestrator.run()

    # Verifica o resultado final acessando o cache do orquestrador.
    final_dataset = orchestrator.instance_cache["final_string"]
    assert isinstance(final_dataset, InMemoryDataSet)
    assert final_dataset.load() == "HELLO WORLD!"


def test_orchestrator_cyclic_dependency_error(tmp_path: Path):
    """Verifica se o orquestrador detecta um ciclo de dependências."""
    catalog_content = """
    datasets:
      data_a: { type: InMemoryDataSet, layer: raw }
      data_b: { type: InMemoryDataSet, layer: raw }
    """
    (tmp_path / "catalog.yml").write_text(catalog_content)

    # Job A depende de B, Job B depende de A -> Ciclo
    pipeline_content = """
    jobs:
      job_a:
        type: aether.jobs.sample_jobs.UpperCaseJob
        inputs:
          input_str: data_b
        outputs:
          output_str: data_a
      job_b:
        type: aether.jobs.sample_jobs.UpperCaseJob
        inputs:
          input_str: data_a
        outputs:
          output_str: data_b
    """
    (tmp_path / "pipeline.yml").write_text(pipeline_content)

    catalog_config = load_config(tmp_path / "catalog.yml", CatalogConfig)
    pipeline_config = load_config(tmp_path / "pipeline.yml", PipelineConfig)

    with pytest.raises(
        OrchestratorError, match="O pipeline contém um ciclo de dependências."
    ):
        AssetOrchestrator(pipeline_config, catalog_config)


def test_orchestrator_job_output_mismatch_error(tmp_path: Path):
    """Verifica erro quando um job não produz a saída declarada."""
    catalog_content = """
    datasets:
      in: { type: InMemoryDataSet, layer: raw, options: { initial_data: "a" } }
      out: { type: InMemoryDataSet, layer: processed }
      extra_out: { type: InMemoryDataSet, layer: processed }
    """
    (tmp_path / "catalog.yml").write_text(catalog_content)

    # Job declara duas saídas mas só produz uma
    pipeline_content = """
    jobs:
      my_job:
        type: aether.jobs.sample_jobs.UpperCaseJob
        inputs:
          input_str: in
        outputs:
          output_str: out
          non_existent_output: extra_out
    """
    (tmp_path / "pipeline.yml").write_text(pipeline_content)

    catalog_config = load_config(tmp_path / "catalog.yml", CatalogConfig)
    pipeline_config = load_config(tmp_path / "pipeline.yml", PipelineConfig)

    orchestrator = AssetOrchestrator(pipeline_config, catalog_config)
    with pytest.raises(
        OrchestratorError,
        match="O job 'my_job' produziu 1 saídas, mas 2 foram declaradas.",
    ):
        orchestrator.run()
