"""
Implementações de Jobs para um pipeline RAG (Retrieval-Augmented Generation).
"""

from typing import Any, Dict, List, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from aether.core.interfaces import AbstractJob


class EmbeddingJob(AbstractJob):
    """
    Gera embeddings vetoriais para uma lista de documentos de texto.
    """

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        super().__init__(name, params)
        # O modelo será baixado na primeira utilização
        self._model = SentenceTransformer(
            self.params.get("model_name", "all-MiniLM-L6-v2")
        )

    def _execute(self, **loaded_inputs: Any) -> Dict[str, Any]:
        """
        Args:
            loaded_inputs: Espera um dicionário com a chave 'documents',
                           onde o valor é uma lista de dicionários,
                           cada um com 'id' e 'text'.
        """
        documents: List[Dict[str, str]] = loaded_inputs.get("documents", [])
        if not documents:
            return {"embeddings": {}}

        texts = [doc["text"] for doc in documents]
        ids = [doc["id"] for doc in documents]

        print(f"Gerando embeddings para {len(texts)} documentos...")
        embeddings = self._model.encode(texts, convert_to_numpy=True)

        embeddings_map = {doc_id: emb for doc_id, emb in zip(ids, embeddings)}
        print("Embeddings gerados com sucesso.")

        return {"embeddings": embeddings_map}


class IndexingJob(AbstractJob):
    """
    Indexa embeddings em um índice FAISS.
    """

    def _execute(self, **loaded_inputs: Any) -> Dict[str, Any]:
        """
        Args:
            loaded_inputs: Espera:
                           - 'embeddings': Um mapa de {doc_id: embedding}.
        """
        embeddings_map: Dict[str, np.ndarray] = loaded_inputs.get("embeddings", {})

        if not embeddings_map:
            print("Nenhum embedding para indexar.")
            # Retorna um índice vazio se não houver entrada
            return {"faiss_index": (None, {})}

        index: Optional[faiss.Index] = None
        id_map: Dict[int, str] = {}

        doc_ids = list(embeddings_map.keys())
        vectors = np.array(list(embeddings_map.values())).astype("float32")

        dimension = vectors.shape[1]

        if index is None:
            print(f"Criando novo índice FAISS com dimensão {dimension}.")
            index = faiss.IndexFlatL2(dimension)
            id_map = {}

        # Adiciona os novos vetores ao índice
        start_index = index.ntotal
        index.add(vectors)
        print(f"Adicionados {len(vectors)} vetores ao índice.")

        # Atualiza o mapa de IDs
        for i, doc_id in enumerate(doc_ids):
            id_map[start_index + i] = doc_id

        return {"faiss_index": (index, id_map)}
