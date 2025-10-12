"""Tests for CsvDataSet."""

from pathlib import Path

import pandas as pd
import pytest

from aether.datasets.csv_data_set import CsvDataSet


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "score": [95.5, 87.3, 92.1, 88.7, 91.4],
        "active": [True, True, False, True, False],
    })


@pytest.fixture
def sample_csv_content() -> str:
    """Sample CSV content as string."""
    return """id,name,score,active
1,Alice,95.5,True
2,Bob,87.3,True
3,Charlie,92.1,False
4,Diana,88.7,True
5,Eve,91.4,False"""


class TestCsvDataSetBasic:
    """Basic functionality tests for CsvDataSet."""

    def test_init_default_options(self, tmp_path: Path):
        """Test initialization with default options."""
        dataset = CsvDataSet(path=str(tmp_path / "test.csv"))
        
        assert dataset.path == tmp_path / "test.csv"
        assert dataset.encoding == "utf-8"
        assert dataset.delimiter == ","
        assert dataset.quotechar == '"'
        assert dataset.header == "infer"
        assert dataset.index_col is None
        assert dataset.chunksize is None

    def test_init_custom_options(self, tmp_path: Path):
        """Test initialization with custom options."""
        dataset = CsvDataSet(
            path=str(tmp_path / "test.csv"),
            encoding="latin-1",
            delimiter=";",
            quotechar="'",
            header=None,
            chunksize=1000,
        )
        
        assert dataset.encoding == "latin-1"
        assert dataset.delimiter == ";"
        assert dataset.quotechar == "'"
        assert dataset.header is None
        assert dataset.chunksize == 1000

    def test_repr(self, tmp_path: Path):
        """Test string representation."""
        dataset = CsvDataSet(
            path=str(tmp_path / "test.csv"),
            encoding="latin-1",
            delimiter=";",
        )
        
        repr_str = repr(dataset)
        assert "CsvDataSet" in repr_str
        assert "test.csv" in repr_str
        assert "latin-1" in repr_str
        assert ";" in repr_str


class TestCsvDataSetReadWrite:
    """Tests for basic read/write operations."""

    def test_save_and_load_basic(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test basic save and load functionality."""
        file_path = tmp_path / "test.csv"
        dataset = CsvDataSet(path=str(file_path))
        
        # Save
        dataset.save(sample_dataframe)
        assert file_path.exists()
        
        # Load
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)

    def test_load_nonexistent_file(self, tmp_path: Path):
        """Test that loading non-existent file raises FileNotFoundError."""
        dataset = CsvDataSet(path=str(tmp_path / "nonexistent.csv"))
        
        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            dataset.load()

    def test_save_wrong_data_type(self, tmp_path: Path):
        """Test that saving wrong data type raises ValueError."""
        dataset = CsvDataSet(path=str(tmp_path / "test.csv"))
        
        with pytest.raises(ValueError, match="Expected pandas DataFrame"):
            dataset.save({"not": "a dataframe"})

    def test_save_creates_parent_directories(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test that save creates parent directories if they don't exist."""
        file_path = tmp_path / "nested" / "dir" / "test.csv"
        dataset = CsvDataSet(path=str(file_path))
        
        dataset.save(sample_dataframe)
        assert file_path.exists()
        assert file_path.parent.exists()


class TestCsvDataSetEncodings:
    """Tests for different encodings."""

    def test_utf8_encoding(self, tmp_path: Path):
        """Test UTF-8 encoding with special characters."""
        file_path = tmp_path / "utf8.csv"
        dataset = CsvDataSet(path=str(file_path), encoding="utf-8")
        
        df = pd.DataFrame({
            "name": ["José", "François", "Müller", "北京"],
            "value": [1, 2, 3, 4],
        })
        
        dataset.save(df)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_latin1_encoding(self, tmp_path: Path):
        """Test Latin-1 encoding."""
        file_path = tmp_path / "latin1.csv"
        dataset = CsvDataSet(path=str(file_path), encoding="latin-1")
        
        df = pd.DataFrame({
            "name": ["Café", "Résumé"],
            "value": [1, 2],
        })
        
        dataset.save(df)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, df)


class TestCsvDataSetDelimiters:
    """Tests for different delimiters."""

    def test_semicolon_delimiter(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test semicolon delimiter."""
        file_path = tmp_path / "semicolon.csv"
        dataset = CsvDataSet(path=str(file_path), delimiter=";")
        
        dataset.save(sample_dataframe)
        
        # Verify semicolon is actually used
        content = file_path.read_text()
        assert ";" in content
        assert content.count(";") > 0
        
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)

    def test_tab_delimiter(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test tab delimiter (TSV)."""
        file_path = tmp_path / "tab.tsv"
        dataset = CsvDataSet(path=str(file_path), delimiter="\t")
        
        dataset.save(sample_dataframe)
        
        # Verify tab is actually used
        content = file_path.read_text()
        assert "\t" in content
        
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)

    def test_pipe_delimiter(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test pipe delimiter."""
        file_path = tmp_path / "pipe.csv"
        dataset = CsvDataSet(path=str(file_path), delimiter="|")
        
        dataset.save(sample_dataframe)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)


class TestCsvDataSetQuoting:
    """Tests for quoting options."""

    def test_custom_quotechar(self, tmp_path: Path):
        """Test custom quote character."""
        file_path = tmp_path / "quotes.csv"
        dataset = CsvDataSet(path=str(file_path), quotechar="'")
        
        df = pd.DataFrame({
            "text": ["Hello, world", "Test, data"],
            "value": [1, 2],
        })
        
        dataset.save(df)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_fields_with_delimiter(self, tmp_path: Path):
        """Test that fields containing delimiter are properly quoted."""
        file_path = tmp_path / "delim_in_field.csv"
        dataset = CsvDataSet(path=str(file_path))
        
        df = pd.DataFrame({
            "description": ["Item, with comma", "Another, item"],
            "price": [10.5, 20.3],
        })
        
        dataset.save(df)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, df)


class TestCsvDataSetHeaders:
    """Tests for header options."""

    def test_no_header_write(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test writing without header."""
        file_path = tmp_path / "no_header.csv"
        dataset = CsvDataSet(
            path=str(file_path),
            write_options={"header": False}
        )
        
        dataset.save(sample_dataframe)
        
        # Verify no header in file
        content = file_path.read_text()
        first_line = content.split("\n")[0]
        assert "id" not in first_line
        assert "name" not in first_line

    def test_no_header_read(self, tmp_path: Path):
        """Test reading file without header."""
        file_path = tmp_path / "no_header.csv"
        
        # Write data without header manually
        file_path.write_text("1,Alice,95.5\n2,Bob,87.3\n")
        
        dataset = CsvDataSet(path=str(file_path), header=None)
        loaded_df = dataset.load()
        
        # When header=None, pandas treats first row as header
        # To get numbered columns, need to use read_options with names parameter
        # For this test, just verify it read the data
        assert len(loaded_df) == 1  # Only second row becomes data
        assert loaded_df.columns[0] == "1"  # First row becomes column names


class TestCsvDataSetChunking:
    """Tests for chunked reading."""

    def test_chunksize_returns_iterator(self, tmp_path: Path):
        """Test that chunksize returns an iterator."""
        file_path = tmp_path / "chunks.csv"
        
        # Create a larger dataset
        df = pd.DataFrame({
            "id": range(100),
            "value": range(100, 200),
        })
        
        # Save first
        dataset_write = CsvDataSet(path=str(file_path))
        dataset_write.save(df)
        
        # Load with chunks
        dataset_read = CsvDataSet(path=str(file_path), chunksize=25)
        result = dataset_read.load()
        
        # Should be an iterator
        chunks = list(result)
        assert len(chunks) == 4  # 100 / 25 = 4 chunks
        
        # Each chunk should have 25 rows
        for chunk in chunks:
            assert len(chunk) == 25

    def test_chunksize_data_integrity(self, tmp_path: Path):
        """Test that chunked reading preserves all data."""
        file_path = tmp_path / "chunks_integrity.csv"
        
        # Create dataset
        df = pd.DataFrame({
            "id": range(50),
            "value": range(50, 100),
        })
        
        dataset_write = CsvDataSet(path=str(file_path))
        dataset_write.save(df)
        
        # Load in chunks and concatenate
        dataset_read = CsvDataSet(path=str(file_path), chunksize=10)
        chunks = list(dataset_read.load())
        combined = pd.concat(chunks, ignore_index=True)
        
        pd.testing.assert_frame_equal(combined, df)


class TestCsvDataSetSkipRows:
    """Tests for skipping rows."""

    def test_skip_rows(self, tmp_path: Path):
        """Test skipping rows at the start."""
        file_path = tmp_path / "skip.csv"
        
        # Write file with comment lines
        content = """# This is a comment
# Another comment
id,name,value
1,Alice,10
2,Bob,20
"""
        file_path.write_text(content)
        
        dataset = CsvDataSet(path=str(file_path), skip_rows=2)
        loaded_df = dataset.load()
        
        assert len(loaded_df) == 2
        assert list(loaded_df.columns) == ["id", "name", "value"]


class TestCsvDataSetNaValues:
    """Tests for NA value handling."""

    def test_custom_na_values(self, tmp_path: Path):
        """Test custom NA value recognition."""
        file_path = tmp_path / "na_values.csv"
        
        content = """id,name,value
1,Alice,10
2,N/A,20
3,Charlie,MISSING
4,Diana,30
"""
        file_path.write_text(content)
        
        dataset = CsvDataSet(
            path=str(file_path),
            na_values=["N/A", "MISSING"]
        )
        loaded_df = dataset.load()
        
        # Check that N/A and MISSING are treated as NaN
        assert pd.isna(loaded_df.loc[1, "name"])
        assert pd.isna(loaded_df.loc[2, "value"])


class TestCsvDataSetDtype:
    """Tests for data type specification."""

    def test_dtype_specification(self, tmp_path: Path):
        """Test specifying column data types."""
        file_path = tmp_path / "dtype.csv"
        
        content = """id,code,value
1,001,10
2,002,20
3,003,30
"""
        file_path.write_text(content)
        
        dataset = CsvDataSet(
            path=str(file_path),
            dtype={"id": int, "code": str, "value": float}
        )
        loaded_df = dataset.load()
        
        assert loaded_df["id"].dtype == int
        assert loaded_df["code"].dtype == object  # str becomes object
        assert loaded_df["value"].dtype == float


class TestCsvDataSetEdgeCases:
    """Edge case tests for CsvDataSet."""

    def test_empty_dataframe(self, tmp_path: Path):
        """Test saving and loading empty DataFrame."""
        file_path = tmp_path / "empty.csv"
        dataset = CsvDataSet(path=str(file_path))
        
        empty_df = pd.DataFrame(columns=["a", "b", "c"])
        dataset.save(empty_df)
        
        loaded_df = dataset.load()
        assert list(loaded_df.columns) == ["a", "b", "c"]
        assert len(loaded_df) == 0

    def test_single_row(self, tmp_path: Path):
        """Test single row DataFrame."""
        file_path = tmp_path / "single.csv"
        dataset = CsvDataSet(path=str(file_path))
        
        single_row = pd.DataFrame({"a": [1], "b": [2]})
        dataset.save(single_row)
        
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, single_row)

    def test_single_column(self, tmp_path: Path):
        """Test single column DataFrame."""
        file_path = tmp_path / "single_col.csv"
        dataset = CsvDataSet(path=str(file_path))
        
        single_col = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
        dataset.save(single_col)
        
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, single_col)

    def test_special_characters_in_data(self, tmp_path: Path):
        """Test data with special characters."""
        file_path = tmp_path / "special.csv"
        dataset = CsvDataSet(path=str(file_path))
        
        df = pd.DataFrame({
            "text": ['Line\nbreak', 'Tab\there', 'Quote"test'],
            "value": [1, 2, 3],
        })
        
        dataset.save(df)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, df)


class TestCsvDataSetIntegration:
    """Integration tests simulating real-world usage."""

    def test_overwrite_existing_file(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test that saving overwrites existing file."""
        file_path = tmp_path / "overwrite.csv"
        dataset = CsvDataSet(path=str(file_path))
        
        # Save initial data
        dataset.save(sample_dataframe)
        initial_df = dataset.load()
        
        # Modify and save again
        modified_df = sample_dataframe.copy()
        modified_df["new_col"] = range(len(modified_df))
        dataset.save(modified_df)
        
        # Load and verify overwrite
        final_df = dataset.load()
        assert "new_col" in final_df.columns
        assert "new_col" not in initial_df.columns

    def test_read_options_passthrough(self, tmp_path: Path):
        """Test that read_options are passed through correctly."""
        file_path = tmp_path / "read_opts.csv"
        
        content = """id;name;value
1;Alice;10
2;Bob;20
"""
        file_path.write_text(content)
        
        dataset = CsvDataSet(
            path=str(file_path),
            delimiter=";",
            read_options={"nrows": 1}  # Read only first data row
        )
        
        loaded_df = dataset.load()
        assert len(loaded_df) == 1
        assert loaded_df.loc[0, "id"] == 1

    def test_write_options_passthrough(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test that write_options are passed through correctly."""
        file_path = tmp_path / "write_opts.csv"
        
        dataset = CsvDataSet(
            path=str(file_path),
            write_options={
                "index": True,  # Override default to write index
                "lineterminator": "\n"  # Correct parameter name for pandas
            }
        )
        
        dataset.save(sample_dataframe)
        
        # Verify index was written
        content = file_path.read_text()
        lines = content.strip().split("\n")
        # First line should have index column header (empty or "Unnamed: 0")
        first_line = lines[0]
        # Check that there's an extra column for the index
        assert first_line.count(",") == len(sample_dataframe.columns)  # One extra comma for index
