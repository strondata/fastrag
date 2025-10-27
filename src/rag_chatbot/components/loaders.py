"""Implementações de Document Loaders."""

import logging
import glob
from pathlib import Path
from typing import List

from ..interfaces import IDocumentLoader, Documento

logger = logging.getLogger(__name__)


class UniversalLoader(IDocumentLoader):
    """Carrega documentos de múltiplos formatos de uma pasta.
    
    Suporta: .txt, .md, .pdf, .docx
    """
    
    def load(self, source: str) -> List[Documento]:
        """Carrega arquivos de múltiplos formatos de uma pasta.
        
        Args:
            source: Caminho da pasta contendo arquivos.
            
        Returns:
            Lista de documentos carregados.
        """
        logger.info(f"Carregando arquivos de {source}")
        documentos = []
        
        # Padrões de arquivo suportados
        patterns = {
            "*.txt": self._load_text,
            "*.md": self._load_text,
            "*.pdf": self._load_pdf,
            "*.docx": self._load_docx,
        }
        
        for pattern, loader_func in patterns.items():
            for filepath in glob.glob(f"{source}/{pattern}"):
                try:
                    doc = loader_func(filepath)
                    if doc:
                        documentos.append(doc)
                        logger.debug(f"Arquivo {Path(filepath).name} carregado com sucesso.")
                except Exception as e:
                    logger.error(f"Falha ao ler {filepath}: {e}")
        
        logger.info(f"Total de {len(documentos)} documentos carregados.")
        return documentos
    
    def _load_text(self, filepath: str) -> Documento:
        """Carrega arquivo de texto (.txt, .md).
        
        Args:
            filepath: Caminho do arquivo.
            
        Returns:
            Documento carregado.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        nome_arquivo = Path(filepath).name
        metadata = {
            "source": nome_arquivo,
            "path": filepath,
            "type": "text"
        }
        
        return Documento(content=conteudo, metadata=metadata)
    
    def _load_pdf(self, filepath: str) -> Documento:
        """Carrega arquivo PDF usando PyMuPDF.
        
        Args:
            filepath: Caminho do arquivo PDF.
            
        Returns:
            Documento carregado.
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error("PyMuPDF não está instalado. Execute: pip install PyMuPDF")
            raise ImportError("PyMuPDF não encontrado")
        
        doc = fitz.open(filepath)
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_parts.append(page.get_text())
        
        doc.close()
        
        conteudo = "\n".join(text_parts)
        nome_arquivo = Path(filepath).name
        
        metadata = {
            "source": nome_arquivo,
            "path": filepath,
            "type": "pdf",
            "pages": len(text_parts)
        }
        
        return Documento(content=conteudo, metadata=metadata)
    
    def _load_docx(self, filepath: str) -> Documento:
        """Carrega arquivo DOCX usando python-docx.
        
        Args:
            filepath: Caminho do arquivo DOCX.
            
        Returns:
            Documento carregado.
        """
        try:
            from docx import Document as DocxDocument
        except ImportError:
            logger.error("python-docx não está instalado. Execute: pip install python-docx")
            raise ImportError("python-docx não encontrado")
        
        doc = DocxDocument(filepath)
        text_parts = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        
        conteudo = "\n".join(text_parts)
        nome_arquivo = Path(filepath).name
        
        metadata = {
            "source": nome_arquivo,
            "path": filepath,
            "type": "docx",
            "paragraphs": len(text_parts)
        }
        
        return Documento(content=conteudo, metadata=metadata)


# Manter FolderLoader como alias para compatibilidade com código existente
class FolderLoader(UniversalLoader):
    """Alias para UniversalLoader para compatibilidade retroativa."""
    pass
