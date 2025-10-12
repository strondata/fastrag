"""CsvDataSet implementation for reading and writing CSV files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator, Literal, Optional, Union

from aether.core.interfaces import IDataSet


class CsvDataSet(IDataSet):
    """Dataset for reading and writing CSV (Comma-Separated Values) files.
    
    Supports various encodings, delimiters, quoting options, and chunked reading
    for large files.
    
    Args:
        path: Path to the CSV file.
        encoding: Character encoding (e.g., 'utf-8', 'latin-1', 'cp1252').
            Defaults to 'utf-8'.
        delimiter: Field delimiter character. Defaults to ','.
        quotechar: Character used to quote fields containing special characters.
            Defaults to '"'.
        header: Row number(s) to use as column names. Use 'infer' to auto-detect,
            None for no header, or int for specific row. Defaults to 'infer'.
        index_col: Column to use as row index. Defaults to None (no index).
        chunksize: Number of rows per chunk for iterative reading. If set,
            load() returns an iterator. Defaults to None (read all at once).
        skip_rows: Number of rows to skip at the start. Defaults to 0.
        na_values: Additional strings to recognize as NA/NaN. Defaults to None.
        dtype: Data type for columns. Dict or single type. Defaults to None (infer).
        read_options: Additional options passed to pd.read_csv().
        write_options: Additional options passed to df.to_csv().
        
    Example:
        ```yaml
        # catalog.yml
        sales_data:
          type: CsvDataSet
          layer: raw
          options:
            path: "data/sales.csv"
            encoding: "utf-8"
            delimiter: ","
        
        legacy_data:
          type: CsvDataSet
          layer: raw
          options:
            path: "data/legacy.csv"
            encoding: "latin-1"
            delimiter: ";"
            quotechar: "'"
        ```
    
    Example:
        ```python
        # Python usage
        dataset = CsvDataSet(
            path="data/large_file.csv",
            chunksize=10000  # Read in 10k row chunks
        )
        for chunk in dataset.load():
            process_chunk(chunk)
        ```
    """

    def __init__(
        self,
        path: str,
        encoding: str = "utf-8",
        delimiter: str = ",",
        quotechar: str = '"',
        header: Union[Literal["infer"], int, None] = "infer",
        index_col: Optional[Union[int, str]] = None,
        chunksize: Optional[int] = None,
        skip_rows: Optional[int] = None,
        na_values: Optional[list[str]] = None,
        dtype: Optional[Union[str, dict]] = None,
        read_options: Optional[dict[str, Any]] = None,
        write_options: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CsvDataSet.
        
        Args:
            path: Path to CSV file.
            encoding: Character encoding.
            delimiter: Field delimiter.
            quotechar: Quote character.
            header: Header row specification.
            index_col: Column to use as index.
            chunksize: Chunk size for iterative reading.
            skip_rows: Rows to skip at start.
            na_values: Additional NA values.
            dtype: Column data types.
            read_options: Additional read parameters.
            write_options: Additional write parameters.
            **kwargs: Additional options (ignored for flexibility).
        """
        self.path = Path(path)
        self.encoding = encoding
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.header = header
        self.index_col = index_col
        self.chunksize = chunksize
        self.skip_rows = skip_rows
        self.na_values = na_values or []
        self.dtype = dtype
        self.read_options = read_options or {}
        self.write_options = write_options or {}

    def load(self) -> Union[Any, Iterator[Any]]:
        """Load data from CSV file.
        
        Returns:
            DataFrame if chunksize is None, otherwise an iterator of DataFrames.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ImportError: If pandas is not installed.
            ValueError: If the file format is invalid.
        """
        if not self.path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.path}")
        
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "pandas is required for CsvDataSet. "
                "Install it with: pip install pandas"
            ) from exc
        
        # Build read options
        options = {
            "encoding": self.encoding,
            "delimiter": self.delimiter,
            "quotechar": self.quotechar,
            "header": self.header if self.header != "infer" else 0,
            "index_col": self.index_col,
            "skiprows": self.skip_rows,
            "na_values": self.na_values if self.na_values else None,
            "dtype": self.dtype,
            "chunksize": self.chunksize,
            **self.read_options,
        }
        
        # Remove None values for cleaner API
        options = {k: v for k, v in options.items() if v is not None}
        
        try:
            result = pd.read_csv(self.path, **options)
            
            # If chunksize is set, result is an iterator
            if self.chunksize:
                return result  # Return iterator
            else:
                return result  # Return DataFrame
                
        except Exception as exc:
            raise ValueError(
                f"Failed to load CSV file: {exc}"
            ) from exc

    def save(self, data: Any) -> None:
        """Save data to CSV file.
        
        Args:
            data: DataFrame to save.
            
        Raises:
            ImportError: If pandas is not installed.
            ValueError: If data type is incompatible.
        """
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "pandas is required for CsvDataSet. "
                "Install it with: pip install pandas"
            ) from exc
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError(
                f"Expected pandas DataFrame, got {type(data).__name__}"
            )
        
        # Create parent directories if needed
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build write options
        options = {
            "encoding": self.encoding,
            "sep": self.delimiter,
            "quotechar": self.quotechar,
            "index": False,  # Don't write index by default
            "header": True,  # Write header by default
            **self.write_options,
        }
        
        try:
            data.to_csv(self.path, **options)
        except Exception as exc:
            raise ValueError(
                f"Failed to save CSV file: {exc}"
            ) from exc

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CsvDataSet(path='{self.path}', encoding='{self.encoding}', "
            f"delimiter='{self.delimiter}')"
        )
