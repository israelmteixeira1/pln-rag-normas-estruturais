"""
src/ingestion.py
================
Módulo de ingestão de seções normativas a partir de arquivos Markdown.

Responsabilidades
-----------------
- Ler os arquivos de seção Markdown em ``data/norms/sections/<norm_id>/``
- Extrair frontmatter YAML (title, summary, norm_id, edicao) de cada seção
- Agregar seções de múltiplas normas em uma lista unificada de chunks

Os arquivos de seção são gerados pelo script
``scripts/split_sections_auto.py``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from tqdm import tqdm

# ---------------------------------------------------------------------------
# Diretório base das seções (relativo à raiz do projeto)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECTIONS_BASE_DIR = _PROJECT_ROOT / "data" / "norms" / "sections"

# ---------------------------------------------------------------------------
# Metadados fixos por norma (complementam o frontmatter dos arquivos)
# ---------------------------------------------------------------------------
NORMS_METADATA: dict[str, dict[str, str]] = {
    "nbr6120": {
        "doc_id": "NBR6120",
        "titulo": "Cargas para o cálculo de estruturas de edificações",
        "fonte": "ABNT",
        "edicao": "2019",
    },
    "nbr6123": {
        "doc_id": "NBR6123",
        "titulo": "Forças devidas ao vento em edificações",
        "fonte": "ABNT",
        "edicao": "2023",
    },
}

# ---------------------------------------------------------------------------
# Regex para extrair frontmatter YAML
# ---------------------------------------------------------------------------
_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n",
    re.DOTALL,
)

_YAML_FIELD_RE = re.compile(r'^(\w+):\s*"?(.+?)"?\s*$', re.MULTILINE)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Extrai frontmatter YAML e conteúdo de um arquivo de seção."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text.strip()

    yaml_block = match.group(1)
    content = text[match.end():].strip()

    fields = {}
    for field_match in _YAML_FIELD_RE.finditer(yaml_block):
        fields[field_match.group(1)] = field_match.group(2).strip('"')

    return fields, content


def load_sections(
    sections_dir: str | Path | None = None,
    norm_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Carrega seções normativas como chunks com metadados.

    Parâmetros
    ----------
    sections_dir : str | Path | None
        Diretório base das seções. Padrão: ``data/norms/sections/``.
        Pode apontar diretamente para um subdiretório de norma específica.
    norm_ids : list[str] | None
        Lista de IDs de norma a carregar (ex.: ``["nbr6120", "nbr6118"]``).
        Se None, carrega todas as normas encontradas em ``sections_dir``.

    Retorna
    -------
    list[dict]
        Lista de chunks (um por seção), cada um com:
        - ``chunk_id``  : ex. ``NBR6120#02_objetivo``
        - ``doc_id``    : ex. ``NBR6120``
        - ``titulo``    : título do documento completo
        - ``fonte``     : ``ABNT``
        - ``edicao``    : edição da norma
        - ``secao``     : título da seção (do frontmatter)
        - ``summary``   : resumo da seção (do frontmatter)
        - ``texto``     : conteúdo puro (para embedding)
        - ``texto_md``  : conteúdo com frontmatter (para exibição)
        - ``n_chars``   : tamanho do conteúdo
        - ``filename``  : nome do arquivo de seção
    """
    base = Path(sections_dir) if sections_dir else SECTIONS_BASE_DIR

    if not base.exists():
        raise FileNotFoundError(
            f"Diretório de seções não encontrado: {base}. "
            "Execute scripts/split_sections_auto.py primeiro."
        )

    # Descobre subdiretórios de normas
    if norm_ids is not None:
        norm_dirs = [base / nid.lower() for nid in norm_ids]
    else:
        # Tenta subdiretórios; se não houver, assume que base é o próprio diretório de seções
        subdirs = [d for d in sorted(base.iterdir()) if d.is_dir()]
        norm_dirs = subdirs if subdirs else [base]

    all_chunks: list[dict[str, Any]] = []

    for norm_dir in norm_dirs:
        if not norm_dir.exists():
            print(f"[ingestion] ⚠  Diretório não encontrado: {norm_dir} — pulando.")
            continue

        # Determina metadados da norma pelo nome do diretório
        dir_key = norm_dir.name.lower()
        meta = NORMS_METADATA.get(dir_key, {
            "doc_id": dir_key.upper(),
            "titulo": dir_key.upper(),
            "fonte": "ABNT",
            "edicao": "—",
        })

        md_files = sorted(norm_dir.glob("*.md"))
        if not md_files:
            print(f"[ingestion] ⚠  Nenhum .md em {norm_dir} — pulando.")
            continue

        print(f"[ingestion] Carregando {meta['doc_id']} de {norm_dir} ...")

        for md_file in tqdm(md_files, desc=f"  {meta['doc_id']}"):
            raw_text = md_file.read_text(encoding="utf-8")
            frontmatter, content = _parse_frontmatter(raw_text)

            if not content.strip():
                continue

            section_id = md_file.stem
            chunk_id = f"{meta['doc_id']}#{section_id}"
            section_title = frontmatter.get("title", section_id)
            summary = frontmatter.get("summary", "")
            edicao = frontmatter.get("edicao", meta["edicao"])

            all_chunks.append({
                "chunk_id": chunk_id,
                "doc_id": meta["doc_id"],
                "titulo": meta["titulo"],
                "fonte": meta["fonte"],
                "edicao": edicao,
                "secao": section_title,
                "summary": summary,
                "texto": content,
                "texto_md": raw_text.strip(),
                "n_chars": len(content),
                "filename": md_file.name,
            })

    print(f"\n[ingestion] ✓ {len(all_chunks)} seções carregadas no total.")
    return all_chunks


# ---------------------------------------------------------------------------
# Utilitário de inspeção
# ---------------------------------------------------------------------------

def print_sections_summary(chunks: list[dict[str, Any]]) -> None:
    """Exibe um resumo formatado das seções carregadas, agrupadas por norma."""
    from itertools import groupby

    print(f"\n{'='*70}")
    print(f"  Total: {len(chunks)} seções | {sum(c['n_chars'] for c in chunks):,} chars")
    print(f"{'='*70}")

    for doc_id, group in groupby(chunks, key=lambda c: c["doc_id"]):
        group_list = list(group)
        print(f"\n  [{doc_id}] {group_list[0]['titulo']}")
        print(f"  Fonte: {group_list[0]['fonte']} | Edição: {group_list[0]['edicao']}")
        print(f"  Seções: {len(group_list)}")
        for c in group_list:
            print(f"    {c['chunk_id']:50s} {c['n_chars']:6,} chars")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    chunks = load_sections()
    print_sections_summary(chunks)
