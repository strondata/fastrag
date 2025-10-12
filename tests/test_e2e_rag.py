import os
from pathlib import Path

from typer.testing import CliRunner

from aether.cli import app

runner = CliRunner(env={"AETHER_LOG_LEVEL": "CRITICAL"})  # Suppress logs in tests


def test_rag_indexing_pipeline_e2e(tmp_path: Path):
    """
    Teste de ponta a ponta que executa o pipeline de indexação RAG via CLI.
    """
    # Define o caminho do pipeline de teste
    pipeline_dir = "tests/pipelines/rag_indexing"

    # Define o caminho de saída esperado e garante que ele esteja limpo
    output_dir = tmp_path / "rag_output"
    output_dir.mkdir()
    output_path_base = output_dir / "my_index"

    # Precisamos sobrescrever o caminho de saída no catalog.yml para usar o tmp_path
    # A maneira mais fácil é ler, modificar e reescrever o arquivo de catálogo.
    # Em um cenário real, isso poderia ser feito com variáveis de ambiente.
    catalog_path = Path(pipeline_dir) / "catalog.yml"
    original_catalog_text = catalog_path.read_text()

    # Usa um caminho temporário para o catálogo modificado
    temp_catalog_path = tmp_path / "temp_catalog.yml"
    modified_catalog_text = original_catalog_text.replace(
        'path: "tests/output/rag_index/my_index"',
        f'path: "{output_path_base.as_posix()}"',
    )
    temp_catalog_path.write_text(modified_catalog_text)

    # Cria um diretório de pipeline temporário com o pipeline original e o catálogo modificado
    temp_pipeline_dir = tmp_path / "temp_pipeline"
    temp_pipeline_dir.mkdir()
    (temp_pipeline_dir / "pipeline.yml").write_text(
        (Path(pipeline_dir) / "pipeline.yml").read_text()
    )
    (temp_pipeline_dir / "catalog.yml").write_text(modified_catalog_text)

    # Executa o pipeline
    result = runner.invoke(app, ["run", str(temp_pipeline_dir)])

    # Verifica se a execução foi bem-sucedida
    assert result.exit_code == 0, f"A execução da CLI falhou:\n{result.stdout}"
    assert "Pipeline concluído com sucesso!" in result.stdout

    # Verifica se os arquivos de saída foram criados
    expected_faiss_file = output_path_base.with_suffix(".faiss")
    expected_json_file = output_path_base.with_suffix(".json")

    assert (
        expected_faiss_file.exists()
    ), f"O arquivo de índice FAISS não foi criado em {expected_faiss_file}"
    assert (
        expected_json_file.exists()
    ), f"O arquivo de mapa de ID não foi criado em {expected_json_file}"

    # Limpa o catálogo original
    catalog_path.write_text(original_catalog_text)
