"""
src/hybrid_search.py
====================
Retriever híbrido: BM25 (léxico) + FAISS (semântico) via Reciprocal Rank Fusion.

Algoritmo RRF:
    Para cada chunk, score = Σ 1/(60 + rank_retriever)
    onde rank_retriever é a posição no ranking de cada retriever.

Interface idêntica a indexer.retrieve() para compatibilidade com rag_pipeline.py.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi

# RRF constant (standard value)
_RRF_K = 60


def _strip_accents(text: str) -> str:
    """Remove diacríticos: 'variáveis' → 'variaveis', 'ação' → 'acao'."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def _tokenize(text: str) -> list[str]:
    """Tokeniza texto: minúsculas, remove diacríticos, divide em tokens alfanuméricos.

    A remoção de diacríticos garante que queries sem acentos (ex.: 'tipico')
    correspondam a termos acentuados no corpus (ex.: 'típico') no BM25.
    """
    return [tok for tok in re.split(r"\W+", _strip_accents(text.lower())) if tok]


class SparseRetriever:
    """
    Retriever esparso usando BM25 (sem FAISS).
    Interface idêntica a HybridRetriever para compatibilidade com rag_pipeline.py.
    """

    def __init__(self, chunks: list[dict]) -> None:
        self.chunks = chunks
        tokenized_corpus = [_tokenize(chunk["texto"]) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        """
        Retorna top-k chunks usando BM25 puro.

        Parâmetros
        ----------
        query : str
        k : int

        Retorna
        -------
        list[dict] com rank, chunk_id, doc_id, secao, score, texto
        """
        tokenized_query = _tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:k]

        results = []
        for rank, idx in enumerate(top_indices, start=1):
            chunk = self.chunks[int(idx)].copy()
            chunk["rank"] = rank
            chunk["score"] = float(scores[int(idx)])
            results.append(chunk)
        return results


class HybridRetriever:
    """
    Retriever híbrido que combina BM25 (léxico) e FAISS (semântico)
    via Reciprocal Rank Fusion (RRF).

    Interface idêntica a indexer.retrieve() para compatibilidade com
    rag_pipeline.py.
    """

    def __init__(
        self,
        chunks: list[dict[str, Any]],
        faiss_index: Any,
        embedding_model: Any,
    ) -> None:
        """
        Parâmetros
        ----------
        chunks : list[dict]
            Lista de chunk dicts (mesmo formato usado em indexer.py).
        faiss_index : faiss.IndexFlatIP
            Índice FAISS já carregado.
        embedding_model : SentenceTransformer
            Modelo de embedding já carregado.
        """
        self.chunks = chunks
        self.faiss_index = faiss_index
        self.embedding_model = embedding_model

        # Constrói índice BM25 a partir dos textos dos chunks
        tokenized_corpus = [_tokenize(chunk["texto"]) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """
        Retorna os top-k chunks usando busca híbrida BM25+FAISS com RRF.

        Algoritmo
        ---------
        1. BM25: obtém os top min(k*3, len(chunks)) resultados.
        2. FAISS: obtém os top min(k*3, len(chunks)) resultados.
        3. RRF fusion: para cada chunk_id único,
           score = Σ 1/(60 + rank) sobre os dois retrievers.
        4. Ordena por RRF score decrescente, retorna top k.
        5. Atribui rank 1..k e define score = rrf_score.

        Parâmetros
        ----------
        query : str
            Pergunta em linguagem natural.
        k : int
            Número de resultados a retornar (padrão: 5).

        Retorna
        -------
        list[dict]
            Lista de k resultados, cada um com:
            - ``rank``     : posição no ranking (1 = mais relevante)
            - ``chunk_id`` : ID rastreável do chunk
            - ``doc_id``   : documento de origem
            - ``secao``    : seção normativa detectada
            - ``score``    : RRF score (soma de 1/(60+rank) por retriever)
            - ``texto``    : conteúdo do chunk
            - mais campos originais do chunk dict
        """
        n_candidates = min(k * 3, len(self.chunks))

        # ------------------------------------------------------------------
        # 1. BM25 — ranking léxico
        # ------------------------------------------------------------------
        tokenized_query = _tokenize(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)
        # argsort descending, take top n_candidates
        bm25_top_indices = np.argsort(bm25_scores)[::-1][:n_candidates]

        # ------------------------------------------------------------------
        # 2. FAISS — ranking semântico
        # ------------------------------------------------------------------
        query_vec = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        faiss_scores, faiss_raw_indices = self.faiss_index.search(query_vec, n_candidates)
        faiss_top_indices = faiss_raw_indices[0]

        # ------------------------------------------------------------------
        # 3. RRF fusion
        # ------------------------------------------------------------------
        rrf_scores: dict[int, float] = {}

        for rank, idx in enumerate(bm25_top_indices, start=1):
            rrf_scores[int(idx)] = rrf_scores.get(int(idx), 0.0) + 1.0 / (_RRF_K + rank)

        for rank, idx in enumerate(faiss_top_indices, start=1):
            rrf_scores[int(idx)] = rrf_scores.get(int(idx), 0.0) + 1.0 / (_RRF_K + rank)

        # ------------------------------------------------------------------
        # 4. Sort by RRF score descending, take top k
        # ------------------------------------------------------------------
        sorted_indices = sorted(rrf_scores, key=lambda i: rrf_scores[i], reverse=True)[:k]

        # ------------------------------------------------------------------
        # 5. Build results with rank and score (same format as indexer.retrieve)
        # ------------------------------------------------------------------
        results = []
        for rank, idx in enumerate(sorted_indices, start=1):
            chunk = self.chunks[idx].copy()
            chunk["rank"] = rank
            chunk["score"] = rrf_scores[idx]
            results.append(chunk)

        return results
