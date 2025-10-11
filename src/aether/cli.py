"""
Módulo da Interface de Linha de Comando (CLI) para o Aether.
"""

import json
from pathlib import Path
from typing import Optional

import networkx as nx
import typer
from rich.console import Console
from rich.panel import Panel

from aether.core.config_loader import AetherConfigError, load_config
from aether.core.models import CatalogConfig, PipelineConfig
from aether.core.orchestrator import AssetOrchestrator, OrchestratorError

app = typer.Typer(
    name="aether",
    help="Uma plataforma de engenharia de dados de autoatendimento.",
    add_completion=False,
)
console = Console()


def _load_configs(
    pipeline_dir: Path,
) -> Optional[tuple[PipelineConfig, CatalogConfig]]:
    """Carrega os arquivos pipeline.yml e catalog.yml de um diretório."""
    try:
        pipeline_path = pipeline_dir / "pipeline.yml"
        catalog_path = pipeline_dir / "catalog.yml"

        if not pipeline_path.exists() or not catalog_path.exists():
            console.print(
                f"[bold red]Erro:[/bold red] O diretório '{pipeline_dir}' deve conter 'pipeline.yml' e 'catalog.yml'."
            )
            raise typer.Exit(code=1)

        pipeline_config = load_config(pipeline_path, PipelineConfig)
        catalog_config = load_config(catalog_path, CatalogConfig)
        return pipeline_config, catalog_config
    except AetherConfigError as e:
        console.print(f"[bold red]Erro de Configuração:[/bold red]\n{e}")
        raise typer.Exit(code=1)


@app.command()
def run(
    pipeline_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="O caminho para o diretório do pipeline contendo 'pipeline.yml' e 'catalog.yml'.",
    )
):
    """
    Executa um pipeline do Aether.
    """
    console.print(
        Panel(
            f"[bold green]🚀 Executando pipeline em '{pipeline_dir}'[/bold green]",
            title="Aether Run",
            expand=False,
        )
    )

    configs = _load_configs(pipeline_dir)
    if not configs:
        # Erro já foi impresso por _load_configs
        raise typer.Exit(code=1)

    pipeline_config, catalog_config = configs

    try:
        orchestrator = AssetOrchestrator(pipeline_config, catalog_config)
        orchestrator.run()
        console.print("\n[bold green]✅ Pipeline concluído com sucesso![/bold green]")
    except OrchestratorError as e:
        console.print(f"\n[bold red]Erro de Orquestração:[/bold red]\n{e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(
            f"\n[bold red]Erro inesperado durante a execução:[/bold red]\n{e}"
        )
        raise typer.Exit(code=1)


@app.command()
def viz(
    pipeline_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="O caminho para o diretório do pipeline a ser visualizado.",
    ),
    output_json: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Imprime a saída do grafo em formato JSON.",
    ),
):
    """
    Visualiza o Grafo Acíclico Dirigido (DAG) de um pipeline.
    """
    configs = _load_configs(pipeline_dir)
    if not configs:
        raise typer.Exit(code=1)

    pipeline_config, catalog_config = configs

    try:
        orchestrator = AssetOrchestrator(pipeline_config, catalog_config)
        if output_json:
            dag_data = nx.node_link_data(orchestrator.graph)
            console.print(json.dumps(dag_data, indent=2))
        else:
            console.print(
                Panel(
                    f"[bold blue]Visualização do Pipeline: {pipeline_dir.name}[/bold blue]",
                    title="Aether Viz",
                    expand=False,
                )
            )
            _print_dag_tree(orchestrator.graph)

    except OrchestratorError as e:
        console.print(f"\n[bold red]Erro de Orquestração:[/bold red]\n{e}")
        raise typer.Exit(code=1)


def _print_dag_tree(graph: nx.DiGraph):
    """Imprime uma representação em árvore simples do DAG."""
    console.print("[bold]Nós do Grafo:[/bold]")
    for node, data in graph.nodes(data=True):
        color = "cyan" if data["type"] == "job" else "magenta"
        console.print(f"- [bold {color}]{node}[/bold {color}] ({data['type']})")

    console.print("\n[bold]Dependências (Arestas):[/bold]")
    for u, v in graph.edges():
        console.print(f"- [cyan]{u}[/cyan] -> [magenta]{v}[/magenta]")


@app.command()
def new(
    project_name: str = typer.Argument(
        ..., help="O nome do novo produto de dados Aether."
    )
):
    """
    Cria a estrutura de um novo projeto Aether (scaffolding).
    """
    project_dir = Path(project_name).resolve()
    if project_dir.exists():
        console.print(
            f"[bold red]Erro:[/bold red] O diretório '{project_name}' já existe."
        )
        raise typer.Exit(code=1)

    console.print(f"✨ Criando novo projeto Aether em [cyan]{project_dir}[/cyan]...")
    project_dir.mkdir()
    (project_dir / "src").mkdir()
    (project_dir / "docs").mkdir()
    (project_dir / "pipelines").mkdir()

    # Cria arquivos de exemplo
    (project_dir / "pipelines" / "catalog.yml").touch()
    (project_dir / "pipelines" / "pipeline.yml").touch()
    (project_dir / ".gitignore").write_text("*.pyc\n__pycache__/\n.venv/\n")

    console.print(
        Panel(
            f"[bold green]✅ Projeto '{project_name}' criado com sucesso![/bold green]\n\n"
            f"Próximos passos:\n"
            f"1. `cd {project_name}`\n"
            f"2. Defina seus datasets em `pipelines/catalog.yml`.\n"
            f"3. Defina seu pipeline em `pipelines/pipeline.yml`.",
            title="Projeto Criado",
            expand=False,
        )
    )


def main():
    """Função de entrada principal para a CLI."""
    app()
