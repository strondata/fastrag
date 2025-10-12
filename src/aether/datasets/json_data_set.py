"""JSON DataSet for loading and saving JSON files."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class JsonDataSet:
    """DataSet for JSON file storage.
    
    Supports:
    - Standard JSON (dict/list)
    - JSON Lines format (newline-delimited JSON)
    - Pretty printing
    - pandas DataFrame serialization
    - Schema validation (optional)
    
    Examples:
        In catalog.yml:
        ```yaml
        user_config:
          type: JsonDataSet
          layer: raw
          options:
            path: /data/config.json
            indent: 2  # Pretty print
            
        events_log:
          type: JsonDataSet
          layer: raw
          options:
            path: /data/events.jsonl
            lines: true  # JSON Lines format
            
        dataframe_export:
          type: JsonDataSet
          layer: processed
          options:
            path: /data/results.json
            orient: records  # DataFrame to list of dicts
        ```
        
        In Python code:
        ```python
        # Save dict/list
        dataset = JsonDataSet(path="/data/config.json", indent=2)
        dataset.save({"key": "value", "nested": {"data": [1, 2, 3]}})
        
        # Load as dict
        config = dataset.load()
        
        # JSON Lines (streaming)
        dataset = JsonDataSet(path="/data/events.jsonl", lines=True)
        dataset.save([
            {"event": "click", "user": "alice"},
            {"event": "view", "user": "bob"}
        ])
        
        # DataFrame support
        dataset = JsonDataSet(path="/data/df.json", orient="records")
        dataset.save(df)  # DataFrame -> JSON
        loaded_df = dataset.load()  # JSON -> DataFrame (if pandas installed)
        ```
    """
    
    def __init__(
        self,
        path: str,
        lines: bool = False,
        indent: Optional[int] = None,
        orient: Optional[str] = None,
        encoding: str = "utf-8",
        ensure_ascii: bool = False,
        read_options: Optional[Dict[str, Any]] = None,
        write_options: Optional[Dict[str, Any]] = None,
    ):
        """Initialize JsonDataSet.
        
        Args:
            path: Path to JSON file (.json or .jsonl).
            lines: If True, use JSON Lines format (one JSON object per line).
                   Useful for streaming large datasets.
            indent: Number of spaces for pretty printing. None = compact.
            orient: pandas DataFrame orientation. Options:
                    - 'records': list of dicts [{col: val}, ...]
                    - 'split': dict with 'index', 'columns', 'data'
                    - 'index': dict of dicts {index: {col: val}}
                    - 'columns': dict of dicts {col: {index: val}}
                    - 'values': just the values array
            encoding: File encoding (default: utf-8).
            ensure_ascii: If False, allow non-ASCII characters in output.
            read_options: Additional options for json.load() or pd.read_json().
            write_options: Additional options for json.dump() or df.to_json().
        """
        self.path = Path(path)
        self.lines = lines
        self.indent = indent
        self.orient = orient
        self.encoding = encoding
        self.ensure_ascii = ensure_ascii
        self.read_options = read_options or {}
        self.write_options = write_options or {}
        
    def __repr__(self) -> str:
        """String representation."""
        mode = "JSON Lines" if self.lines else "JSON"
        indent_str = f", indent={self.indent}" if self.indent else ""
        orient_str = f", orient={self.orient}" if self.orient else ""
        return f"JsonDataSet(path={self.path}{indent_str}{orient_str}, mode={mode})"
        
    def load(self) -> Any:
        """Load data from JSON file.
        
        Returns:
            - If orient is specified and pandas available: DataFrame
            - If lines=True: List of dicts (one per line)
            - Otherwise: Dict or list (standard JSON)
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If JSON is malformed or pandas required but not installed.
        """
        if not self.path.exists():
            raise FileNotFoundError(
                f"JSON file not found: {self.path}"
            )
            
        # DataFrame loading (if orient specified)
        if self.orient is not None:
            if not PANDAS_AVAILABLE:
                raise ValueError(
                    "pandas is required when using 'orient' parameter. "
                    "Install it with: pip install pandas"
                )
            return self._load_dataframe()
            
        # JSON Lines loading
        if self.lines:
            return self._load_jsonlines()
            
        # Standard JSON loading
        return self._load_json()
        
    def _load_json(self) -> Union[Dict, List]:
        """Load standard JSON file."""
        with open(self.path, "r", encoding=self.encoding) as f:
            try:
                data = json.load(f, **self.read_options)
                return data
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in file {self.path}: {exc}"
                ) from exc
                
    def _load_jsonlines(self) -> List[Dict]:
        """Load JSON Lines file (newline-delimited JSON)."""
        data = []
        with open(self.path, "r", encoding=self.encoding) as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                try:
                    obj = json.loads(line, **self.read_options)
                    data.append(obj)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON on line {line_num} in {self.path}: {exc}"
                    ) from exc
        return data
        
    def _load_dataframe(self) -> "pd.DataFrame":
        """Load JSON as pandas DataFrame."""
        import pandas as pd
        
        try:
            if self.lines:
                # pandas read_json with lines=True
                df = pd.read_json(
                    self.path,
                    lines=True,
                    orient=self.orient,
                    encoding=self.encoding,
                    **self.read_options
                )
            else:
                df = pd.read_json(
                    self.path,
                    orient=self.orient,
                    encoding=self.encoding,
                    **self.read_options
                )
            return df
        except Exception as exc:
            raise ValueError(
                f"Failed to load JSON as DataFrame: {exc}"
            ) from exc
            
    def save(self, data: Any) -> None:
        """Save data to JSON file.
        
        Args:
            data: Data to save. Can be:
                  - dict or list (standard JSON)
                  - list of dicts (JSON Lines if lines=True)
                  - pandas DataFrame (if orient specified)
                  
        Raises:
            ValueError: If data type is incompatible or serialization fails.
        """
        # Create parent directories if needed
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # DataFrame saving
        if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            return self._save_dataframe(data)
            
        # JSON Lines saving
        if self.lines:
            if not isinstance(data, list):
                raise ValueError(
                    f"JSON Lines format requires a list, got {type(data).__name__}"
                )
            return self._save_jsonlines(data)
            
        # Standard JSON saving
        return self._save_json(data)
        
    def _save_json(self, data: Union[Dict, List]) -> None:
        """Save as standard JSON file."""
        if not isinstance(data, (dict, list)):
            raise ValueError(
                f"JSON data must be dict or list, got {type(data).__name__}"
            )
            
        with open(self.path, "w", encoding=self.encoding) as f:
            try:
                json.dump(
                    data,
                    f,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii,
                    **self.write_options
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Failed to serialize data to JSON: {exc}"
                ) from exc
                
    def _save_jsonlines(self, data: List[Dict]) -> None:
        """Save as JSON Lines file (newline-delimited JSON)."""
        with open(self.path, "w", encoding=self.encoding) as f:
            for obj in data:
                try:
                    line = json.dumps(
                        obj,
                        ensure_ascii=self.ensure_ascii,
                        **self.write_options
                    )
                    f.write(line + "\n")
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Failed to serialize object to JSON: {exc}"
                    ) from exc
                    
    def _save_dataframe(self, data: "pd.DataFrame") -> None:
        """Save pandas DataFrame as JSON."""
        import pandas as pd
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError(
                f"Expected pandas DataFrame, got {type(data).__name__}"
            )
            
        try:
            if self.lines:
                # Save as JSON Lines
                data.to_json(
                    self.path,
                    orient=self.orient or "records",
                    lines=True,
                    **self.write_options
                )
            else:
                # Standard JSON
                data.to_json(
                    self.path,
                    orient=self.orient or "records",
                    indent=self.indent,
                    **self.write_options
                )
        except Exception as exc:
            raise ValueError(
                f"Failed to save DataFrame as JSON: {exc}"
            ) from exc
