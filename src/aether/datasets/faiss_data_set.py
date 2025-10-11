"""
Implementação de um IDataSet que armazena e carrega um índice vetorial FAISS
e seu mapeamento de IDs.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import faiss


class FaissDataSet:
    """
    Um IDataSet que gerencia um índice FAISS e um mapeamento de ID.

    Lida com a serialização e desserialização de um índice vetorial e um
    dicionário que mapeia os índices do FAISS (posições) para IDs de
    documentos externos.
    """

    def __init__(self, path: str):
        self._base_path = Path(path)
        self._index_path = self._base_path.with_suffix(".faiss")
        self._map_path = self._base_path.with_suffix(".json")
        self._index: Optional[faiss.Index] = None
        self._id_map: Optional[Dict[int, str]] = None

    def load(self) -> Tuple[Optional[faiss.Index], Optional[Dict[int, str]]]:
        """
        Carrega o índice FAISS e o mapa de IDs do disco.

        Returns:
            Uma tupla contendo o índice e o mapa de IDs, ou (None, None) se
            os arquivos não existirem.
        """
        if self._index_path.exists() and self._map_path.exists():
            print(f"Carregando índice de {self._index_path}")
            self._index = faiss.read_index(str(self._index_path))
            with open(self._map_path, "r") as f:
                # As chaves do JSON são strings, então as convertemos de volta para int
                self._id_map = {int(k): v for k, v in json.load(f).items()}
        else:
            print("Arquivos de índice não encontrados, retornando None.")
            self._index = None
            self._id_map = None
        return self._index, self._id_map

    def save(self, data: Tuple[faiss.Index, Dict[int, str]]) -> None:
        """
        Salva o índice FAISS e o mapa de IDs no disco.

        Args:
            data: Uma tupla contendo o índice FAISS e o mapa de IDs a serem salvos.
        """
        index, id_map = data

        if not isinstance(index, faiss.Index) or not isinstance(id_map, dict):
            raise TypeError("Os dados devem ser uma tupla de (faiss.Index, dict).")

        # Garante que o diretório de destino exista
        self._base_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Salvando índice com {index.ntotal} vetores em {self._index_path}")
        faiss.write_index(index, str(self._index_path))

        with open(self._map_path, "w") as f:
            json.dump(id_map, f, indent=2)
        print(f"Mapa de ID salvo em {self._map_path}")

        self._index = index
        self._id_map = id_map
