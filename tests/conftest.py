from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def reset_logging_for_tests():
    """Reset logging configuration before each test to avoid pollution."""
    from aether.core.logger import reset_logging_config, configure_logging
    import os
    
    # Reset to clean state
    reset_logging_config()
    
    # Reconfigure with test-appropriate settings (CRITICAL to suppress output)
    log_level = os.getenv("AETHER_LOG_LEVEL", "CRITICAL")
    log_json = os.getenv("AETHER_LOG_JSON", "false").lower() == "true"
    configure_logging(log_level=log_level, json_output=log_json)
    
    yield
    
    # Clean up after test
    reset_logging_config()


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
