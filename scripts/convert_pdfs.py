"""
scripts/convert_pdfs.py
=======================
Converte os PDFs normativos para Markdown usando Docling.

Os arquivos Markdown gerados são salvos em ``data/norms/md/``.
Esse script é executado **uma vez** (ou quando os PDFs mudarem).

Uso:
    python scripts/convert_pdfs.py
"""

from __future__ import annotations

from pathlib import Path

from docling.document_converter import DocumentConverter

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
NORMS_DIR = _PROJECT_ROOT / "data" / "norms"
OUTPUT_DIR = NORMS_DIR / "md"

# Mapeamento: nome do PDF → nome base do Markdown
PDF_FILES = {
    "NBR6120_2019.pdf": "NBR6120_2019",
    "NBR6123_2023.pdf": "NBR6123_2023",
}


def convert_all() -> None:
    """Converte todos os PDFs registrados para Markdown via Docling."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    converter = DocumentConverter()

    for pdf_name, md_base in PDF_FILES.items():
        pdf_path = NORMS_DIR / pdf_name
        if not pdf_path.exists():
            print(f"  ✗ PDF não encontrado: {pdf_path}")
            continue

        print(f"\n[convert] Convertendo {pdf_name} → {md_base}.md ...")
        result = converter.convert(str(pdf_path))
        markdown = result.document.export_to_markdown()

        md_path = OUTPUT_DIR / f"{md_base}.md"
        md_path.write_text(markdown, encoding="utf-8")
        print(f"  ✓ Salvo em: {md_path}  ({len(markdown):,} caracteres)")

    print(f"\n[convert] Conversão finalizada. Arquivos em: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
