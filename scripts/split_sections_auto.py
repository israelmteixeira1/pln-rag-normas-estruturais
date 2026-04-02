"""
scripts/split_sections_auto.py
===============================
Divide qualquer Markdown normativo em seções baseadas em headings (## e ###).

Cada seção é salva como um arquivo .md individual em data/norms/sections/<norm_id>/
com frontmatter YAML (title, summary).

Uso:
    python scripts/split_sections_auto.py                    # todas as normas
    python scripts/split_sections_auto.py --norm NBR6118_2023
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração das normas suportadas
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
MD_DIR = _PROJECT_ROOT / "data" / "norms" / "md"
SECTIONS_BASE_DIR = _PROJECT_ROOT / "data" / "norms" / "sections"

# Metadados de cada norma: md_file → (norm_id, titulo, fonte, edicao, min_heading_level)
NORMS: dict[str, dict] = {
    "NBR6120_2019": {
        "norm_id": "NBR6120",
        "titulo": "Cargas para o cálculo de estruturas de edificações",
        "fonte": "ABNT",
        "edicao": "2019 (2ª edição)",
        "min_level": 2,  # split em ## (h2)
    },
    "NBR6123_2023": {
        "norm_id": "NBR6123",
        "titulo": "Forças devidas ao vento em edificações",
        "fonte": "ABNT",
        "edicao": "2023",
        "min_level": 2,
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def _heading_level(line: str) -> int | None:
    """Retorna o nível do heading (1-6) ou None se não for heading."""
    m = re.match(r"^(#{1,6})\s", line)
    return len(m.group(1)) if m else None


def _slugify(text: str, index: int) -> str:
    """Gera nome de arquivo seguro a partir do título."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_-]+", "_", slug).strip("_")
    slug = slug[:60]
    return f"{index:02d}_{slug}"


def _generate_summary(title: str, content: str) -> str:
    """Gera resumo automático simples: primeira linha não-vazia do conteúdo."""
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("<!--"):
            # Trunca em 120 caracteres
            return line[:120] + ("..." if len(line) > 120 else "")
    return title


def split_norm(md_name: str) -> None:
    """Divide um Markdown normativo em arquivos de seção."""
    config = NORMS.get(md_name)
    if config is None:
        raise ValueError(f"Norma desconhecida: {md_name}. Registre em NORMS.")

    md_path = MD_DIR / f"{md_name}.md"
    if not md_path.exists():
        raise FileNotFoundError(
            f"Markdown não encontrado: {md_path}. "
            "Execute scripts/convert_pdfs.py primeiro."
        )

    norm_id = config["norm_id"]
    min_level = config["min_level"]
    output_dir = SECTIONS_BASE_DIR / norm_id.lower()

    print(f"\n[split] {md_name} → {output_dir}")
    print(f"[split] Splitting em headings de nível >= {min_level} ...")

    # Limpa e recria o diretório de saída
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # --- Particionamento em seções ---
    # Cada seção começa num heading do nível alvo
    sections: list[tuple[str, str]] = []  # (title, content)
    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        level = _heading_level(line.rstrip())
        if level is not None and level <= min_level:
            # Salva seção anterior
            if current_title is not None:
                sections.append((current_title, "".join(current_lines)))
            current_title = line.lstrip("#").strip().rstrip()
            current_lines = [line]
        else:
            if current_title is None:
                # Conteúdo antes do primeiro heading → seção "Preâmbulo"
                if line.strip():
                    if not sections:
                        current_title = "Preâmbulo"
                        current_lines = [line]
                    else:
                        current_lines.append(line)
            else:
                current_lines.append(line)

    # Última seção
    if current_title is not None:
        sections.append((current_title, "".join(current_lines)))

    if not sections:
        print(f"  ✗ Nenhuma seção encontrada em {md_name}.md")
        return

    # --- Salvar arquivos ---
    for idx, (title, content) in enumerate(sections, start=1):
        # Ignora seções completamente vazias
        body = content.strip()
        if not body:
            continue

        summary = _generate_summary(title, body)
        filename = f"{_slugify(title, idx)}.md"
        filepath = output_dir / filename

        # Escapa aspas duplas no frontmatter
        safe_title = title.replace('"', "'")
        safe_summary = summary.replace('"', "'")

        frontmatter = f'---\ntitle: "{safe_title}"\nsummary: "{safe_summary}"\nnorm_id: "{norm_id}"\nedicao: "{config["edicao"]}"\n---\n'
        filepath.write_text(frontmatter + body + "\n", encoding="utf-8")
        print(f"  ✓ {filename:55s} ({len(body):6,} chars)  |  {title[:50]}")

    n_files = len(list(output_dir.glob("*.md")))
    print(f"\n[split] ✓ {n_files} seções criadas em {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Split normas em seções Markdown.")
    parser.add_argument(
        "--norm",
        choices=list(NORMS.keys()),
        default=None,
        help="Nome da norma a dividir (padrão: todas).",
    )
    args = parser.parse_args()

    norms_to_process = [args.norm] if args.norm else list(NORMS.keys())

    for md_name in norms_to_process:
        md_path = MD_DIR / f"{md_name}.md"
        if not md_path.exists():
            print(f"\n[split] ⚠  {md_name}.md não encontrado — pulando.")
            continue
        split_norm(md_name)

    print("\n[split] Processamento concluído.")


if __name__ == "__main__":
    main()
