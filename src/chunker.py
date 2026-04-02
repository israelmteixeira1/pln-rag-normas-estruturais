"""
src/chunker.py
==============
Módulo de chunking para o corpus normativo NBR 6120.

Estratégia simplificada
------------------------
Cada seção Markdown já é um chunk semântico. Não há subdivisão adicional.
As seções foram divididas manualmente pelo script
``scripts/split_nbr6120_sections.py`` para garantir qualidade semântica.

O chunker apenas repassa as seções carregadas pelo ``ingestion.py``,
adicionando estatísticas e utilitários de inspeção.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Constantes (mantidas para compatibilidade com o restante do pipeline)
# ---------------------------------------------------------------------------
CHUNK_SIZE = 800       # referência — não usado para subdivisão aqui
CHUNK_OVERLAP = 120    # referência — não usado para subdivisão aqui


def chunk_sections(
    sections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Recebe as seções do ingestion e as retorna como chunks prontos.

    Cada seção Markdown é um chunk semântico. Não há subdivisão.

    Parâmetros
    ----------
    sections : list[dict]
        Lista de seções retornadas por ``ingestion.load_sections()``.

    Retorna
    -------
    list[dict]
        Lista de chunks (idêntica às seções, para compatibilidade).
    """
    chunks = sections  # cada seção já é um chunk

    print(
        f"[chunker] NBR6120: {len(chunks)} chunks "
        f"(1 chunk por seção)"
    )
    print(f"[chunker] Total: {len(chunks)} chunks gerados.")

    return chunks


# ---------------------------------------------------------------------------
# Utilitários de inspeção
# ---------------------------------------------------------------------------

def print_chunks_stats(chunks: list[dict[str, Any]]) -> None:
    """Exibe estatísticas de distribuição de tamanho dos chunks."""
    import statistics

    sizes = [c["n_chars"] for c in chunks]

    print(f"\n{'='*60}")
    print("  ESTATÍSTICAS DOS CHUNKS")
    print(f"{'='*60}")
    print(f"  Total de chunks : {len(chunks)}")
    print(f"  Tamanho médio   : {statistics.mean(sizes):.0f} chars")
    print(f"  Tamanho mediano : {statistics.median(sizes):.0f} chars")
    print(f"  Mínimo          : {min(sizes)} chars")
    print(f"  Máximo          : {max(sizes)} chars")
    print(f"{'='*60}")

    print("\n  Detalhamento:")
    for c in chunks:
        print(f"    {c['chunk_id']:40s} {c['n_chars']:5d} chars")


def find_table_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Filtra chunks que contêm tabelas Markdown.

    Útil para verificar se tabelas normativas foram preservadas.
    """
    return [c for c in chunks if "|" in c["texto"] and "---" in c["texto"]]


if __name__ == "__main__":
    from src.ingestion import load_sections

    chunks = chunk_sections(load_sections())
    print_chunks_stats(chunks)

    table_chunks = find_table_chunks(chunks)
    print(f"\n[chunker] Chunks com tabelas: {len(table_chunks)}")
    if table_chunks:
        print("\nExemplo de chunk com tabela:")
        print(f"  chunk_id: {table_chunks[0]['chunk_id']}")
        print(f"  texto_md (primeiros 500 chars):\n{table_chunks[0]['texto_md'][:500]}")
