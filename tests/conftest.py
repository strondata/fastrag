from pathlib import Path

import pytest


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
