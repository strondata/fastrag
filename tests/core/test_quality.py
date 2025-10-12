from pathlib import Path

import pytest
import yaml

from aether.core.config_loader import load_config
from aether.core.models import CatalogConfig, PipelineConfig
from aether.core.orchestrator import AssetOrchestrator
from aether.core.quality import QualityCheckError

pd = pytest.importorskip("pandas")
pytest.importorskip("pandera")


def _write_quality_catalog(tmp_path: Path, schema_path: str) -> Path:
    catalog_dict = {
        "datasets": {
            "validated_customers": {
                "type": "InMemoryDataSet",
                "layer": "curated",
                "quality": {
                    "type": "PanderaValidator",
                    "options": {"schema": schema_path},
                },
            }
        }
    }
    catalog_file = tmp_path / "catalog.yml"
    catalog_file.write_text(yaml.safe_dump(catalog_dict, sort_keys=False))
    return catalog_file


def _write_quality_pipeline(tmp_path: Path, data_rows) -> Path:
    pipeline_dict = {
        "jobs": {
            "build_customers": {
                "type": "aether.jobs.sample_jobs.CreateDataFrameJob",
                "outputs": {"dataframe": "validated_customers"},
                "params": {"data": data_rows},
            }
        }
    }
    pipeline_file = tmp_path / "pipeline.yml"
    pipeline_file.write_text(yaml.safe_dump(pipeline_dict, sort_keys=False))
    return pipeline_file


def test_pandera_validator_success(tmp_path: Path):
    catalog_path = _write_quality_catalog(
        tmp_path, "tests.quality.schemas.customer_schema"
    )
    pipeline_path = _write_quality_pipeline(
        tmp_path,
        [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ],
    )

    catalog_config = load_config(catalog_path, CatalogConfig)
    pipeline_config = load_config(pipeline_path, PipelineConfig)

    orchestrator = AssetOrchestrator(pipeline_config, catalog_config)
    orchestrator.run()

    dataset = orchestrator.instance_cache["validated_customers"]
    loaded_df = dataset.load()

    expected_df = pd.DataFrame([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
    pd.testing.assert_frame_equal(loaded_df, expected_df)


def test_pandera_validator_failure(tmp_path: Path):
    catalog_path = _write_quality_catalog(
        tmp_path, "tests.quality.schemas.customer_schema"
    )
    pipeline_path = _write_quality_pipeline(
        tmp_path,
        [
            {"id": -1, "name": "Invalid"},
        ],
    )

    catalog_config = load_config(catalog_path, CatalogConfig)
    pipeline_config = load_config(pipeline_path, PipelineConfig)

    orchestrator = AssetOrchestrator(pipeline_config, catalog_config)

    with pytest.raises(
        QualityCheckError,
        match="Falha na validação de qualidade para o dataset 'validated_customers'",
    ):
        orchestrator.run()
