"""
src/indexer.py
==============
Módulo de indexação vetorial e retrieval para o corpus normativo.

Modelo de Embedding
--------------------
Utiliza ``neuralmind/bert-base-portuguese-cased`` via sentence-transformers.

Justificativa: modelo pré-treinado exclusivamente em português (BERT-PT-BR),
mantido pelo neuralmind. Apresenta excelente desempenho em tarefas de
similaridade semântica para textos técnicos e jurídicos em português,
sem necessitar de API externa — fundamental para reprodutibilidade em
ambientes Google Colab sem chave de API.

Índice FAISS
------------
Utiliza ``IndexFlatIP`` (produto interno) com vetores L2-normalizados,
o que equivale a busca por similaridade de cosseno. Optou-se por ``FlatIP``
(busca exata) em vez de aproximada (IVF/HNSW) pois o corpus é pequeno
(~1.000–3.000 chunks), tornando a busca exata viável e mais precisa.

Persistência
------------
- ``index/faiss.index``            → índice vetorial serializado
- ``index/chunks_metadata.json``   → lista de dicts com todos os metadados
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Modelo de embedding (PT-BR técnico)
# ---------------------------------------------------------------------------
EMBEDDING_MODEL = "neuralmind/bert-base-portuguese-cased"

# Diretório de persistência do índice
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_DIR = _PROJECT_ROOT / "index"

# Nomes dos arquivos persistidos
INDEX_FILE = INDEX_DIR / "faiss.index"
METADATA_FILE = INDEX_DIR / "chunks_metadata.json"
MODEL_INFO_FILE = INDEX_DIR / "model_info.json"

# k's suportados pelo retriever
SUPPORTED_K = (3, 5, 10)


def load_embedding_model(model_name: str = EMBEDDING_MODEL) -> SentenceTransformer:
    """
    Carrega o modelo de embedding a partir do HuggingFace Hub.

    Parâmetros
    ----------
    model_name : str
        Nome do modelo HuggingFace (padrão: bert-base-portuguese-cased).

    Retorna
    -------
    SentenceTransformer
        Modelo carregado e pronto para encoding.
    """
    print(f"[indexer] Carregando modelo de embedding: {model_name}")
    model = SentenceTransformer(model_name)
    print(f"[indexer] Modelo carregado. Dimensão dos vetores: {model.get_sentence_embedding_dimension()}")
    return model


def embed_chunks(
    chunks: list[dict[str, Any]],
    model: SentenceTransformer,
    batch_size: int = 32,
) -> np.ndarray:
    """
    Gera embeddings para todos os chunks do corpus.

    Os vetores são L2-normalizados para permitir busca por cosseno
    via produto interno (IndexFlatIP).

    Parâmetros
    ----------
    chunks : list[dict]
        Lista de chunks com chave ``texto``.
    model : SentenceTransformer
        Modelo de embedding já carregado.
    batch_size : int
        Tamanho do batch para encoding (padrão: 32).

    Retorna
    -------
    np.ndarray
        Matriz de embeddings de shape ``(n_chunks, dim)`` normalizada L2.
    """
    texts = [c["texto"] for c in chunks]
    print(f"[indexer] Gerando embeddings para {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,  # L2 norm → cosseno via produto interno
    )

    print(f"[indexer] Embeddings gerados. Shape: {embeddings.shape}")
    return embeddings.astype(np.float32)


def build_index(
    chunks: list[dict[str, Any]],
    model: SentenceTransformer | None = None,
    model_name: str = EMBEDDING_MODEL,
) -> tuple[faiss.Index, list[dict[str, Any]]]:
    """
    Constrói o índice FAISS a partir dos chunks do corpus.

    Parâmetros
    ----------
    chunks : list[dict]
        Lista de chunks com ``texto`` e metadados.
    model : SentenceTransformer | None
        Modelo pré-carregado. Se None, carrega ``model_name``.
    model_name : str
        Nome do modelo HuggingFace (usado se ``model`` é None).

    Retorna
    -------
    tuple[faiss.Index, list[dict]]
        (índice FAISS, lista de chunks com metadados correspondentes)
    """
    if model is None:
        model = load_embedding_model(model_name)

    embeddings = embed_chunks(chunks, model)

    # Cria índice de produto interno (= cosseno com vetores normalizados)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    print(f"[indexer] Índice FAISS criado com {index.ntotal} vetores (dim={dim}).")
    return index, chunks


def save_index(
    index: faiss.Index,
    chunks: list[dict[str, Any]],
    index_dir: str | Path = INDEX_DIR,
    model_name: str = EMBEDDING_MODEL,
) -> None:
    """
    Persiste o índice FAISS e os metadados dos chunks em disco.

    Parâmetros
    ----------
    index : faiss.Index
        Índice FAISS construído com ``build_index()``.
    chunks : list[dict]
        Lista de chunks com metadados (sem o campo ``texto`` completo
        para reduzir tamanho do arquivo — o texto é incluído, pois
        precisamos dele para exibir os resultados ao usuário).
    index_dir : str | Path
        Diretório de destino (padrão: ``index/``).
    model_name : str
        Nome do modelo usado, salvo em ``model_info.json``.
    """
    index_dir = Path(index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)

    # Salva índice FAISS
    idx_path = index_dir / "faiss.index"
    faiss.write_index(index, str(idx_path))
    print(f"[indexer] Índice salvo em: {idx_path}")

    # Salva metadados dos chunks (incluindo texto para exibição)
    meta_path = index_dir / "chunks_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[indexer] Metadados salvos em: {meta_path}")

    # Salva informação do modelo
    model_info_path = index_dir / "model_info.json"
    with open(model_info_path, "w", encoding="utf-8") as f:
        json.dump({"embedding_model": model_name}, f, ensure_ascii=False)


def load_index(
    index_dir: str | Path = INDEX_DIR,
) -> tuple[faiss.Index, list[dict[str, Any]], SentenceTransformer]:
    """
    Carrega o índice FAISS, metadados e modelo de embedding do disco.

    Parâmetros
    ----------
    index_dir : str | Path
        Diretório onde os artefatos estão salvos.

    Retorna
    -------
    tuple[faiss.Index, list[dict], SentenceTransformer]
        (índice, chunks com metadados, modelo de embedding)

    Raises
    ------
    FileNotFoundError
        Se o índice ou metadados não forem encontrados.
    """
    index_dir = Path(index_dir)
    idx_path = index_dir / "faiss.index"
    meta_path = index_dir / "chunks_metadata.json"
    model_info_path = index_dir / "model_info.json"

    for p in [idx_path, meta_path]:
        if not p.exists():
            raise FileNotFoundError(
                f"Artefato de índice não encontrado: {p}\n"
                "Execute build_index() e save_index() primeiro."
            )

    # Carrega modelo
    model_name = EMBEDDING_MODEL
    if model_info_path.exists():
        with open(model_info_path, encoding="utf-8") as f:
            model_name = json.load(f).get("embedding_model", EMBEDDING_MODEL)

    model = load_embedding_model(model_name)

    # Carrega índice FAISS
    index = faiss.read_index(str(idx_path))
    print(f"[indexer] Índice FAISS carregado: {index.ntotal} vetores.")

    # Carrega metadados
    with open(meta_path, encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"[indexer] Metadados carregados: {len(chunks)} chunks.")

    return index, chunks, model


def retrieve(
    query: str,
    index: faiss.Index,
    chunks: list[dict[str, Any]],
    model: SentenceTransformer,
    k: int = 5,
) -> list[dict[str, Any]]:
    """
    Recupera os ``k`` chunks mais relevantes para uma query.

    Parâmetros
    ----------
    query : str
        Pergunta em linguagem natural.
    index : faiss.Index
        Índice FAISS carregado.
    chunks : list[dict]
        Lista de chunks com metadados (mesma ordem usada na indexação).
    model : SentenceTransformer
        Modelo de embedding.
    k : int
        Número de resultados a retornar. Recomendado: 3, 5 ou 10.

    Retorna
    -------
    list[dict]
        Lista de ``k`` resultados, cada um com:
        - ``rank``     : posição no ranking (1 = mais relevante)
        - ``chunk_id`` : ID rastreável do chunk
        - ``doc_id``   : documento de origem
        - ``secao``    : seção normativa detectada
        - ``score``    : similaridade de cosseno [0, 1]
        - ``texto``    : conteúdo do chunk

    Raises
    ------
    ValueError
        Se ``k`` for maior que o número de chunks no índice.
    """
    if k > index.ntotal:
        raise ValueError(
            f"k={k} maior que o número de chunks no índice ({index.ntotal})."
        )

    # Embed da query (normalizado para cosseno)
    query_vec = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)

    # Busca nos k vizinhos mais próximos
    scores, indices = index.search(query_vec, k)

    results = []
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        chunk = chunks[idx].copy()
        chunk["rank"] = rank
        chunk["score"] = float(score)
        results.append(chunk)

    return results


def print_retrieval_results(results: list[dict[str, Any]], query: str) -> None:
    """Exibe os resultados de retrieval de forma formatada."""
    print(f"\n{'='*70}")
    print(f"  Query: {query}")
    print(f"{'='*70}")
    for r in results:
        print(f"\n  Rank #{r['rank']} | {r['chunk_id']} | score={r['score']:.4f}")
        print(f"  [{r['doc_id']}] Seção {r['secao']}")
        print(f"  {'-'*60}")
        preview = r["texto"][:300].replace("\n", " ")
        print(f"  {preview}...")
    print(f"{'='*70}")


if __name__ == "__main__":
    # Execução direta: testa o retriever com uma query de exemplo
    print("[indexer] Carregando índice do disco...")
    idx, chks, mdl = load_index()

    test_query = "Qual o valor de carga acidental para um pavimento de escritório?"
    for k_val in SUPPORTED_K:
        results = retrieve(test_query, idx, chks, mdl, k=k_val)
        print_retrieval_results(results, f"{test_query} [k={k_val}]")
