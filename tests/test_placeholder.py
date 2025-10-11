import pytest


def test_initial_setup():
    """
    Um teste placeholder para garantir que o Pytest está funcionando.
    """
    assert True, "O setup inicial de testes falhou."


def test_import_core_interfaces():
    """
    Verifica se os contratos centrais podem ser importados sem erros.
    """
    try:
        from aether.core.interfaces import (  # noqa: F401
            AbstractJob,
            AbstractPipeline,
            IDataSet,
        )
    except ImportError as e:
        pytest.fail(f"Falha ao importar as interfaces do Aether: {e}")
