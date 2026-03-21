"""
src/chunker.py
==============
Módulo de chunking hierárquico para o corpus normativo.

Estratégia de segmentação
--------------------------
Normas técnicas ABNT têm estrutura hierárquica rígida:
    Capítulo > Seção > Item > Tabela/Figura

Escolha de parâmetros (justificativa técnica)
----------------------------------------------
- chunk_size = 800 caracteres:
    Uma tabela típica de NBR 6120 (cargas acidentais) ocupa ~400–600 chars.
    Com 800 chars capturamos a tabela + o parágrafo normativo que a precede,
    evitando que valores numéricos percam a condição de aplicação (p.ex.
    "kN/m²" sem saber que se refere a "garagem veículos leves").

- chunk_overlap = 120 caracteres:
    Equivale a ~1–2 linhas de texto normativo. Garante que uma sentença
    cortada no final de um chunk apareça no início do próximo, preservando
    continuidade de enumerações (ex.: itens "a)", "b)", "c)") e condições
    compostas ("deve ser verificado… quando…").

- Separadores: ["\n\n", "\n", ". ", " "] — prioriza quebras naturais do
    documento antes de cortar no meio de uma frase.
"""

from __future__ import annotations

import re
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# Parâmetros de chunking (justificados no docstring do módulo)
# ---------------------------------------------------------------------------
CHUNK_SIZE = 800       # caracteres
CHUNK_OVERLAP = 120    # caracteres

# ---------------------------------------------------------------------------
# Regex para detectar o número de seção normativa em um bloco de texto
# Ex.: "4.2.3 Ações variáveis"  →  grupo 1: "4.2.3"
# ---------------------------------------------------------------------------
_SECTION_RE = re.compile(
    r"(?:^|\n)\s*(\d{1,2}(?:\.\d{1,3}){0,4})\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ]",
    re.MULTILINE,
)


def _detect_section(text: str) -> str:
    """
    Extrai o número de seção normativa mais específico presente no texto.

    Percorre todo o texto em busca do último padrão ``N.N.N`` seguido de
    letra maiúscula (início de título normativo). Retornar o *último*
    (em vez do primeiro) garante que capturamos a seção mais específica
    do chunk, já que o texto está ordenado cronologicamente.

    Parâmetros
    ----------
    text : str
        Conteúdo textual do chunk.

    Retorna
    -------
    str
        Número da seção (ex.: '4.2.3') ou 'intro' se não encontrado.
    """
    matches = _SECTION_RE.findall(text)
    if matches:
        return matches[-1]  # usa o número de seção mais específico encontrado
    return "intro"


def _make_chunk_id(doc_id: str, section: str, seq: int) -> str:
    """
    Gera um ID único e rastreável para o chunk.

    Formato: ``{doc_id}#{section}_{seq:04d}``

    Exemplos
    --------
    - ``NBR6120#3.2_0012``
    - ``NBR6118#intro_0001``
    - ``NBR6123#5.1.2_0034``

    Parâmetros
    ----------
    doc_id : str
        Identificador do documento de origem (ex.: 'NBR6120').
    section : str
        Número de seção detectado (ex.: '3.2') ou 'intro'.
    seq : int
        Número sequencial global do chunk dentro do documento.

    Retorna
    -------
    str
        ID único do chunk.
    """
    return f"{doc_id}#{section}_{seq:04d}"


def chunk_document(
    doc: dict[str, Any],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Segmenta um documento normativo em chunks hierárquicos rastreáveis.

    Cada chunk herda os metadados do documento de origem e recebe:
    - ``chunk_id``  : ID único no formato ``NBRxxxx#secao_NNNN``
    - ``secao``     : número de seção normativa detectado no chunk
    - ``n_chars``   : tamanho do chunk em caracteres

    Parâmetros
    ----------
    doc : dict
        Dicionário retornado por ``ingestion.load_document()``, com ao
        menos as chaves: ``doc_id``, ``titulo``, ``fonte``, ``edicao``,
        ``full_text``.
    chunk_size : int
        Tamanho máximo de cada chunk em caracteres (padrão: 800).
    chunk_overlap : int
        Sobreposição entre chunks consecutivos em caracteres (padrão: 120).

    Retorna
    -------
    list[dict]
        Lista de chunks, cada um com as chaves:
        ``chunk_id``, ``doc_id``, ``titulo``, ``fonte``, ``edicao``,
        ``secao``, ``texto``, ``n_chars``.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    raw_chunks = splitter.split_text(doc["full_text"])

    chunks: list[dict[str, Any]] = []
    for seq, text in enumerate(raw_chunks, start=1):
        section = _detect_section(text)
        chunk_id = _make_chunk_id(doc["doc_id"], section, seq)

        chunks.append(
            {
                "chunk_id": chunk_id,
                "doc_id": doc["doc_id"],
                "titulo": doc["titulo"],
                "fonte": doc["fonte"],
                "edicao": doc["edicao"],
                "secao": section,
                "texto": text.strip(),
                "n_chars": len(text.strip()),
            }
        )

    return chunks


def chunk_documents(
    docs: list[dict[str, Any]],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Segmenta uma lista de documentos normativos.

    Parâmetros
    ----------
    docs : list[dict]
        Lista de documentos retornados por ``ingestion.load_all_documents()``.
    chunk_size : int
        Tamanho máximo de cada chunk em caracteres.
    chunk_overlap : int
        Sobreposição entre chunks consecutivos em caracteres.

    Retorna
    -------
    list[dict]
        Lista consolidada de todos os chunks de todos os documentos.
    """
    all_chunks: list[dict[str, Any]] = []

    for doc in docs:
        doc_chunks = chunk_document(doc, chunk_size, chunk_overlap)
        all_chunks.extend(doc_chunks)
        print(
            f"[chunker] {doc['doc_id']}: {len(doc_chunks)} chunks "
            f"(size={chunk_size}, overlap={chunk_overlap})"
        )

    print(f"\n[chunker] Total: {len(all_chunks)} chunks gerados.")
    return all_chunks


# ---------------------------------------------------------------------------
# Utilitários de inspeção
# ---------------------------------------------------------------------------

def print_chunks_stats(chunks: list[dict[str, Any]]) -> None:
    """Exibe estatísticas de distribuição de tamanho dos chunks."""
    import statistics

    sizes = [c["n_chars"] for c in chunks]
    docs = {}
    for c in chunks:
        docs.setdefault(c["doc_id"], 0)
        docs[c["doc_id"]] += 1

    print(f"\n{'='*60}")
    print("  ESTATÍSTICAS DOS CHUNKS")
    print(f"{'='*60}")
    print(f"  Total de chunks : {len(chunks)}")
    print(f"  Tamanho médio   : {statistics.mean(sizes):.0f} chars")
    print(f"  Tamanho mediano : {statistics.median(sizes):.0f} chars")
    print(f"  Mínimo          : {min(sizes)} chars")
    print(f"  Máximo          : {max(sizes)} chars")
    print(f"\n  Por documento:")
    for doc_id, count in sorted(docs.items()):
        print(f"    {doc_id}: {count} chunks")
    print(f"{'='*60}")


def find_table_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Filtra chunks que contêm marcadores de tabela ``[TABELA]``.

    Útil para verificar se tabelas normativas foram preservadas com
    contexto suficiente.
    """
    return [c for c in chunks if "[TABELA]" in c["texto"]]


if __name__ == "__main__":
    from src.ingestion import load_all_documents

    docs = load_all_documents()
    chunks = chunk_documents(docs)
    print_chunks_stats(chunks)

    table_chunks = find_table_chunks(chunks)
    print(f"\n[chunker] Chunks com tabelas: {len(table_chunks)}")
    if table_chunks:
        print("\nExemplo de chunk com tabela:")
        print(f"  chunk_id: {table_chunks[0]['chunk_id']}")
        print(f"  texto (primeiros 400 chars):\n{table_chunks[0]['texto'][:400]}")
