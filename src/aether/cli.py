"""
Módulo da Interface de Linha de Comando (CLI) para o Aether.
"""

import json
import os
from pathlib import Path
from typing import Optional

import networkx as nx
import typer
from rich.console import Console
from rich.panel import Panel

from aether.core.config_loader import AetherConfigError, load_config
from aether.core.logger import configure_logging, get_logger
from aether.core.models import CatalogConfig, PipelineConfig
from aether.core.orchestrator import AssetOrchestrator, OrchestratorError

app = typer.Typer(
    name="aether",
    help="Uma plataforma de engenharia de dados de autoatendimento.",
    add_completion=False,
)
console = Console()

# Configure logging based on environment
_LOG_LEVEL = os.getenv("AETHER_LOG_LEVEL", "INFO")
_LOG_JSON = os.getenv("AETHER_LOG_JSON", "false").lower() == "true"

configure_logging(log_level=_LOG_LEVEL, json_output=_LOG_JSON)
logger = get_logger(__name__)


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
    logger.info(
        "cli_run_started",
        pipeline_dir=str(pipeline_dir),
    )
    
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
        logger.error("cli_run_failed", reason="config_load_error")
        raise typer.Exit(code=1)

    pipeline_config, catalog_config = configs

    try:
        orchestrator = AssetOrchestrator(pipeline_config, catalog_config)
        orchestrator.run()
        console.print("\n[bold green]✅ Pipeline concluído com sucesso![/bold green]")
        logger.info("cli_run_completed", pipeline_dir=str(pipeline_dir))
    except OrchestratorError as e:
        console.print(f"\n[bold red]Erro de Orquestração:[/bold red]\n{e}")
        logger.error(
            "cli_run_failed",
            reason="orchestrator_error",
            error=str(e),
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(
            f"\n[bold red]Erro inesperado durante a execução:[/bold red]\n{e}"
        )
        logger.error(
            "cli_run_failed",
            reason="unexpected_error",
            error=str(e),
            error_type=type(e).__name__,
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
    logger.info(
        "cli_viz_started",
        pipeline_dir=str(pipeline_dir),
        output_format="json" if output_json else "tree",
    )
    
    configs = _load_configs(pipeline_dir)
    if not configs:
        logger.error("cli_viz_failed", reason="config_load_error")
        raise typer.Exit(code=1)

    pipeline_config, catalog_config = configs

    try:
        orchestrator = AssetOrchestrator(pipeline_config, catalog_config)
        if output_json:
            dag_data = nx.node_link_data(orchestrator.graph)
            print(json.dumps(dag_data, indent=2))  # Use print() to avoid Rich formatting
        else:
            console.print(
                Panel(
                    f"[bold blue]Visualização do Pipeline: {pipeline_dir.name}[/bold blue]",
                    title="Aether Viz",
                    expand=False,
                )
            )
            _print_dag_tree(orchestrator.graph)
        
        logger.info("cli_viz_completed")

    except OrchestratorError as e:
        console.print(f"\n[bold red]Erro de Orquestração:[/bold red]\n{e}")
        logger.error("cli_viz_failed", reason="orchestrator_error", error=str(e))
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


@app.command()
def test(
    pipeline_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="O caminho para o diretório do pipeline a ser testado.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Exibe informações detalhadas dos testes.",
    ),
):
    """
    Testa a configuração e validade de um pipeline.
    
    Verifica:
    - Sintaxe YAML válida
    - Schemas Pydantic
    - Referências entre jobs e datasets
    - DAG sem ciclos
    - Tipos de datasets disponíveis
    - Parâmetros obrigatórios
    """
    logger.info(
        "cli_test_started",
        pipeline_dir=str(pipeline_dir),
        verbose=verbose,
    )
    
    console.print(
        Panel(
            f"[bold blue]🧪 Testando pipeline em '{pipeline_dir}'[/bold blue]",
            title="Aether Test",
            expand=False,
        )
    )
    
    test_results = []
    has_errors = False
    
    # Test 1: Verificar arquivos existem
    pipeline_path = pipeline_dir / "pipeline.yml"
    catalog_path = pipeline_dir / "catalog.yml"
    
    if not pipeline_path.exists():
        test_results.append(("❌", "pipeline.yml não encontrado"))
        has_errors = True
    else:
        test_results.append(("✅", "pipeline.yml encontrado"))
        
    if not catalog_path.exists():
        test_results.append(("❌", "catalog.yml não encontrado"))
        has_errors = True
    else:
        test_results.append(("✅", "catalog.yml encontrado"))
    
    if has_errors:
        for icon, msg in test_results:
            console.print(f"{icon} {msg}")
        raise typer.Exit(code=1)
    
    # Test 2: Carregar e validar configs
    try:
        pipeline_config, catalog_config = _load_configs(pipeline_dir)
        pipeline_name = pipeline_config.description or pipeline_dir.name
        test_results.append(("✅", f"Schemas válidos (Pipeline: {pipeline_name})"))
    except (AetherConfigError, typer.Exit):
        test_results.append(("❌", "Erro ao validar schemas"))
        for icon, msg in test_results:
            console.print(f"{icon} {msg}")
        raise typer.Exit(code=1)
    
    # Test 3: Verificar datasets referenciados existem
    dataset_refs_ok = True
    for job_name, job in pipeline_config.jobs.items():
        for input_ref in job.inputs.values():
            if input_ref not in catalog_config.datasets:
                test_results.append(("❌", f"Dataset '{input_ref}' (job '{job_name}') não existe no catalog"))
                dataset_refs_ok = False
                has_errors = True
        for output_ref in job.outputs.values():
            if output_ref not in catalog_config.datasets:
                test_results.append(("❌", f"Dataset '{output_ref}' (job '{job_name}') não existe no catalog"))
                dataset_refs_ok = False
                has_errors = True
    
    if dataset_refs_ok:
        test_results.append(("✅", f"Todas as referências de datasets válidas ({len(catalog_config.datasets)} datasets)"))
    
    # Test 4: Construir DAG (detecta ciclos)
    try:
        orchestrator = AssetOrchestrator(pipeline_config, catalog_config)
        num_nodes = orchestrator.graph.number_of_nodes()
        num_edges = orchestrator.graph.number_of_edges()
        test_results.append(("✅", f"DAG válido (sem ciclos): {num_nodes} nós, {num_edges} arestas"))
    except OrchestratorError as e:
        test_results.append(("❌", f"Erro no DAG: {e}"))
        has_errors = True
    
    # Test 5: Verificar tipos de datasets disponíveis
    from aether.core.factory import DataSetFactory
    factory = DataSetFactory()
    unavailable_types = []
    
    for ds_name in catalog_config.datasets.keys():
        try:
            factory.create(ds_name, catalog_config)
        except Exception as e:
            ds_type = catalog_config.datasets[ds_name].type
            unavailable_types.append((ds_name, ds_type, str(e)))
            has_errors = True
    
    if unavailable_types:
        for ds_name, ds_type, error in unavailable_types:
            test_results.append(("❌", f"Dataset '{ds_name}' (type={ds_type}): {error}"))
    else:
        test_results.append(("✅", f"Todos os tipos de datasets disponíveis"))
    
    # Exibir resultados
    console.print()
    for icon, msg in test_results:
        console.print(f"{icon} {msg}")
    
    if verbose and not has_errors:
        console.print("\n[bold]Detalhes do Pipeline:[/bold]")
        console.print(f"  Jobs: {len(pipeline_config.jobs)}")
        console.print(f"  Datasets: {len(catalog_config.datasets)}")
        
        console.print("\n[bold]Layers:[/bold]")
        layers = {}
        for ds_name, ds_config in catalog_config.datasets.items():
            layer = ds_config.layer
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(ds_name)
        
        for layer, datasets in sorted(layers.items()):
            console.print(f"  {layer}: {len(datasets)} dataset(s)")
    
    if has_errors:
        console.print("\n[bold red]❌ Testes falharam[/bold red]")
        logger.warning("cli_test_completed", status="failed", errors=sum(1 for icon, _ in test_results if icon == "❌"))
        raise typer.Exit(code=1)
    else:
        console.print("\n[bold green]✅ Todos os testes passaram![/bold green]")
        logger.info("cli_test_completed", status="passed", total_checks=len(test_results))


@app.command()
def lint(
    pipeline_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="O caminho para o diretório do pipeline a ser validado.",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        "-s",
        help="Modo estrito: avisos se tornam erros.",
    ),
):
    """
    Valida a qualidade e convenções dos arquivos de configuração.
    
    Verifica:
    - Nomenclatura (snake_case, sem espaços)
    - Layers válidos (raw, staging, transient, processed, curated)
    - Documentação (description fields)
    - Boas práticas (quality validators, etc.)
    """
    logger.info(
        "cli_lint_started",
        pipeline_dir=str(pipeline_dir),
        strict_mode=strict,
    )
    
    console.print(
        Panel(
            f"[bold yellow]🔍 Linting pipeline em '{pipeline_dir}'[/bold yellow]",
            title="Aether Lint",
            expand=False,
        )
    )
    
    warnings = []
    errors = []
    
    # Carregar configs
    try:
        pipeline_config, catalog_config = _load_configs(pipeline_dir)
    except (AetherConfigError, typer.Exit):
        console.print("[bold red]❌ Não foi possível carregar configurações[/bold red]")
        raise typer.Exit(code=1)
    
    # Rule 1: Nomenclatura snake_case
    import re
    snake_case_pattern = re.compile(r'^[a-z][a-z0-9_]*$')
    
    for ds_name in catalog_config.datasets.keys():
        if not snake_case_pattern.match(ds_name):
            warnings.append(f"Dataset '{ds_name}' não está em snake_case")
    
    for job_name in pipeline_config.jobs.keys():
        if not snake_case_pattern.match(job_name):
            warnings.append(f"Job '{job_name}' não está em snake_case")
    
    # Rule 2: Layers válidos
    valid_layers = {"raw", "staging", "transient", "processed", "curated"}
    
    for ds_name, ds_config in catalog_config.datasets.items():
        if ds_config.layer not in valid_layers:
            errors.append(
                f"Dataset '{ds_name}' tem layer inválido: '{ds_config.layer}'. "
                f"Use um dos: {', '.join(valid_layers)}"
            )
    
    # Rule 3: Datasets curated devem ter quality validation
    for ds_name, ds_config in catalog_config.datasets.items():
        if ds_config.layer == "curated" and not ds_config.quality:
            warnings.append(
                f"Dataset curated '{ds_name}' não possui validação de qualidade (quality)"
            )
    
    # Rule 4: Jobs devem ter descrição
    if hasattr(pipeline_config, 'description') and not pipeline_config.description:
        warnings.append("Pipeline sem campo 'description'")
    
    # Rule 5: Datasets não utilizados
    used_datasets = set()
    for job in pipeline_config.jobs.values():
        used_datasets.update(job.inputs.values())
        used_datasets.update(job.outputs.values())
    
    unused_datasets = set(catalog_config.datasets.keys()) - used_datasets
    for ds_name in unused_datasets:
        warnings.append(f"Dataset '{ds_name}' declarado mas não utilizado em nenhum job")
    
    # Rule 6: Ordem topológica sugere layers
    try:
        orchestrator = AssetOrchestrator(pipeline_config, catalog_config)
        topo_order = list(nx.topological_sort(orchestrator.graph))
        
        # Verificar se outputs têm layer >= inputs
        layer_order = {"raw": 0, "staging": 1, "transient": 1, "processed": 2, "curated": 3}
        
        for job_name, job in pipeline_config.jobs.items():
            input_layers = [
                layer_order.get(catalog_config.datasets[ds_ref].layer, 0)
                for ds_ref in job.inputs.values()
            ]
            output_layers = [
                layer_order.get(catalog_config.datasets[ds_ref].layer, 0)
                for ds_ref in job.outputs.values()
            ]
            
            if input_layers and output_layers:
                max_input = max(input_layers)
                min_output = min(output_layers)
                
                if min_output < max_input:
                    warnings.append(
                        f"Job '{job_name}' tem output layer inferior ao input "
                        f"(possível regressão de qualidade)"
                    )
    except OrchestratorError:
        pass  # DAG error já foi reportado em test
    
    # Exibir resultados
    console.print()
    
    if errors:
        console.print("[bold red]Erros:[/bold red]")
        for error in errors:
            console.print(f"  ❌ {error}")
    
    if warnings:
        icon = "❌" if strict else "⚠️"
        color = "red" if strict else "yellow"
        console.print(f"\n[bold {color}]Avisos:[/bold {color}]")
        for warning in warnings:
            console.print(f"  {icon} {warning}")
    
    if not errors and not warnings:
        console.print("[bold green]✅ Nenhum problema encontrado![/bold green]")
    
    console.print(f"\n[bold]Resumo:[/bold]")
    console.print(f"  Erros: {len(errors)}")
    console.print(f"  Avisos: {len(warnings)}")
    
    logger.info(
        "cli_lint_completed",
        errors=len(errors),
        warnings=len(warnings),
        strict_mode=strict,
    )
    
    if errors or (strict and warnings):
        raise typer.Exit(code=1)


@app.command()
def catalog(
    pipeline_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="O caminho para o diretório do pipeline.",
    ),
    output_json: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Saída em formato JSON.",
    ),
    layer_filter: Optional[str] = typer.Option(
        None,
        "--layer",
        "-l",
        help="Filtrar por layer específico (raw, staging, processed, curated).",
    ),
):
    """
    Lista todos os datasets do catálogo com suas informações.
    
    Mostra: nome, tipo, layer, caminho (se disponível), quality.
    """
    logger.info(
        "cli_catalog_started",
        pipeline_dir=str(pipeline_dir),
        layer_filter=layer_filter,
        output_format="json" if output_json else "table",
    )
    
    try:
        pipeline_config, catalog_config = _load_configs(pipeline_dir)
    except (AetherConfigError, typer.Exit):
        logger.error("cli_catalog_failed", reason="config_load_error")
        raise typer.Exit(code=1)
    
    datasets_info = []
    
    for ds_name, ds_config in catalog_config.datasets.items():
        if layer_filter and ds_config.layer != layer_filter:
            continue
        
        info = {
            "name": ds_name,
            "type": ds_config.type,
            "layer": ds_config.layer,
            "path": ds_config.options.get("path", "N/A"),
            "has_quality": ds_config.quality is not None,
        }
        
        if ds_config.quality:
            info["quality_type"] = ds_config.quality.type
        
        datasets_info.append(info)
    
    if output_json:
        print(json.dumps(datasets_info, indent=2))  # Use print() to avoid Rich formatting
    else:
        pipeline_name = pipeline_config.description or pipeline_dir.name
        console.print(
            Panel(
                f"[bold magenta]Catálogo de Datasets: {pipeline_name}[/bold magenta]",
                title="Aether Catalog",
                expand=False,
            )
        )
        
        if not datasets_info:
            console.print("[yellow]Nenhum dataset encontrado[/yellow]")
            if layer_filter:
                console.print(f"[dim](filtrado por layer: {layer_filter})[/dim]")
        else:
            # Agrupar por layer
            by_layer = {}
            for info in datasets_info:
                layer = info["layer"]
                if layer not in by_layer:
                    by_layer[layer] = []
                by_layer[layer].append(info)
            
            for layer in ["raw", "staging", "transient", "processed", "curated"]:
                if layer not in by_layer:
                    continue
                
                console.print(f"\n[bold cyan]{layer.upper()}[/bold cyan] ({len(by_layer[layer])} dataset(s))")
                
                for info in by_layer[layer]:
                    quality_badge = "🛡️" if info["has_quality"] else ""
                    console.print(f"  • [bold]{info['name']}[/bold] {quality_badge}")
                    console.print(f"    Type: {info['type']}")
                    console.print(f"    Path: {info['path']}")
                    if info.get("quality_type"):
                        console.print(f"    Quality: {info['quality_type']}")
            
            console.print(f"\n[bold]Total:[/bold] {len(datasets_info)} dataset(s)")
    
    logger.info(
        "cli_catalog_completed",
        total_datasets=len(datasets_info),
        layer_filter=layer_filter,
    )


def main():
    """Função de entrada principal para a CLI."""
    app()
