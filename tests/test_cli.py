import json
from pathlib import Path

from typer.testing import CliRunner

from aether.cli import app

# A fixture `test_pipeline_path` é importada implicitamente pelo pytest
# do arquivo tests/core/test_orchestrator.py, então não precisamos redefini-la.
# No entanto, para clareza, seria melhor movê-la para um conftest.py.
# Por enquanto, vamos contar com o comportamento do pytest.


runner = CliRunner()


def test_cli_run_success(test_pipeline_path: Path):
    """Verifica se `aether run` executa com sucesso."""
    result = runner.invoke(app, ["run", str(test_pipeline_path)])
    assert result.exit_code == 0
    assert "Pipeline concluído com sucesso!" in result.stdout


def test_cli_run_missing_dir():
    """Verifica se `aether run` falha para um diretório inexistente."""
    result = runner.invoke(app, ["run", "non_existent_dir"])
    assert result.exit_code != 0
    # A mensagem de erro exata do Typer pode variar, então apenas verificamos o código de saída.


def test_cli_run_missing_files(tmp_path: Path):
    """Verifica se `aether run` falha se o diretório não contém os ymls."""
    result = runner.invoke(app, ["run", str(tmp_path)])
    assert result.exit_code == 1
    assert "deve conter 'pipeline.yml' e 'catalog.yml'" in result.stdout


def test_cli_viz_text_output(test_pipeline_path: Path):
    """Verifica a saída de texto padrão de `aether viz`."""
    result = runner.invoke(app, ["viz", str(test_pipeline_path)])
    assert result.exit_code == 0
    assert "Visualização do Pipeline" in result.stdout
    assert "Nós do Grafo" in result.stdout
    assert "raw_string" in result.stdout
    assert "uppercase_job" in result.stdout
    assert "Dependências (Arestas)" in result.stdout
    assert "raw_string -> uppercase_job" in result.stdout


def test_cli_viz_json_output(test_pipeline_path: Path):
    """Verifica a saída JSON de `aether viz --json`."""
    result = runner.invoke(app, ["viz", "--json", str(test_pipeline_path)])
    assert result.exit_code == 0

    # Tenta analisar a saída como JSON para verificar se é válida
    try:
        dag_data = json.loads(result.stdout)
        assert "nodes" in dag_data
        assert "links" in dag_data
        assert len(dag_data["nodes"]) > 0
        assert len(dag_data["links"]) > 0

        node_ids = {node["id"] for node in dag_data["nodes"]}
        assert "raw_string" in node_ids
        assert "uppercase_job" in node_ids

    except json.JSONDecodeError:
        assert False, "A saída de `aether viz --json` não é um JSON válido."


def test_cli_new_success(tmp_path: Path):
    """Verifica se `aether new` cria a estrutura de diretórios esperada."""
    project_name = "meu-novo-projeto"
    project_dir = tmp_path / project_name

    result = runner.invoke(app, ["new", str(project_dir)])
    assert result.exit_code == 0
    assert "criado com sucesso!" in result.stdout

    assert project_dir.is_dir()
    assert (project_dir / "src").is_dir()
    assert (project_dir / "pipelines").is_dir()
    assert (project_dir / "pipelines" / "catalog.yml").is_file()
    assert (project_dir / ".gitignore").is_file()


def test_cli_new_project_exists(tmp_path: Path):
    """Verifica se `aether new` falha se o diretório já existe."""
    project_name = "projeto-existente"
    project_dir = tmp_path / project_name
    project_dir.mkdir()

    result = runner.invoke(app, ["new", str(project_dir)])
    assert result.exit_code == 1
    assert "já existe" in result.stdout
