"""Implementações de Text Splitters para divisão de documentos."""

import logging
from typing import List
from copy import deepcopy

from ..interfaces import ITextSplitter, Documento

logger = logging.getLogger(__name__)


class RecursiveCharacterTextSplitter(ITextSplitter):
    """Divide texto recursivamente usando diferentes separadores.
    
    Tenta dividir o texto em chunks usando separadores em ordem de prioridade:
    primeiro por parágrafos (\n\n), depois por linhas (\n), depois por espaços ( ).
    
    Attributes:
        chunk_size: Tamanho máximo de cada chunk em caracteres.
        chunk_overlap: Quantidade de caracteres de sobreposição entre chunks.
        separators: Lista de separadores a tentar, em ordem de prioridade.
    """
    
    def __init__(
        self, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """Inicializa o text splitter.
        
        Args:
            chunk_size: Tamanho máximo de cada chunk.
            chunk_overlap: Sobreposição entre chunks consecutivos.
            separators: Lista customizada de separadores (opcional).
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]
        
        logger.info(
            f"RecursiveCharacterTextSplitter inicializado: "
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )
    
    def split_documents(self, docs: List[Documento]) -> List[Documento]:
        """Divide documentos em chunks menores.
        
        Args:
            docs: Lista de documentos a dividir.
            
        Returns:
            Lista de documentos divididos (chunks) com metadados herdados.
        """
        logger.info(f"Dividindo {len(docs)} documentos em chunks...")
        
        all_chunks = []
        
        for doc in docs:
            # Dividir o texto do documento
            text_chunks = self._split_text(doc.content)
            
            # Criar novos documentos para cada chunk, herdando metadados
            for i, chunk_text in enumerate(text_chunks):
                # Criar cópia dos metadados do documento pai
                chunk_metadata = deepcopy(doc.metadata)
                
                # Adicionar informações sobre o chunk
                chunk_metadata['chunk_index'] = i
                chunk_metadata['total_chunks'] = len(text_chunks)
                
                chunk_doc = Documento(
                    content=chunk_text,
                    metadata=chunk_metadata
                )
                all_chunks.append(chunk_doc)
        
        logger.info(
            f"Divisão concluída: {len(docs)} documentos -> {len(all_chunks)} chunks "
            f"({len(all_chunks) / len(docs):.1f} chunks/doc em média)"
        )
        
        return all_chunks
    
    def _split_text(self, text: str) -> List[str]:
        """Divide um texto em chunks recursivamente.
        
        Args:
            text: Texto a dividir.
            
        Returns:
            Lista de chunks de texto.
        """
        # Se o texto é menor que chunk_size, retornar como está
        if len(text) <= self.chunk_size:
            return [text] if text else []
        
        # Tentar cada separador em ordem de prioridade
        for separator in self.separators:
            if separator == "":
                # Se chegamos ao separador vazio, dividir por caractere
                return self._split_by_character(text)
            
            if separator in text:
                # Dividir pelo separador atual
                return self._split_by_separator(text, separator)
        
        # Fallback: dividir por caractere
        return self._split_by_character(text)
    
    def _split_by_separator(self, text: str, separator: str) -> List[str]:
        """Divide texto por um separador específico.
        
        Args:
            text: Texto a dividir.
            separator: Separador a usar.
            
        Returns:
            Lista de chunks.
        """
        # Dividir o texto pelo separador
        splits = text.split(separator)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for split in splits:
            split_size = len(split) + len(separator)
            
            # Se adicionar este split ultrapassar o limite
            if current_size + split_size > self.chunk_size and current_chunk:
                # Finalizar o chunk atual
                chunk_text = separator.join(current_chunk)
                if chunk_text:
                    chunks.append(chunk_text)
                
                # Começar novo chunk com overlap
                # Pegar os últimos itens para criar overlap
                overlap_size = 0
                overlap_items = []
                
                for item in reversed(current_chunk):
                    item_size = len(item) + len(separator)
                    if overlap_size + item_size <= self.chunk_overlap:
                        overlap_items.insert(0, item)
                        overlap_size += item_size
                    else:
                        break
                
                current_chunk = overlap_items + [split]
                current_size = sum(len(s) + len(separator) for s in current_chunk)
            else:
                # Adicionar ao chunk atual
                current_chunk.append(split)
                current_size += split_size
        
        # Adicionar o último chunk
        if current_chunk:
            chunk_text = separator.join(current_chunk)
            if chunk_text:
                chunks.append(chunk_text)
        
        return chunks
    
    def _split_by_character(self, text: str) -> List[str]:
        """Divide texto por caractere (último recurso).
        
        Args:
            text: Texto a dividir.
            
        Returns:
            Lista de chunks.
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Garantir que não quebramos no meio de uma palavra se possível
            if end < len(text):
                # Tentar encontrar um espaço próximo
                space_pos = text.rfind(' ', start, end)
                if space_pos > start:
                    end = space_pos
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Próximo chunk começa com overlap
            start = end - self.chunk_overlap
            
            # Evitar loop infinito se overlap >= chunk_size
            if start <= chunks[-1][:10].find(chunks[-2][-10:]) if len(chunks) > 1 else False:
                start = end
        
        return chunks
