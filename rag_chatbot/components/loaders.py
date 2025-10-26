"""Implementações de Document Loaders."""

import logging
import glob
from pathlib import Path
from typing import List

from rag_chatbot.interfaces import IDocumentLoader, Documento

logger = logging.getLogger(__name__)


class FolderLoader(IDocumentLoader):
    """Carrega documentos de texto de uma pasta.
    
    Lê todos os arquivos .txt de uma pasta especificada.
    """
    
    def load(self, source: str) -> List[Documento]:
        """Carrega arquivos .txt de uma pasta.
        
        Args:
            source: Caminho da pasta contendo arquivos .txt.
            
        Returns:
            Lista de documentos carregados.
        """
        logger.info(f"Carregando arquivos de {source}")
        documentos = []
        
        # Suporta tanto .txt quanto .md
        patterns = [f"{source}/*.txt", f"{source}/*.md"]
        
        for pattern in patterns:
            for filepath in glob.glob(pattern):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    # Criar metadata com informações do arquivo
                    nome_arquivo = Path(filepath).name
                    metadata = {
                        "source": nome_arquivo,
                        "path": filepath
                    }
                    
                    documentos.append(Documento(content=conteudo, metadata=metadata))
                    logger.debug(f"Arquivo {nome_arquivo} carregado com sucesso.")
                    
                except Exception as e:
                    logger.error(f"Falha ao ler {filepath}: {e}")
        
        logger.info(f"Total de {len(documentos)} documentos carregados.")
        return documentos
