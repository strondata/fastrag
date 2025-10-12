"""Tests for new CLI commands: test, lint, catalog."""

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aether.cli import app

runner = CliRunner(env={"AETHER_LOG_LEVEL": "CRITICAL"})  # Suppress logs in tests


@pytest.fixture
def valid_pipeline(tmp_path: Path) -> Path:
    """Create a valid pipeline directory for testing."""
    pipeline_dir = tmp_path / "test_pipeline"
    pipeline_dir.mkdir()
    
    # Create valid catalog.yml
    catalog_content = """datasets:
  raw_data:
    type: CsvDataSet
    layer: raw
    options:
      path: /data/input.csv
  
  processed_data:
    type: ParquetDataSet
    layer: processed
    options:
      path: /data/output.parquet
  
  curated_data:
    type: ParquetDataSet
    layer: curated
    options:
      path: /data/final.parquet
    quality:
      type: PanderaValidator
      options:
        schema: "schemas.curated_schema"
"""
    (pipeline_dir / "catalog.yml").write_text(catalog_content)
    
    # Create valid pipeline.yml
    pipeline_content = """description: A test pipeline

jobs:
  process_job:
    type: sample_jobs.SampleJob
    inputs:
      raw: raw_data
    outputs:
      processed: processed_data
    
  curate_job:
    type: sample_jobs.SampleJob
    inputs:
      processed: processed_data
    outputs:
      curated: curated_data
"""
    (pipeline_dir / "pipeline.yml").write_text(pipeline_content)
    
    return pipeline_dir


@pytest.fixture
def invalid_pipeline_missing_files(tmp_path: Path) -> Path:
    """Create pipeline directory missing config files."""
    pipeline_dir = tmp_path / "invalid_pipeline"
    pipeline_dir.mkdir()
    return pipeline_dir


@pytest.fixture
def pipeline_with_cycle(tmp_path: Path) -> Path:
    """Create pipeline with circular dependency."""
    pipeline_dir = tmp_path / "cycle_pipeline"
    pipeline_dir.mkdir()
    
    catalog_content = """datasets:
  dataset_a:
    type: InMemoryDataSet
    layer: raw
  dataset_b:
    type: InMemoryDataSet
    layer: processed
"""
    (pipeline_dir / "catalog.yml").write_text(catalog_content)
    
    # Create circular dependency: job1 -> dataset_b, job2 -> dataset_a
    # but job1 needs dataset_a and job2 needs dataset_b
    pipeline_content = """jobs:
  job1:
    type: sample_jobs.SampleJob
    inputs:
      input: dataset_a
    outputs:
      output: dataset_b
  
  job2:
    type: sample_jobs.SampleJob
    inputs:
      input: dataset_b
    outputs:
      output: dataset_a
"""
    (pipeline_dir / "pipeline.yml").write_text(pipeline_content)
    
    return pipeline_dir


@pytest.fixture
def pipeline_missing_dataset_ref(tmp_path: Path) -> Path:
    """Create pipeline with missing dataset reference."""
    pipeline_dir = tmp_path / "missing_ref_pipeline"
    pipeline_dir.mkdir()
    
    catalog_content = """datasets:
  existing_dataset:
    type: InMemoryDataSet
    layer: raw
"""
    (pipeline_dir / "catalog.yml").write_text(catalog_content)
    
    pipeline_content = """jobs:
  test_job:
    type: sample_jobs.SampleJob
    inputs:
      input: nonexistent_dataset
    outputs:
      output: existing_dataset
"""
    (pipeline_dir / "pipeline.yml").write_text(pipeline_content)
    
    return pipeline_dir


class TestAetherTestCommand:
    """Tests for 'aether test' command."""
    
    def test_valid_pipeline(self, valid_pipeline: Path):
        """Test that valid pipeline passes all tests."""
        result = runner.invoke(app, ["test", str(valid_pipeline)])
        
        if result.exit_code != 0:
            print(f"\nSTDOUT:\n{result.stdout}")
            print(f"\nEXIT CODE: {result.exit_code}")
        
        assert result.exit_code == 0
        assert "✅ Todos os testes passaram!" in result.stdout
        assert "pipeline.yml encontrado" in result.stdout
        assert "catalog.yml encontrado" in result.stdout
        assert "Schemas válidos" in result.stdout
        assert "DAG válido" in result.stdout
    
    def test_missing_files(self, invalid_pipeline_missing_files: Path):
        """Test that missing files are detected."""
        result = runner.invoke(app, ["test", str(invalid_pipeline_missing_files)])
        
        assert result.exit_code == 1
        assert "❌" in result.stdout
        assert "pipeline.yml não encontrado" in result.stdout or "catalog.yml não encontrado" in result.stdout
    
    def test_circular_dependency(self, pipeline_with_cycle: Path):
        """Test that circular dependencies are detected."""
        result = runner.invoke(app, ["test", str(pipeline_with_cycle)])
        
        assert result.exit_code == 1
        assert "❌" in result.stdout
        # Should detect cycle in DAG
        assert "DAG" in result.stdout or "ciclo" in result.stdout.lower()
    
    def test_missing_dataset_reference(self, pipeline_missing_dataset_ref: Path):
        """Test that missing dataset references are detected."""
        result = runner.invoke(app, ["test", str(pipeline_missing_dataset_ref)])
        
        assert result.exit_code == 1
        assert "❌" in result.stdout
        assert "nonexistent_dataset" in result.stdout
        assert "não existe no catalog" in result.stdout
    
    def test_verbose_mode(self, valid_pipeline: Path):
        """Test verbose mode shows additional details."""
        result = runner.invoke(app, ["test", str(valid_pipeline), "--verbose"])
        
        assert result.exit_code == 0
        assert "Detalhes do Pipeline" in result.stdout
        assert "Jobs:" in result.stdout
        assert "Datasets:" in result.stdout
        assert "Layers:" in result.stdout
    
    def test_nonexistent_directory(self, tmp_path: Path):
        """Test that nonexistent directory is handled."""
        nonexistent = tmp_path / "does_not_exist"
        result = runner.invoke(app, ["test", str(nonexistent)])
        
        assert result.exit_code != 0


class TestAetherLintCommand:
    """Tests for 'aether lint' command."""
    
    def test_valid_pipeline_no_warnings(self, valid_pipeline: Path):
        """Test that well-formed pipeline has no lint warnings."""
        result = runner.invoke(app, ["lint", str(valid_pipeline)])
        
        # May have warnings but should not error
        assert "Erros:" not in result.stdout or "Erros: 0" in result.stdout
    
    def test_invalid_layer(self, tmp_path: Path):
        """Test that invalid layer is detected as error."""
        pipeline_dir = tmp_path / "invalid_layer"
        pipeline_dir.mkdir()
        
        catalog_content = """datasets:
  bad_dataset:
    type: InMemoryDataSet
    layer: invalid_layer
    options: {}
"""
        (pipeline_dir / "catalog.yml").write_text(catalog_content)
        
        pipeline_content = """jobs: {}
"""
        (pipeline_dir / "pipeline.yml").write_text(pipeline_content)
        
        result = runner.invoke(app, ["lint", str(pipeline_dir)])
        
        assert result.exit_code == 1
        assert "layer inválido" in result.stdout
        assert "invalid_layer" in result.stdout
    
    def test_non_snake_case_names(self, tmp_path: Path):
        """Test that non-snake_case names trigger warnings."""
        pipeline_dir = tmp_path / "bad_naming"
        pipeline_dir.mkdir()
        
        catalog_content = """datasets:
  BadDataSet:
    type: InMemoryDataSet
    layer: raw
    options: {}
"""
        (pipeline_dir / "catalog.yml").write_text(catalog_content)
        
        pipeline_content = """jobs:
  BadJobName:
    type: sample_jobs.SampleJob
    inputs: {}
    outputs:
      bad_out: BadDataSet
"""
        (pipeline_dir / "pipeline.yml").write_text(pipeline_content)
        
        result = runner.invoke(app, ["lint", str(pipeline_dir)])
        
        assert "⚠️" in result.stdout or "Avisos:" in result.stdout
        assert "snake_case" in result.stdout
    
    def test_curated_without_quality(self, tmp_path: Path):
        """Test warning for curated dataset without quality validation."""
        pipeline_dir = tmp_path / "no_quality"
        pipeline_dir.mkdir()
        
        catalog_content = """datasets:
  curated_no_quality:
    type: ParquetDataSet
    layer: curated
    options:
      path: /data/output.parquet
"""
        (pipeline_dir / "catalog.yml").write_text(catalog_content)
        
        pipeline_content = """jobs: {}
"""
        (pipeline_dir / "pipeline.yml").write_text(pipeline_content)
        
        result = runner.invoke(app, ["lint", str(pipeline_dir)])
        
        assert "curated_no_quality" in result.stdout
        assert "qualidade" in result.stdout or "quality" in result.stdout
    
    def test_unused_dataset_warning(self, tmp_path: Path):
        """Test warning for datasets not used in any job."""
        pipeline_dir = tmp_path / "unused"
        pipeline_dir.mkdir()
        
        catalog_content = """datasets:
  used_dataset:
    type: InMemoryDataSet
    layer: raw
  unused_dataset:
    type: InMemoryDataSet
    layer: raw
"""
        (pipeline_dir / "catalog.yml").write_text(catalog_content)
        
        pipeline_content = """jobs:
  single_job:
    type: sample_jobs.SampleJob
    inputs: {}
    outputs:
      out: used_dataset
"""
        (pipeline_dir / "pipeline.yml").write_text(pipeline_content)
        
        result = runner.invoke(app, ["lint", str(pipeline_dir)])
        
        assert "unused_dataset" in result.stdout
        assert "não utilizado" in result.stdout
    
    def test_strict_mode(self, tmp_path: Path):
        """Test that strict mode converts warnings to errors."""
        pipeline_dir = tmp_path / "warnings"
        pipeline_dir.mkdir()
        
        catalog_content = """datasets:
  BadName:
    type: InMemoryDataSet
    layer: raw
    options: {}
"""
        (pipeline_dir / "catalog.yml").write_text(catalog_content)
        
        pipeline_content = """jobs: {}
"""
        (pipeline_dir / "pipeline.yml").write_text(pipeline_content)
        
        # Normal mode - should pass despite warnings
        result_normal = runner.invoke(app, ["lint", str(pipeline_dir)])
        # May exit 0 or 1 depending on warnings
        
        # Strict mode - should fail on warnings
        result_strict = runner.invoke(app, ["lint", str(pipeline_dir), "--strict"])
        assert result_strict.exit_code == 1
        assert "❌" in result_strict.stdout


class TestAetherCatalogCommand:
    """Tests for 'aether catalog' command."""
    
    def test_list_all_datasets(self, valid_pipeline: Path):
        """Test listing all datasets."""
        result = runner.invoke(app, ["catalog", str(valid_pipeline)])
        
        assert result.exit_code == 0
        assert "raw_data" in result.stdout
        assert "processed_data" in result.stdout
        assert "curated_data" in result.stdout
        assert "CsvDataSet" in result.stdout
        assert "ParquetDataSet" in result.stdout
    
    def test_json_output(self, valid_pipeline: Path):
        """Test JSON output format."""
        result = runner.invoke(app, ["catalog", str(valid_pipeline), "--json"])
        
        assert result.exit_code == 0
        
        # Should be valid JSON
        import json
        data = json.loads(result.stdout)
        
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Check structure
        for item in data:
            assert "name" in item
            assert "type" in item
            assert "layer" in item
            assert "path" in item
            assert "has_quality" in item
    
    def test_filter_by_layer(self, valid_pipeline: Path):
        """Test filtering by specific layer."""
        result = runner.invoke(app, ["catalog", str(valid_pipeline), "--layer", "raw"])
        
        assert result.exit_code == 0
        assert "raw_data" in result.stdout
        assert "processed_data" not in result.stdout
        assert "curated_data" not in result.stdout
    
    def test_shows_quality_badge(self, valid_pipeline: Path):
        """Test that quality validation is indicated."""
        result = runner.invoke(app, ["catalog", str(valid_pipeline)])
        
        assert result.exit_code == 0
        # curated_data has quality, should show badge
        assert "🛡️" in result.stdout or "Quality:" in result.stdout
    
    def test_grouped_by_layer(self, valid_pipeline: Path):
        """Test that output is grouped by layer."""
        result = runner.invoke(app, ["catalog", str(valid_pipeline)])
        
        assert result.exit_code == 0
        assert "RAW" in result.stdout
        assert "PROCESSED" in result.stdout
        assert "CURATED" in result.stdout
    
    def test_empty_catalog(self, tmp_path: Path):
        """Test catalog with no datasets."""
        pipeline_dir = tmp_path / "empty"
        pipeline_dir.mkdir()
        
        catalog_content = """datasets: {}
"""
        (pipeline_dir / "catalog.yml").write_text(catalog_content)
        
        pipeline_content = """jobs: {}
"""
        (pipeline_dir / "pipeline.yml").write_text(pipeline_content)
        
        result = runner.invoke(app, ["catalog", str(pipeline_dir)])
        
        assert result.exit_code == 0
        assert "Nenhum dataset encontrado" in result.stdout or "Total: 0" in result.stdout


class TestCLIIntegration:
    """Integration tests combining multiple CLI commands."""
    
    def test_test_then_catalog(self, valid_pipeline: Path):
        """Test running test command followed by catalog."""
        # First test
        test_result = runner.invoke(app, ["test", str(valid_pipeline)])
        assert test_result.exit_code == 0
        
        # Then catalog
        catalog_result = runner.invoke(app, ["catalog", str(valid_pipeline)])
        assert catalog_result.exit_code == 0
    
    def test_lint_then_test(self, valid_pipeline: Path):
        """Test running lint followed by test."""
        lint_result = runner.invoke(app, ["lint", str(valid_pipeline)])
        # May have warnings but should succeed
        
        test_result = runner.invoke(app, ["test", str(valid_pipeline)])
        assert test_result.exit_code == 0
    
    def test_all_commands_on_invalid_pipeline(self, invalid_pipeline_missing_files: Path):
        """Test that all commands fail gracefully on invalid pipeline."""
        commands = [
            ["test", str(invalid_pipeline_missing_files)],
            ["lint", str(invalid_pipeline_missing_files)],
            ["catalog", str(invalid_pipeline_missing_files)],
        ]
        
        for cmd in commands:
            result = runner.invoke(app, cmd)
            assert result.exit_code != 0
