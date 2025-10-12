"""Tests for ParquetDataSet."""

from pathlib import Path

import pandas as pd
import pytest

from aether.datasets.parquet_data_set import ParquetDataSet


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age": [25, 30, 35, 28, 32],
        "department": ["Engineering", "Sales", "Engineering", "HR", "Sales"],
    })


@pytest.fixture
def partitioned_dataframe() -> pd.DataFrame:
    """Create a DataFrame suitable for partitioning tests."""
    return pd.DataFrame({
        "id": range(1, 11),
        "value": range(10, 20),
        "year": [2023, 2023, 2023, 2024, 2024, 2024, 2024, 2025, 2025, 2025],
        "month": [1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
    })


class TestParquetDataSetBasic:
    """Basic functionality tests for ParquetDataSet."""

    def test_init_default_options(self, tmp_path: Path):
        """Test initialization with default options."""
        dataset = ParquetDataSet(path=str(tmp_path / "test.parquet"))
        
        assert dataset.path == tmp_path / "test.parquet"
        assert dataset.engine == "pandas"
        assert dataset.compression == "snappy"
        assert dataset.partition_cols == []
        assert dataset.schema is None

    def test_init_custom_options(self, tmp_path: Path):
        """Test initialization with custom options."""
        dataset = ParquetDataSet(
            path=str(tmp_path / "test.parquet"),
            engine="pandas",
            compression="gzip",
            partition_cols=["year", "month"],
        )
        
        assert dataset.engine == "pandas"
        assert dataset.compression == "gzip"
        assert dataset.partition_cols == ["year", "month"]

    def test_init_invalid_engine(self, tmp_path: Path):
        """Test that invalid engine raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported engine"):
            ParquetDataSet(
                path=str(tmp_path / "test.parquet"),
                engine="invalid",
            )

    def test_repr(self, tmp_path: Path):
        """Test string representation."""
        dataset = ParquetDataSet(
            path=str(tmp_path / "test.parquet"),
            compression="zstd",
        )
        
        repr_str = repr(dataset)
        assert "ParquetDataSet" in repr_str
        assert "test.parquet" in repr_str
        assert "pandas" in repr_str
        assert "zstd" in repr_str


class TestParquetDataSetPandas:
    """Tests for ParquetDataSet with pandas engine."""

    def test_save_and_load_basic(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test basic save and load functionality."""
        file_path = tmp_path / "test.parquet"
        dataset = ParquetDataSet(path=str(file_path))
        
        # Save
        dataset.save(sample_dataframe)
        assert file_path.exists()
        
        # Load
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)

    def test_save_with_different_compressions(
        self, tmp_path: Path, sample_dataframe: pd.DataFrame
    ):
        """Test saving with different compression codecs."""
        compressions = ["snappy", "gzip", "brotli", "lz4", "zstd", None]
        
        for compression in compressions:
            file_path = tmp_path / f"test_{compression}.parquet"
            dataset = ParquetDataSet(
                path=str(file_path),
                compression=compression,
            )
            
            dataset.save(sample_dataframe)
            assert file_path.exists()
            
            loaded_df = dataset.load()
            pd.testing.assert_frame_equal(loaded_df, sample_dataframe)

    def test_save_creates_parent_directories(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test that save creates parent directories if they don't exist."""
        file_path = tmp_path / "nested" / "dir" / "test.parquet"
        dataset = ParquetDataSet(path=str(file_path))
        
        dataset.save(sample_dataframe)
        assert file_path.exists()
        assert file_path.parent.exists()

    def test_load_nonexistent_file(self, tmp_path: Path):
        """Test that loading non-existent file raises FileNotFoundError."""
        dataset = ParquetDataSet(path=str(tmp_path / "nonexistent.parquet"))
        
        with pytest.raises(FileNotFoundError, match="Parquet file not found"):
            dataset.load()

    def test_save_wrong_data_type(self, tmp_path: Path):
        """Test that saving wrong data type raises ValueError."""
        dataset = ParquetDataSet(path=str(tmp_path / "test.parquet"))
        
        with pytest.raises(ValueError, match="Expected pandas DataFrame"):
            dataset.save({"not": "a dataframe"})

    def test_save_with_custom_write_options(
        self, tmp_path: Path, sample_dataframe: pd.DataFrame
    ):
        """Test save with custom write options."""
        file_path = tmp_path / "test.parquet"
        dataset = ParquetDataSet(
            path=str(file_path),
            write_options={"row_group_size": 1000},
        )
        
        dataset.save(sample_dataframe)
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)

    def test_load_with_custom_read_options(
        self, tmp_path: Path, sample_dataframe: pd.DataFrame
    ):
        """Test load with custom read options."""
        file_path = tmp_path / "test.parquet"
        
        # Save first
        dataset_write = ParquetDataSet(path=str(file_path))
        dataset_write.save(sample_dataframe)
        
        # Load with specific columns
        dataset_read = ParquetDataSet(
            path=str(file_path),
            read_options={"columns": ["id", "name"]},
        )
        
        loaded_df = dataset_read.load()
        assert list(loaded_df.columns) == ["id", "name"]
        assert len(loaded_df) == len(sample_dataframe)


class TestParquetDataSetPartitioning:
    """Tests for partitioned Parquet datasets."""

    def test_save_partitioned_pandas(
        self, tmp_path: Path, partitioned_dataframe: pd.DataFrame
    ):
        """Test saving partitioned dataset with pandas."""
        output_dir = tmp_path / "partitioned"
        dataset = ParquetDataSet(
            path=str(output_dir),
            partition_cols=["year", "month"],
        )
        
        dataset.save(partitioned_dataframe)
        
        # Check that partition directories were created
        assert output_dir.exists()
        assert output_dir.is_dir()
        
        # Should have year partitions
        year_partitions = list(output_dir.glob("year=*"))
        assert len(year_partitions) > 0

    def test_load_partitioned_pandas(
        self, tmp_path: Path, partitioned_dataframe: pd.DataFrame
    ):
        """Test loading partitioned dataset with pandas."""
        output_dir = tmp_path / "partitioned"
        dataset = ParquetDataSet(
            path=str(output_dir),
            partition_cols=["year", "month"],
        )
        
        # Save partitioned
        dataset.save(partitioned_dataframe)
        
        # Load back
        loaded_df = dataset.load()
        
        # Pandas adds partition columns back
        assert "year" in loaded_df.columns
        assert "month" in loaded_df.columns
        assert len(loaded_df) == len(partitioned_dataframe)

    def test_single_partition_column(
        self, tmp_path: Path, partitioned_dataframe: pd.DataFrame
    ):
        """Test partitioning by single column."""
        output_dir = tmp_path / "single_partition"
        dataset = ParquetDataSet(
            path=str(output_dir),
            partition_cols=["year"],
        )
        
        dataset.save(partitioned_dataframe)
        
        year_partitions = list(output_dir.glob("year=*"))
        assert len(year_partitions) == 3  # 2023, 2024, 2025


class TestParquetDataSetEdgeCases:
    """Edge case tests for ParquetDataSet."""

    def test_empty_dataframe(self, tmp_path: Path):
        """Test saving and loading empty DataFrame."""
        file_path = tmp_path / "empty.parquet"
        dataset = ParquetDataSet(path=str(file_path))
        
        empty_df = pd.DataFrame(columns=["a", "b", "c"])
        dataset.save(empty_df)
        
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, empty_df)

    def test_single_row_dataframe(self, tmp_path: Path):
        """Test saving and loading single-row DataFrame."""
        file_path = tmp_path / "single_row.parquet"
        dataset = ParquetDataSet(path=str(file_path))
        
        single_row_df = pd.DataFrame({"a": [1], "b": [2]})
        dataset.save(single_row_df)
        
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, single_row_df)

    def test_large_dataframe(self, tmp_path: Path):
        """Test with a larger DataFrame."""
        file_path = tmp_path / "large.parquet"
        dataset = ParquetDataSet(path=str(file_path), compression="zstd")
        
        # Create DataFrame with 10k rows
        large_df = pd.DataFrame({
            "id": range(10000),
            "value": range(10000, 20000),
            "category": (["A", "B", "C"] * 3334)[:10000],  # Fix: ensure exact length
        })
        
        dataset.save(large_df)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, large_df)

    def test_special_characters_in_columns(self, tmp_path: Path):
        """Test DataFrame with special characters in column names."""
        file_path = tmp_path / "special.parquet"
        dataset = ParquetDataSet(path=str(file_path))
        
        df = pd.DataFrame({
            "column with spaces": [1, 2, 3],
            "column-with-dashes": [4, 5, 6],
            "column.with.dots": [7, 8, 9],
        })
        
        dataset.save(df)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_various_data_types(self, tmp_path: Path):
        """Test DataFrame with various data types."""
        file_path = tmp_path / "types.parquet"
        dataset = ParquetDataSet(path=str(file_path))
        
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
            "bool_col": [True, False, True],
            "datetime_col": pd.date_range("2025-01-01", periods=3),
        })
        
        dataset.save(df)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, df)


class TestParquetDataSetIntegration:
    """Integration tests simulating real-world usage."""

    def test_pipeline_simulation(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test simulating a pipeline with multiple save/load cycles."""
        # Stage 1: Raw data
        raw_path = tmp_path / "raw.parquet"
        raw_dataset = ParquetDataSet(path=str(raw_path), compression="snappy")
        raw_dataset.save(sample_dataframe)
        
        # Stage 2: Load and transform
        loaded_df = raw_dataset.load()
        transformed_df = loaded_df.copy()
        transformed_df["age_group"] = pd.cut(
            transformed_df["age"],
            bins=[0, 30, 40, 100],
            labels=["young", "middle", "senior"],
        )
        
        # Stage 3: Save processed
        processed_path = tmp_path / "processed.parquet"
        processed_dataset = ParquetDataSet(
            path=str(processed_path),
            compression="zstd",
        )
        processed_dataset.save(transformed_df)
        
        # Verify final output
        final_df = processed_dataset.load()
        assert "age_group" in final_df.columns
        assert len(final_df) == len(sample_dataframe)

    def test_overwrite_existing_file(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test that saving overwrites existing file."""
        file_path = tmp_path / "overwrite.parquet"
        dataset = ParquetDataSet(path=str(file_path))
        
        # Save initial data
        dataset.save(sample_dataframe)
        initial_df = dataset.load()
        
        # Modify and save again
        modified_df = sample_dataframe.copy()
        modified_df["new_column"] = range(len(modified_df))
        dataset.save(modified_df)
        
        # Load and verify overwrite
        final_df = dataset.load()
        assert "new_column" in final_df.columns
        assert "new_column" not in initial_df.columns
