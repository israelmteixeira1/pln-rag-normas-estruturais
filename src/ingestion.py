"""
src/ingestion.py
================
Módulo de ingestão de PDFs normativos.

Responsabilidades
-----------------
- Extrair texto bruto dos PDFs com pdfplumber
- Associar metadados fixos a cada documento (doc_id, titulo, fonte, edição)
- Detectar estrutura hierárquica via regex para informar o chunker

Documentos suportados
---------------------
- NBR6118_2023.pdf  → Projeto de estruturas de concreto
- NBR6120_2019.pdf  → Ações para o cálculo de estruturas de edifícios
- NBR6123_2023.pdf  → Forças devidas ao vento em edificações
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import pdfplumber
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Diretório padrão dos PDFs (relativo à raiz do projeto)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
NORMS_DIR = _PROJECT_ROOT / "data" / "norms"

# ---------------------------------------------------------------------------
# Metadados fixos por documento
# ---------------------------------------------------------------------------
DOCUMENT_METADATA: dict[str, dict[str, str]] = {
    "NBR6118": {
        "doc_id": "NBR6118",
        "titulo": "Projeto de estruturas de concreto — Procedimento",
        "fonte": "ABNT",
        "edicao": "2023",
        "filename": "NBR6118_2023.pdf",
    },
    "NBR6120": {
        "doc_id": "NBR6120",
        "titulo": "Ações para o cálculo de estruturas de edificações",
        "fonte": "ABNT",
        "edicao": "2019",
        "filename": "NBR6120_2019.pdf",
    },
    "NBR6123": {
        "doc_id": "NBR6123",
        "titulo": "Forças devidas ao vento em edificações",
        "fonte": "ABNT",
        "edicao": "2023 (Proposta de Revisão)",
        "filename": "NBR6123_2023_PROPOSTA.pdf",
    },
}

# ---------------------------------------------------------------------------
# Regex para detecção de seções normativas
# Padrão: número seguido de ponto(s) + letra maiúscula inicial
# Ex.: "4.2.3 Ações variáveis"  "13 — Dimensionamento"
# ---------------------------------------------------------------------------
_SECTION_PATTERN = re.compile(
    r"^(\d{1,2}(?:\.\d{1,3}){0,4})\s+[\u00C0-\u017EA-Z]",
    re.MULTILINE,
)


def _detect_section(text: str) -> str:
    """
    Detecta o número da seção mais provável no início de um bloco de texto.

    Percorre as primeiras 300 caracteres do texto procurando o padrão
    numérico de item normativo (ex.: '4.2', '13.2.1').

    Parâmetros
    ----------
    text : str
        Texto de um chunk ou página.

    Retorna
    -------
    str
        Número da seção (ex.: '4.2.3') ou 'intro' se nenhum for detectado.
    """
    sample = text[:300]
    match = _SECTION_PATTERN.search(sample)
    if match:
        return match.group(1)
    return "intro"


def extract_text_from_pdf(pdf_path: str | Path) -> list[dict[str, Any]]:
    """
    Extrai texto página a página de um PDF usando pdfplumber.

    Tabelas são extraídas separadamente e concatenadas abaixo do texto
    da página para preservar o contexto numérico (valores, unidades).

    Parâmetros
    ----------
    pdf_path : str | Path
        Caminho absoluto para o arquivo PDF.

    Retorna
    -------
    list[dict]
        Lista de dicts com ``page_num`` (int) e ``text`` (str) para cada página.
    """
    pdf_path = Path(pdf_path)
    pages: list[dict[str, Any]] = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            # Extrai texto corrido da página
            raw_text = page.extract_text() or ""

            # Extrai tabelas e serializa como texto TSV para preservar
            # os valores e unidades sem perder a estrutura matricial
            table_texts: list[str] = []
            for table in page.extract_tables():
                rows = []
                for row in table:
                    cleaned = [
                        str(cell).strip() if cell else "" for cell in row
                    ]
                    rows.append("\t".join(cleaned))
                if rows:
                    table_texts.append("[TABELA]\n" + "\n".join(rows) + "\n[/TABELA]")

            combined = raw_text
            if table_texts:
                combined = raw_text + "\n\n" + "\n\n".join(table_texts)

            if combined.strip():
                pages.append({"page_num": i, "text": combined.strip()})

    return pages


def load_document(doc_id: str, norms_dir: str | Path = NORMS_DIR) -> dict[str, Any]:
    """
    Carrega texto completo e metadados de um documento normativo.

    Parâmetros
    ----------
    doc_id : str
        Identificador do documento ('NBR6118', 'NBR6120' ou 'NBR6123').
    norms_dir : str | Path
        Diretório onde os PDFs estão armazenados.

    Retorna
    -------
    dict
        Dicionário com todos os metadados + lista de páginas + texto completo.

    Raises
    ------
    ValueError
        Se ``doc_id`` não estiver registrado em DOCUMENT_METADATA.
    FileNotFoundError
        Se o arquivo PDF não existir em ``norms_dir``.
    """
    if doc_id not in DOCUMENT_METADATA:
        raise ValueError(
            f"doc_id '{doc_id}' desconhecido. "
            f"Opções: {list(DOCUMENT_METADATA.keys())}"
        )

    meta = DOCUMENT_METADATA[doc_id].copy()
    pdf_path = Path(norms_dir) / meta["filename"]

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    print(f"[ingestion] Carregando {doc_id} ({pdf_path.name})...")
    pages = extract_text_from_pdf(pdf_path)

    # Texto completo: concatena todas as páginas
    full_text = "\n\n".join(p["text"] for p in pages)

    return {
        **meta,
        "pages": pages,
        "n_pages": len(pages),
        "full_text": full_text,
        "n_chars": len(full_text),
    }


def load_all_documents(norms_dir: str | Path = NORMS_DIR) -> list[dict[str, Any]]:
    """
    Carrega todos os documentos normativos registrados.

    Parâmetros
    ----------
    norms_dir : str | Path
        Diretório onde os PDFs estão armazenados.

    Retorna
    -------
    list[dict]
        Lista com um dicionário por documento, incluindo metadados e texto.
    """
    documents = []
    doc_ids = list(DOCUMENT_METADATA.keys())

    for doc_id in tqdm(doc_ids, desc="Ingestão de normas"):
        try:
            doc = load_document(doc_id, norms_dir)
            documents.append(doc)
            print(
                f"  ✓ {doc_id}: {doc['n_pages']} páginas, "
                f"{doc['n_chars']:,} caracteres"
            )
        except FileNotFoundError as e:
            print(f"  ✗ {doc_id}: {e}")

    print(f"\n[ingestion] {len(documents)}/{len(doc_ids)} documentos carregados.")
    return documents


# ---------------------------------------------------------------------------
# Utilitário de inspeção
# ---------------------------------------------------------------------------

def print_document_summary(doc: dict[str, Any]) -> None:
    """Exibe um resumo formatado de um documento carregado."""
    print(f"\n{'='*60}")
    print(f"  doc_id  : {doc['doc_id']}")
    print(f"  titulo  : {doc['titulo']}")
    print(f"  fonte   : {doc['fonte']}")
    print(f"  edicao  : {doc['edicao']}")
    print(f"  páginas : {doc['n_pages']}")
    print(f"  chars   : {doc['n_chars']:,}")
    print(f"{'='*60}")
    # Amostra das primeiras 500 chars do texto
    preview = doc["full_text"][:500].replace("\n", " ")
    print(f"  preview : {preview}...")


if __name__ == "__main__":
    # Execução direta: ingere todos os documentos e exibe resumo
    docs = load_all_documents()
    for d in docs:
        print_document_summary(d)
