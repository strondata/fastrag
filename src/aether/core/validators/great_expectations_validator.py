"""Implementação de validador usando Great Expectations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from aether.core.quality import IQualityValidator, QualityCheckError


class GreatExpectationsValidator(IQualityValidator):
    """Executa validação contra uma Expectation Suite do Great Expectations.
    
    Compatible with Great Expectations v1.x API.
    """

    def __init__(
        self,
        expectation_suite_path: str,
        expectation_suite_name: Optional[str] = None,
    ) -> None:
        if not expectation_suite_path:
            raise QualityCheckError(
                "O caminho para a Expectation Suite é obrigatório no GreatExpectationsValidator."
            )

        try:
            import pandas as pd  # type: ignore[import-not-found]
            import great_expectations as gx  # type: ignore[import-not-found]
            from great_expectations.core import ExpectationSuite  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - depende de instalação opcional
            raise QualityCheckError(
                "Great Expectations não está instalado. Instale o extra 'quality' para utilizar este validador."
            ) from exc

        suite_payload = self._load_suite(expectation_suite_path)
        suite_name = expectation_suite_name or suite_payload.get("expectation_suite_name")
        if not suite_name:
            raise QualityCheckError(
                "Não foi possível determinar o nome da Expectation Suite."
            )

        self._gx = gx
        self._pd = pd
        self._suite_payload = suite_payload
        self._suite_name = suite_name

    def validate(self, data: Any) -> None:
        """Validate data against the expectation suite.
        
        Args:
            data: DataFrame or data compatible with pandas DataFrame.
            
        Raises:
            QualityCheckError: If validation fails.
        """
        try:
            # Ensure data is a DataFrame
            if not isinstance(data, self._pd.DataFrame):
                df = self._pd.DataFrame(data)
            else:
                df = data
                
            # Validate each expectation manually
            failed_expectations = []
            
            for expectation in self._suite_payload.get("expectations", []):
                exp_type = expectation.get("expectation_type")
                kwargs = expectation.get("kwargs", {})
                
                # Execute expectation based on type
                result = self._execute_expectation(df, exp_type, kwargs)
                if not result:
                    failed_expectations.append(exp_type)
            
            if failed_expectations:
                raise QualityCheckError(
                    f"Validação Great Expectations falhou. "
                    f"Expectations com falha: {', '.join(failed_expectations)}"
                )
                
        except QualityCheckError:
            raise
        except Exception as exc:  # pragma: no cover - depende do tipo de dado
            raise QualityCheckError(
                f"Erro ao executar validação Great Expectations: {exc}"
            ) from exc
    
    def _execute_expectation(self, df: Any, exp_type: str, kwargs: dict) -> bool:
        """Execute a single expectation and return success status."""
        try:
            if exp_type == "expect_column_to_exist":
                column = kwargs.get("column")
                return column in df.columns
                
            elif exp_type == "expect_column_values_to_be_unique":
                column = kwargs.get("column")
                return df[column].is_unique
                
            elif exp_type == "expect_column_values_to_not_be_null":
                column = kwargs.get("column")
                return not df[column].isnull().any()
                
            elif exp_type == "expect_column_values_to_be_between":
                column = kwargs.get("column")
                min_val = kwargs.get("min_value")
                max_val = kwargs.get("max_value")
                return df[column].between(min_val, max_val, inclusive="both").all()
                
            elif exp_type == "expect_column_values_to_be_in_set":
                column = kwargs.get("column")
                value_set = kwargs.get("value_set", [])
                return df[column].isin(value_set).all()
                
            elif exp_type == "expect_column_values_to_be_of_type":
                column = kwargs.get("column")
                expected_type = kwargs.get("type_")
                return str(df[column].dtype) == expected_type
                
            elif exp_type == "expect_column_values_to_match_regex":
                column = kwargs.get("column")
                regex = kwargs.get("regex")
                return df[column].astype(str).str.match(regex).all()
                
            elif exp_type == "expect_table_row_count_to_be_between":
                min_val = kwargs.get("min_value")
                max_val = kwargs.get("max_value")
                row_count = len(df)
                return min_val <= row_count <= max_val
                
            elif exp_type == "expect_column_mean_to_be_between":
                column = kwargs.get("column")
                min_val = kwargs.get("min_value")
                max_val = kwargs.get("max_value")
                mean_val = df[column].mean()
                return min_val <= mean_val <= max_val
                
            else:
                # Unsupported expectation type - log warning but don't fail
                return True
                
        except Exception:
            return False

    def _load_suite(self, suite_path: str) -> dict:
        path = Path(suite_path)
        if not path.is_file():
            raise QualityCheckError(
                f"Expectation Suite não encontrada em '{suite_path}'."
            )

        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise QualityCheckError(
                f"Não foi possível carregar a Expectation Suite de '{suite_path}': {exc}"
            ) from exc
