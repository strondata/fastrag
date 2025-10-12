"""ParquetDataSet implementation for reading and writing Parquet files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

from aether.core.interfaces import IDataSet


class ParquetDataSet(IDataSet):
    """Dataset for reading and writing Parquet files.
    
    Supports both pandas and polars DataFrames with configurable compression,
    partitioning, and schema validation.
    
    Args:
        path: Path to the Parquet file or directory (for partitioned datasets).
        engine: Engine to use ('pandas' or 'polars'). Defaults to 'pandas'.
        compression: Compression codec ('snappy', 'gzip', 'brotli', 'lz4', 'zstd', None).
            Defaults to 'snappy'.
        partition_cols: List of column names to partition by (write only).
        schema: Optional Parquet schema for validation.
        read_options: Additional options passed to read function.
        write_options: Additional options passed to write function.
        
    Example:
        ```yaml
        # catalog.yml
        employee_data:
          type: ParquetDataSet
          layer: processed
          options:
            path: "data/employees.parquet"
            compression: "snappy"
            engine: "pandas"
        
        partitioned_data:
          type: ParquetDataSet
          layer: curated
          options:
            path: "data/sales/"
            partition_cols: ["year", "month"]
            compression: "zstd"
        ```
    
    Example:
        ```python
        # Python usage
        dataset = ParquetDataSet(
            path="data/output.parquet",
            compression="zstd",
            engine="pandas"
        )
        dataset.save(df)
        loaded_df = dataset.load()
        ```
    """

    def __init__(
        self,
        path: str,
        engine: Literal["pandas", "polars"] = "pandas",
        compression: Optional[Literal["snappy", "gzip", "brotli", "lz4", "zstd"]] = "snappy",
        partition_cols: Optional[list[str]] = None,
        schema: Optional[Any] = None,
        read_options: Optional[Dict[str, Any]] = None,
        write_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ParquetDataSet.
        
        Args:
            path: Path to Parquet file or directory.
            engine: 'pandas' or 'polars'.
            compression: Compression codec or None.
            partition_cols: Columns to partition by.
            schema: Parquet schema for validation.
            read_options: Additional read parameters.
            write_options: Additional write parameters.
            **kwargs: Additional options (ignored for flexibility).
        """
        self.path = Path(path)
        self.engine = engine
        self.compression = compression
        self.partition_cols = partition_cols or []
        self.schema = schema
        self.read_options = read_options or {}
        self.write_options = write_options or {}
        
        # Validate engine
        if engine not in ("pandas", "polars"):
            raise ValueError(f"Unsupported engine '{engine}'. Must be 'pandas' or 'polars'.")

    def load(self) -> Any:
        """Load data from Parquet file.
        
        Returns:
            DataFrame (pandas or polars depending on engine).
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ImportError: If the required engine is not installed.
            ValueError: If the file format is invalid.
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Parquet file not found: {self.path}")
        
        if self.engine == "pandas":
            return self._load_pandas()
        else:
            return self._load_polars()

    def save(self, data: Any) -> None:
        """Save data to Parquet file.
        
        Args:
            data: DataFrame to save (pandas or polars).
            
        Raises:
            ImportError: If the required engine is not installed.
            ValueError: If data type is incompatible.
        """
        # Create parent directories if needed
        if self.partition_cols:
            # Partitioned writes create subdirectories
            self.path.mkdir(parents=True, exist_ok=True)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.engine == "pandas":
            self._save_pandas(data)
        else:
            self._save_polars(data)

    def _load_pandas(self) -> Any:
        """Load data using pandas."""
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "pandas is required for ParquetDataSet with engine='pandas'. "
                "Install it with: pip install pandas pyarrow"
            ) from exc
        
        # Merge read_options with defaults
        options = {
            "engine": "pyarrow",  # Use pyarrow for better performance
            **self.read_options,
        }
        
        try:
            if self.path.is_dir():
                # Read partitioned dataset
                return pd.read_parquet(self.path, **options)
            else:
                # Read single file
                return pd.read_parquet(self.path, **options)
        except Exception as exc:
            raise ValueError(
                f"Failed to load Parquet file with pandas: {exc}"
            ) from exc

    def _save_pandas(self, data: Any) -> None:
        """Save data using pandas."""
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "pandas is required for ParquetDataSet with engine='pandas'. "
                "Install it with: pip install pandas pyarrow"
            ) from exc
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError(
                f"Expected pandas DataFrame, got {type(data).__name__}. "
                "Set engine='polars' if using polars DataFrames."
            )
        
        # Merge write_options with defaults
        options = {
            "engine": "pyarrow",
            "compression": self.compression,
            "index": False,  # Don't write index by default
            **self.write_options,
        }
        
        # Handle partitioning
        if self.partition_cols:
            options["partition_cols"] = self.partition_cols
            # For partitioned writes, path should be a directory
            data.to_parquet(self.path, **options)
        else:
            # Single file write
            data.to_parquet(self.path, **options)

    def _load_polars(self) -> Any:
        """Load data using polars."""
        try:
            import polars as pl
        except ImportError as exc:
            raise ImportError(
                "polars is required for ParquetDataSet with engine='polars'. "
                "Install it with: pip install polars"
            ) from exc
        
        try:
            if self.path.is_dir():
                # Read partitioned dataset
                # Polars reads Hive-style partitioned datasets automatically
                return pl.read_parquet(self.path / "**/*.parquet", **self.read_options)
            else:
                # Read single file
                return pl.read_parquet(self.path, **self.read_options)
        except Exception as exc:
            raise ValueError(
                f"Failed to load Parquet file with polars: {exc}"
            ) from exc

    def _save_polars(self, data: Any) -> None:
        """Save data using polars."""
        try:
            import polars as pl
        except ImportError as exc:
            raise ImportError(
                "polars is required for ParquetDataSet with engine='polars'. "
                "Install it with: pip install polars"
            ) from exc
        
        # Convert to polars DataFrame if needed
        if not isinstance(data, pl.DataFrame):
            try:
                # Try to convert from pandas
                import pandas as pd
                if isinstance(data, pd.DataFrame):
                    data = pl.from_pandas(data)
                else:
                    raise ValueError(
                        f"Expected polars DataFrame or pandas DataFrame, got {type(data).__name__}"
                    )
            except ImportError:
                raise ValueError(
                    f"Expected polars DataFrame, got {type(data).__name__}"
                )
        
        # Merge write_options with defaults
        options = {
            "compression": self.compression,
            **self.write_options,
        }
        
        # Handle partitioning
        if self.partition_cols:
            # Polars doesn't have built-in partitioning like pandas
            # We need to write manually by grouping
            for partition_key, partition_df in data.partition_by(self.partition_cols, as_dict=True).items():
                # Create partition path
                if isinstance(partition_key, tuple):
                    partition_parts = [f"{col}={val}" for col, val in zip(self.partition_cols, partition_key)]
                else:
                    partition_parts = [f"{self.partition_cols[0]}={partition_key}"]
                
                partition_path = self.path / "/".join(partition_parts) / "data.parquet"
                partition_path.parent.mkdir(parents=True, exist_ok=True)
                partition_df.write_parquet(partition_path, **options)
        else:
            # Single file write
            data.write_parquet(self.path, **options)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ParquetDataSet(path='{self.path}', engine='{self.engine}', "
            f"compression='{self.compression}')"
        )
