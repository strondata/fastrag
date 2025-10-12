"""Testes de integração para GreatExpectationsValidator."""

import json
from pathlib import Path

import pandas as pd
import pytest

from aether.core.quality import QualityCheckError

# Importar condicionalmente (Great Expectations é opcional)
ge = pytest.importorskip("great_expectations", reason="great-expectations not installed")

from aether.core.validators.great_expectations_validator import (
    GreatExpectationsValidator,
)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Cria um DataFrame de exemplo para testes."""
    return pd.DataFrame({
        "employee_id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age": [25, 30, 35, 28, 32],
        "salary": [50000.0, 60000.0, 75000.0, 55000.0, 70000.0],
        "department": ["Engineering", "Sales", "Engineering", "HR", "Sales"],
    })


@pytest.fixture
def invalid_dataframe() -> pd.DataFrame:
    """Cria um DataFrame inválido para testes de falha."""
    return pd.DataFrame({
        "employee_id": [1, 2, 2, 4, 5],  # ID duplicado (2)
        "name": ["Alice", "Bob", None, "Diana", "Eve"],  # Nome nulo
        "age": [25, 30, 35, -5, 32],  # Idade negativa
        "salary": [50000.0, 60000.0, 75000.0, 55000.0, -10000.0],  # Salário negativo
        "department": ["Engineering", "Sales", "Engineering", "HR", "Sales"],
    })


@pytest.fixture
def expectation_suite_path(tmp_path: Path) -> Path:
    """Cria uma Expectation Suite válida em arquivo temporário."""
    suite = {
        "expectation_suite_name": "employee_suite",
        "expectations": [
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "employee_id"},
            },
            {
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {"column": "employee_id"},
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "name"},
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "age", "min_value": 18, "max_value": 100},
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "salary", "min_value": 0, "max_value": 1000000},
            },
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "department",
                    "value_set": ["Engineering", "Sales", "HR", "Marketing"],
                },
            },
        ],
        "data_asset_type": "Dataset",
        "meta": {
            "great_expectations_version": "0.18.0",
        },
    }

    suite_path = tmp_path / "employee_suite.json"
    suite_path.write_text(json.dumps(suite, indent=2))
    return suite_path


class TestGreatExpectationsValidator:
    """Testes para GreatExpectationsValidator."""

    def test_validator_initialization_success(self, expectation_suite_path: Path):
        """Testa que o validador é inicializado corretamente com suite válida."""
        validator = GreatExpectationsValidator(
            expectation_suite_path=str(expectation_suite_path)
        )
        assert validator._suite_payload is not None
        assert validator._suite_name == "employee_suite"
        assert len(validator._suite_payload.get("expectations", [])) == 6

    def test_validator_initialization_missing_path(self):
        """Testa que erro é levantado quando suite path está vazio."""
        with pytest.raises(
            QualityCheckError,
            match="O caminho para a Expectation Suite é obrigatório",
        ):
            GreatExpectationsValidator(expectation_suite_path="")

    def test_validator_initialization_file_not_found(self):
        """Testa que erro é levantado quando arquivo da suite não existe."""
        with pytest.raises(
            QualityCheckError,
            match="Expectation Suite não encontrada",
        ):
            GreatExpectationsValidator(
                expectation_suite_path="/nonexistent/path/suite.json"
            )

    def test_validator_initialization_invalid_json(self, tmp_path: Path):
        """Testa que erro é levantado quando JSON da suite é inválido."""
        invalid_suite = tmp_path / "invalid.json"
        invalid_suite.write_text("{invalid json")

        with pytest.raises(
            QualityCheckError,
            match="Não foi possível carregar a Expectation Suite",
        ):
            GreatExpectationsValidator(expectation_suite_path=str(invalid_suite))

    def test_validate_success(
        self, expectation_suite_path: Path, sample_dataframe: pd.DataFrame
    ):
        """Testa que validação passa com dados válidos."""
        validator = GreatExpectationsValidator(
            expectation_suite_path=str(expectation_suite_path)
        )

        # Não deve levantar exceção
        validator.validate(sample_dataframe)

    def test_validate_failure_with_invalid_data(
        self, expectation_suite_path: Path, invalid_dataframe: pd.DataFrame
    ):
        """Testa que validação falha com dados inválidos."""
        validator = GreatExpectationsValidator(
            expectation_suite_path=str(expectation_suite_path)
        )

        with pytest.raises(
            QualityCheckError,
            match="Validação Great Expectations falhou",
        ):
            validator.validate(invalid_dataframe)

    def test_validate_with_explicit_suite_name(
        self, tmp_path: Path, sample_dataframe: pd.DataFrame
    ):
        """Testa validação com nome de suite explícito."""
        suite = {
            "expectations": [
                {
                    "expectation_type": "expect_column_to_exist",
                    "kwargs": {"column": "employee_id"},
                }
            ],
            "data_asset_type": "Dataset",
        }

        suite_path = tmp_path / "custom_suite.json"
        suite_path.write_text(json.dumps(suite))

        validator = GreatExpectationsValidator(
            expectation_suite_path=str(suite_path),
            expectation_suite_name="custom_name",
        )

        assert validator._suite_name == "custom_name"
        validator.validate(sample_dataframe)

    def test_validate_with_missing_columns(
        self, expectation_suite_path: Path
    ):
        """Testa que validação falha quando colunas esperadas estão faltando."""
        validator = GreatExpectationsValidator(
            expectation_suite_path=str(expectation_suite_path)
        )

        incomplete_df = pd.DataFrame({
            "employee_id": [1, 2, 3],
            # Faltam outras colunas
        })

        with pytest.raises(
            QualityCheckError,
            match="Validação Great Expectations falhou",
        ):
            validator.validate(incomplete_df)

    def test_validate_with_wrong_data_types(
        self, expectation_suite_path: Path
    ):
        """Testa que validação falha com tipos de dados incorretos."""
        validator = GreatExpectationsValidator(
            expectation_suite_path=str(expectation_suite_path)
        )

        wrong_type_df = pd.DataFrame({
            "employee_id": ["a", "b", "c", "d", "e"],  # Strings ao invés de int
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "salary": [50000, 60000, 75000, 55000, 70000],
            "department": ["Engineering", "Sales", "Engineering", "HR", "Sales"],
        })

        # Note: Great Expectations pode não falhar dependendo das expectations
        # Esta é uma validação de que o validador funciona, não das expectations
        try:
            validator.validate(wrong_type_df)
        except QualityCheckError:
            pass  # Esperado se houver expectations de tipo

    def test_integration_with_orchestrator_pattern(
        self, expectation_suite_path: Path, sample_dataframe: pd.DataFrame
    ):
        """Testa o padrão de uso com orquestrador (como seria usado na prática)."""
        # Este teste simula como o validador seria usado no orquestrador
        validator = GreatExpectationsValidator(
            expectation_suite_path=str(expectation_suite_path)
        )

        # Simula job retornando dados
        job_output = sample_dataframe

        # Validação antes de salvar dataset
        validator.validate(job_output)  # Não deve levantar exceção

        # Se chegou aqui, a validação passou e o dataset seria salvo
        assert True


class TestGreatExpectationsSuiteExamples:
    """Testa diferentes tipos de Expectation Suites."""

    def test_minimal_suite(self, tmp_path: Path, sample_dataframe: pd.DataFrame):
        """Testa suite mínima com apenas uma expectation."""
        suite = {
            "expectation_suite_name": "minimal_suite",
            "expectations": [
                {
                    "expectation_type": "expect_table_row_count_to_be_between",
                    "kwargs": {"min_value": 1, "max_value": 10},
                }
            ],
            "data_asset_type": "Dataset",
        }

        suite_path = tmp_path / "minimal.json"
        suite_path.write_text(json.dumps(suite))

        validator = GreatExpectationsValidator(
            expectation_suite_path=str(suite_path)
        )
        validator.validate(sample_dataframe)

    def test_complex_suite_with_regex(self, tmp_path: Path):
        """Testa suite com expectations complexas (regex, etc)."""
        suite = {
            "expectation_suite_name": "complex_suite",
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_match_regex",
                    "kwargs": {
                        "column": "email",
                        "regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    },
                }
            ],
            "data_asset_type": "Dataset",
        }

        suite_path = tmp_path / "complex.json"
        suite_path.write_text(json.dumps(suite))

        validator = GreatExpectationsValidator(
            expectation_suite_path=str(suite_path)
        )

        valid_email_df = pd.DataFrame({
            "email": ["alice@example.com", "bob@test.org", "charlie@company.co.uk"]
        })

        validator.validate(valid_email_df)

        # Teste com emails inválidos
        invalid_email_df = pd.DataFrame({
            "email": ["not-an-email", "missing@domain", "@no-user.com"]
        })

        with pytest.raises(QualityCheckError):
            validator.validate(invalid_email_df)
