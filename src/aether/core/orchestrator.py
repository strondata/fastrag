"""
Este módulo contém o AssetOrchestrator, o cérebro do Aether.
Ele constrói o DAG de um pipeline e executa os jobs na ordem correta.
"""

import importlib
from typing import Dict, Type

import networkx as nx

from aether.core.factory import DataSetFactory
from aether.core.interfaces import AbstractJob, IDataSet
from aether.core.models import CatalogConfig, PipelineConfig


class OrchestratorError(Exception):
    """Exceção base para erros de orquestração."""


def _import_class(class_path: str) -> Type:
    """Helper para importar uma classe dinamicamente a partir de seu caminho."""
    try:
        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        if not isinstance(cls, type):
            raise OrchestratorError(
                f"O caminho '{class_path}' não aponta para uma classe."
            )
        return cls
    except (ImportError, AttributeError, ValueError) as e:
        raise OrchestratorError(
            f"Não foi possível importar a classe '{class_path}'"
        ) from e


class AssetOrchestrator:
    """
    Orquestra a execução de um pipeline de ativos de dados.
    """

    def __init__(self, pipeline_config: PipelineConfig, catalog_config: CatalogConfig):
        self.pipeline = pipeline_config
        self.catalog = catalog_config
        self._dataset_factory = DataSetFactory()
        self._instance_cache: Dict[str, IDataSet] = {}
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.DiGraph:
        """Constrói um grafo de dependências a partir das configurações."""
        g = nx.DiGraph()

        # Adiciona nós para todos os datasets e jobs
        for dataset_name in self.catalog.datasets:
            g.add_node(dataset_name, type="dataset")

        for job_name, job_config in self.pipeline.jobs.items():
            g.add_node(job_name, type="job", config=job_config)

            # Adiciona arestas de datasets de entrada para o job
            for input_name in job_config.inputs.values():
                if not g.has_node(input_name):
                    raise OrchestratorError(
                        f"Dataset '{input_name}' usado no job '{job_name}' não foi definido no catálogo."
                    )
                g.add_edge(input_name, job_name)

            # Adiciona arestas do job para os datasets de saída
            for dataset_name in job_config.outputs.values():
                if not g.has_node(dataset_name):
                    raise OrchestratorError(
                        f"Dataset '{dataset_name}' usado no job '{job_name}' não foi definido no catálogo."
                    )
                g.add_edge(job_name, dataset_name)

        if not nx.is_directed_acyclic_graph(g):
            raise OrchestratorError("O pipeline contém um ciclo de dependências.")

        return g

    def run(self):
        """Executa o pipeline completo na ordem topológica."""
        execution_order = list(nx.topological_sort(self.graph))

        print("--- Ordem de Execução do Pipeline ---")
        for node in execution_order:
            print(f"- {node} ({self.graph.nodes[node]['type']})")
        print("------------------------------------")

        for node_name in execution_order:
            node_data = self.graph.nodes[node_name]
            if node_data["type"] == "job":
                self._execute_job(node_name, node_data["config"])

    def _execute_job(self, job_name: str, job_config):
        """Instancia e executa um único job."""
        print(f"\n>>> Iniciando execução do Job: {job_name}")

        # Instancia a classe do Job
        job_class = _import_class(job_config.type)
        job_instance: AbstractJob = job_class(name=job_name, params=job_config.params)

        # Prepara os IDataSets de entrada
        input_datasets = {
            local_name: self._get_or_create_dataset(catalog_name)
            for local_name, catalog_name in job_config.inputs.items()
        }

        # Executa o job
        output_data = job_instance.run(**input_datasets)

        # Salva os IDataSets de saída
        if len(job_config.outputs) != len(output_data):
            raise OrchestratorError(
                f"O job '{job_name}' produziu {len(output_data)} saídas, mas {len(job_config.outputs)} foram declaradas."
            )

        for job_output_name, dataset_name in job_config.outputs.items():
            if job_output_name not in output_data:
                raise OrchestratorError(
                    f"O job '{job_name}' deveria produzir a saída '{job_output_name}', mas não o fez."
                )

            output_dataset = self._get_or_create_dataset(dataset_name)
            output_dataset.save(output_data[job_output_name])
            print(
                f"Saída '{job_output_name}' salva no dataset '{dataset_name}' com sucesso."
            )

        print(f"<<< Execução do Job '{job_name}' concluída.")

    def _get_or_create_dataset(self, name: str) -> IDataSet:
        """Obtém um dataset do cache ou cria um novo se não existir."""
        if name not in self._instance_cache:
            self._instance_cache[name] = self._dataset_factory.create(
                name, self.catalog
            )
        return self._instance_cache[name]

    @property
    def instance_cache(self) -> Dict[str, IDataSet]:
        """Expõe o cache de instâncias para fins de teste e inspeção."""
        return self._instance_cache
