import pytest

from aether.core.factory import DataSetFactory, DataSetFactoryError
from aether.core.models import CatalogConfig
from aether.datasets.in_memory_data_set import InMemoryDataSet


@pytest.fixture
def catalog_config() -> CatalogConfig:
    """Fixture que fornece uma configuração de catálogo de exemplo."""
    config_data = {
        "datasets": {
            "test_data": {
                "type": "InMemoryDataSet",
                "layer": "test",
                "options": {"initial_data": [1, 2, 3]},
            },
            "another_data": {
                "type": "ExplicitlyRegisteredDataSet",
                "layer": "test",
            },
            "unregistered_data": {
                "type": "NonExistentDataSet",
                "layer": "test",
            },
        }
    }
    return CatalogConfig.model_validate(config_data)


def test_factory_lazy_load_success(catalog_config: CatalogConfig):
    """Verifica se a factory pode carregar dinamicamente um IDataSet não registrado."""
    factory = DataSetFactory()
    dataset = factory.create("test_data", catalog_config)

    assert isinstance(dataset, InMemoryDataSet)
    assert dataset.load() == [1, 2, 3]


def test_factory_register_and_create(catalog_config: CatalogConfig):
    """Verifica o registro explícito e a criação de um IDataSet."""

    class ExplicitlyRegisteredDataSet:
        def load(self):
            return "explicit"

        def save(self, data):
            pass

    factory = DataSetFactory()
    factory.register("ExplicitlyRegisteredDataSet", ExplicitlyRegisteredDataSet)

    dataset = factory.create("another_data", catalog_config)
    assert isinstance(dataset, ExplicitlyRegisteredDataSet)
    assert dataset.load() == "explicit"


def test_factory_create_not_in_catalog():
    """Verifica se um erro é levantado ao tentar criar um DataSet que não está no catálogo."""
    factory = DataSetFactory()
    empty_catalog = CatalogConfig.model_validate({"datasets": {}})
    with pytest.raises(
        DataSetFactoryError, match="DataSet 'non_existent' não encontrado no catálogo."
    ):
        factory.create("non_existent", empty_catalog)


def test_factory_create_type_not_registered(catalog_config: CatalogConfig):
    """Verifica se um erro é levantado quando o tipo de DataSet não pode ser encontrado/carregado."""
    factory = DataSetFactory()
    with pytest.raises(
        DataSetFactoryError,
        match="Tipo de DataSet 'NonExistentDataSet' não registrado.",
    ):
        factory.create("unregistered_data", catalog_config)


def test_factory_register_duplicate_error():
    """Verifica se um erro é levantado ao tentar registrar um tipo que já existe."""
    factory = DataSetFactory()
    factory.register("MyDataSet", InMemoryDataSet)
    with pytest.raises(
        DataSetFactoryError, match="Tipo de DataSet 'MyDataSet' já registrado."
    ):
        factory.register("MyDataSet", InMemoryDataSet)
