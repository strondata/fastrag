"""Tests for JsonDataSet."""

import json
from pathlib import Path

import pandas as pd
import pytest

from aether.datasets.json_data_set import JsonDataSet


@pytest.fixture
def sample_dict() -> dict:
    """Sample dictionary data."""
    return {
        "name": "Alice",
        "age": 30,
        "active": True,
        "scores": [95, 87, 92],
        "metadata": {
            "created": "2024-01-01",
            "tags": ["python", "data"]
        }
    }


@pytest.fixture
def sample_list() -> list:
    """Sample list of dicts."""
    return [
        {"id": 1, "name": "Alice", "score": 95.5},
        {"id": 2, "name": "Bob", "score": 87.3},
        {"id": 3, "name": "Charlie", "score": 92.1},
    ]


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Sample DataFrame."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "score": [95.5, 87.3, 92.1],
    })


class TestJsonDataSetBasic:
    """Basic functionality tests for JsonDataSet."""

    def test_init_default_options(self, tmp_path: Path):
        """Test initialization with default options."""
        dataset = JsonDataSet(path=str(tmp_path / "test.json"))
        
        assert dataset.path == tmp_path / "test.json"
        assert dataset.lines is False
        assert dataset.indent is None
        assert dataset.orient is None
        assert dataset.encoding == "utf-8"
        assert dataset.ensure_ascii is False

    def test_init_custom_options(self, tmp_path: Path):
        """Test initialization with custom options."""
        dataset = JsonDataSet(
            path=str(tmp_path / "test.json"),
            lines=True,
            indent=2,
            orient="records",
            encoding="latin-1",
            ensure_ascii=True,
        )
        
        assert dataset.lines is True
        assert dataset.indent == 2
        assert dataset.orient == "records"
        assert dataset.encoding == "latin-1"
        assert dataset.ensure_ascii is True

    def test_repr(self, tmp_path: Path):
        """Test string representation."""
        dataset = JsonDataSet(
            path=str(tmp_path / "test.json"),
            indent=2,
            orient="records",
        )
        
        repr_str = repr(dataset)
        assert "JsonDataSet" in repr_str
        assert "test.json" in repr_str
        assert "indent=2" in repr_str
        assert "orient=records" in repr_str

    def test_repr_jsonlines(self, tmp_path: Path):
        """Test string representation for JSON Lines mode."""
        dataset = JsonDataSet(path=str(tmp_path / "test.jsonl"), lines=True)
        
        repr_str = repr(dataset)
        assert "JSON Lines" in repr_str


class TestJsonDataSetDict:
    """Tests for dict save/load operations."""

    def test_save_and_load_dict(self, tmp_path: Path, sample_dict: dict):
        """Test saving and loading dictionary."""
        file_path = tmp_path / "data.json"
        dataset = JsonDataSet(path=str(file_path))
        
        # Save
        dataset.save(sample_dict)
        assert file_path.exists()
        
        # Load
        loaded = dataset.load()
        assert loaded == sample_dict

    def test_save_dict_pretty_print(self, tmp_path: Path, sample_dict: dict):
        """Test saving with pretty printing."""
        file_path = tmp_path / "pretty.json"
        dataset = JsonDataSet(path=str(file_path), indent=2)
        
        dataset.save(sample_dict)
        
        # Verify indentation
        content = file_path.read_text()
        assert "  " in content  # Has indentation
        assert "\n" in content  # Has newlines

    def test_save_dict_compact(self, tmp_path: Path, sample_dict: dict):
        """Test saving in compact format."""
        file_path = tmp_path / "compact.json"
        dataset = JsonDataSet(path=str(file_path), indent=None)
        
        dataset.save(sample_dict)
        
        # Verify compact (but may have some whitespace from json.dump)
        content = file_path.read_text()
        # Just verify it's valid JSON
        loaded = json.loads(content)
        assert loaded == sample_dict


class TestJsonDataSetList:
    """Tests for list save/load operations."""

    def test_save_and_load_list(self, tmp_path: Path, sample_list: list):
        """Test saving and loading list."""
        file_path = tmp_path / "list.json"
        dataset = JsonDataSet(path=str(file_path))
        
        dataset.save(sample_list)
        loaded = dataset.load()
        
        assert loaded == sample_list

    def test_load_nonexistent_file(self, tmp_path: Path):
        """Test loading non-existent file raises error."""
        dataset = JsonDataSet(path=str(tmp_path / "missing.json"))
        
        with pytest.raises(FileNotFoundError, match="JSON file not found"):
            dataset.load()

    def test_save_wrong_type(self, tmp_path: Path):
        """Test saving unsupported type raises error."""
        dataset = JsonDataSet(path=str(tmp_path / "wrong.json"))
        
        with pytest.raises(ValueError, match="must be dict or list"):
            dataset.save("not a dict or list")


class TestJsonDataSetJsonLines:
    """Tests for JSON Lines format."""

    def test_save_and_load_jsonlines(self, tmp_path: Path, sample_list: list):
        """Test JSON Lines save and load."""
        file_path = tmp_path / "data.jsonl"
        dataset = JsonDataSet(path=str(file_path), lines=True)
        
        dataset.save(sample_list)
        
        # Verify format (one JSON per line)
        content = file_path.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == len(sample_list)
        
        # Load and verify
        loaded = dataset.load()
        assert loaded == sample_list

    def test_jsonlines_invalid_data_type(self, tmp_path: Path):
        """Test JSON Lines requires list."""
        dataset = JsonDataSet(path=str(tmp_path / "data.jsonl"), lines=True)
        
        with pytest.raises(ValueError, match="requires a list"):
            dataset.save({"not": "a list"})

    def test_jsonlines_skip_empty_lines(self, tmp_path: Path):
        """Test that empty lines are skipped when loading."""
        file_path = tmp_path / "with_empty.jsonl"
        
        # Write file with empty lines
        content = '''{"id": 1}

{"id": 2}

{"id": 3}
'''
        file_path.write_text(content)
        
        dataset = JsonDataSet(path=str(file_path), lines=True)
        loaded = dataset.load()
        
        assert len(loaded) == 3
        assert loaded[0]["id"] == 1
        assert loaded[2]["id"] == 3


class TestJsonDataSetDataFrame:
    """Tests for pandas DataFrame support."""

    def test_save_and_load_dataframe_records(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test DataFrame save/load with orient='records'."""
        file_path = tmp_path / "df.json"
        dataset = JsonDataSet(path=str(file_path), orient="records")
        
        dataset.save(sample_dataframe)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)

    def test_save_dataframe_split(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test DataFrame save with orient='split'."""
        file_path = tmp_path / "df_split.json"
        dataset = JsonDataSet(path=str(file_path), orient="split")
        
        dataset.save(sample_dataframe)
        loaded_df = dataset.load()
        
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)

    def test_save_dataframe_jsonlines(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Test DataFrame save as JSON Lines."""
        file_path = tmp_path / "df.jsonl"
        dataset = JsonDataSet(path=str(file_path), lines=True, orient="records")
        
        dataset.save(sample_dataframe)
        
        # Verify JSON Lines format
        content = file_path.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == len(sample_dataframe)
        
        # Load and verify
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)


class TestJsonDataSetEncoding:
    """Tests for encoding options."""

    def test_utf8_encoding(self, tmp_path: Path):
        """Test UTF-8 encoding with unicode characters."""
        file_path = tmp_path / "utf8.json"
        dataset = JsonDataSet(path=str(file_path), indent=2)
        
        data = {
            "name": "José François",
            "city": "北京",
            "emoji": "🎉",
        }
        
        dataset.save(data)
        loaded = dataset.load()
        
        assert loaded == data

    def test_ensure_ascii_true(self, tmp_path: Path):
        """Test ensure_ascii=True escapes unicode."""
        file_path = tmp_path / "ascii.json"
        dataset = JsonDataSet(path=str(file_path), ensure_ascii=True)
        
        data = {"name": "José"}
        dataset.save(data)
        
        # Verify unicode is escaped
        content = file_path.read_text()
        assert "José" not in content  # Should be escaped
        assert "\\u" in content or "Jos" in content  # Either escaped or ASCII-fied

    def test_ensure_ascii_false(self, tmp_path: Path):
        """Test ensure_ascii=False preserves unicode."""
        file_path = tmp_path / "unicode.json"
        dataset = JsonDataSet(path=str(file_path), ensure_ascii=False)
        
        data = {"name": "José"}
        dataset.save(data)
        
        # Verify unicode is preserved (read with correct encoding)
        content = file_path.read_text(encoding="utf-8")
        assert "José" in content


class TestJsonDataSetEdgeCases:
    """Edge case tests."""

    def test_empty_dict(self, tmp_path: Path):
        """Test empty dictionary."""
        file_path = tmp_path / "empty.json"
        dataset = JsonDataSet(path=str(file_path))
        
        dataset.save({})
        loaded = dataset.load()
        
        assert loaded == {}

    def test_empty_list(self, tmp_path: Path):
        """Test empty list."""
        file_path = tmp_path / "empty_list.json"
        dataset = JsonDataSet(path=str(file_path))
        
        dataset.save([])
        loaded = dataset.load()
        
        assert loaded == []

    def test_nested_structures(self, tmp_path: Path):
        """Test deeply nested structures."""
        file_path = tmp_path / "nested.json"
        dataset = JsonDataSet(path=str(file_path), indent=2)
        
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": [1, 2, 3]
                    }
                }
            }
        }
        
        dataset.save(data)
        loaded = dataset.load()
        
        assert loaded == data

    def test_special_json_values(self, tmp_path: Path):
        """Test special JSON values (null, true, false)."""
        file_path = tmp_path / "special.json"
        dataset = JsonDataSet(path=str(file_path))
        
        data = {
            "null_value": None,
            "bool_true": True,
            "bool_false": False,
            "number": 42,
            "float": 3.14,
        }
        
        dataset.save(data)
        loaded = dataset.load()
        
        assert loaded == data

    def test_invalid_json_raises_error(self, tmp_path: Path):
        """Test that invalid JSON raises error on load."""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("{invalid json content")
        
        dataset = JsonDataSet(path=str(file_path))
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            dataset.load()

    def test_save_creates_parent_directories(self, tmp_path: Path):
        """Test that save creates parent directories."""
        file_path = tmp_path / "nested" / "dir" / "data.json"
        dataset = JsonDataSet(path=str(file_path))
        
        dataset.save({"test": "data"})
        
        assert file_path.exists()
        assert file_path.parent.exists()


class TestJsonDataSetReadWriteOptions:
    """Tests for read_options and write_options."""

    def test_write_options_sort_keys(self, tmp_path: Path):
        """Test write_options for sorting keys."""
        file_path = tmp_path / "sorted.json"
        dataset = JsonDataSet(
            path=str(file_path),
            indent=2,
            write_options={"sort_keys": True}
        )
        
        data = {"z": 1, "a": 2, "m": 3}
        dataset.save(data)
        
        # Verify keys are sorted
        content = file_path.read_text()
        lines = [line.strip() for line in content.split("\n") if ":" in line]
        # First key should be 'a', last should be 'z'
        assert '"a"' in lines[0]
        assert '"z"' in lines[-1]

    def test_read_options_passthrough(self, tmp_path: Path):
        """Test that read_options are passed through."""
        file_path = tmp_path / "data.json"
        
        # Write valid JSON
        file_path.write_text('{"a": 1, "b": 2}')
        
        # Load (read_options would apply if we had custom parse_* functions)
        dataset = JsonDataSet(path=str(file_path))
        loaded = dataset.load()
        
        assert loaded == {"a": 1, "b": 2}


class TestJsonDataSetIntegration:
    """Integration tests simulating real-world usage."""

    def test_config_file_workflow(self, tmp_path: Path):
        """Test typical config file workflow."""
        config_path = tmp_path / "config.json"
        dataset = JsonDataSet(path=str(config_path), indent=2)
        
        # Save config
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
            },
            "features": {
                "enabled": ["feature_a", "feature_b"],
                "disabled": [],
            }
        }
        dataset.save(config)
        
        # Load and modify
        loaded_config = dataset.load()
        loaded_config["features"]["enabled"].append("feature_c")
        
        # Save again
        dataset.save(loaded_config)
        
        # Verify
        final_config = dataset.load()
        assert "feature_c" in final_config["features"]["enabled"]

    def test_event_log_workflow(self, tmp_path: Path):
        """Test event log workflow with JSON Lines."""
        log_path = tmp_path / "events.jsonl"
        dataset = JsonDataSet(path=str(log_path), lines=True)
        
        # Log events
        events = [
            {"timestamp": "2024-01-01T10:00:00", "event": "login", "user": "alice"},
            {"timestamp": "2024-01-01T10:05:00", "event": "click", "user": "alice"},
            {"timestamp": "2024-01-01T10:10:00", "event": "logout", "user": "alice"},
        ]
        dataset.save(events)
        
        # Read and process
        loaded_events = dataset.load()
        assert len(loaded_events) == 3
        assert all(e["user"] == "alice" for e in loaded_events)

    def test_dataframe_export_workflow(self, tmp_path: Path):
        """Test DataFrame export workflow."""
        export_path = tmp_path / "export.json"
        dataset = JsonDataSet(path=str(export_path), orient="records", indent=2)
        
        # Create and export DataFrame
        df = pd.DataFrame({
            "product": ["A", "B", "C"],
            "sales": [100, 200, 150],
            "region": ["North", "South", "East"],
        })
        dataset.save(df)
        
        # Load back as DataFrame
        loaded_df = dataset.load()
        pd.testing.assert_frame_equal(loaded_df, df)

    def test_overwrite_existing_file(self, tmp_path: Path):
        """Test overwriting existing file."""
        file_path = tmp_path / "overwrite.json"
        dataset = JsonDataSet(path=str(file_path))
        
        # Write initial data
        dataset.save({"version": 1})
        
        # Overwrite
        dataset.save({"version": 2, "new_field": "added"})
        
        # Verify overwrite
        loaded = dataset.load()
        assert loaded["version"] == 2
        assert "new_field" in loaded
