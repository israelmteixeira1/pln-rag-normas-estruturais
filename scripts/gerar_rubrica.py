"""
scripts/gerar_rubrica.py
========================
Gera respostas do pipeline RAG para as perguntas do golden set e salva
um template de rubrica pronto para avaliação manual.

Saída
-----
data/eval/rubrica_respostas.json  — perguntas + respostas geradas + template de scores
data/eval/rubrica_respostas.md    — versão legível para impressão / avaliação

Uso:
    python scripts/gerar_rubrica.py
    python scripts/gerar_rubrica.py --provider groq --k 5 --n 15
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(_PROJECT_ROOT / ".env")

from src.ingestion import load_sections
from src.chunker import chunk_sections
from src.indexer import load_embedding_model, build_index, save_index, retrieve
from src.hybrid_search import SparseRetriever, HybridRetriever
from src.rag_pipeline import RAGPipeline
from src.evaluator import load_golden_set

# ---------------------------------------------------------------------------
EVAL_DIR = _PROJECT_ROOT / "data" / "eval"
SECTIONS_BASE_DIR = _PROJECT_ROOT / "data" / "norms" / "sections"
INDEX_DIR = _PROJECT_ROOT / "index"

# Critérios da rubrica e suas escalas
RUBRICA_CRITERIA = {
    "groundedness": {
        "descricao": "Resposta está suportada pelos trechos recuperados?",
        "escala": "0=não suportada | 1=parcialmente suportada | 2=totalmente suportada",
    },
    "correcao": {
        "descricao": "Resposta está correta conforme as normas ABNT?",
        "escala": "0=incorreta | 1=parcialmente correta | 2=correta",
    },
    "citacoes": {
        "descricao": "Cita trechos adequados e coerentes?",
        "escala": "0=sem citações ou erradas | 1=citações parciais | 2=citações adequadas",
    },
    "alucinacao": {
        "descricao": "Inventou informação fora do corpus?",
        "escala": "0=sim (alucinação presente) | 1=não (sem alucinação)",
    },
    "recusa": {
        "descricao": "Quando sem evidência, recusou corretamente? (N/A para perguntas com resposta)",
        "escala": "0=não recusou / recusou indevidamente | 1=recusou corretamente | null=não aplicável",
    },
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Gera respostas RAG para avaliação de rubrica.")
    p.add_argument("--provider", default="groq", choices=["groq", "gemini", "nvidia"])
    p.add_argument("--mode", default="dense", choices=["dense", "sparse", "hybrid"])
    p.add_argument("--k", type=int, default=5, help="Top-k chunks para retrieval")
    p.add_argument("--n", type=int, default=None, help="Número de perguntas a processar (padrão: todas)")
    p.add_argument("--delay", type=float, default=1.5, help="Delay em segundos entre chamadas ao LLM")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    print(f"[rubrica] Configuração: provider={args.provider} | mode={args.mode} | k={args.k}")
    print(f"[rubrica] Carregando corpus e construindo índice...\n")

    # --- Carrega corpus e índice ---
    sections = load_sections(SECTIONS_BASE_DIR)
    chunks = chunk_sections(sections)
    embed_model = load_embedding_model()
    faiss_index, indexed_chunks = build_index(chunks, model=embed_model)
    save_index(faiss_index, indexed_chunks, index_dir=INDEX_DIR)

    sparse_ret = SparseRetriever(indexed_chunks)
    hybrid_ret = HybridRetriever(indexed_chunks, faiss_index, embed_model)

    pipeline = RAGPipeline(provider=args.provider, index_dir=INDEX_DIR)

    # --- Seleciona retriever pelo modo ---
    retriever_obj = None
    if args.mode == "sparse":
        retriever_obj = sparse_ret
    elif args.mode == "hybrid":
        retriever_obj = hybrid_ret

    # --- Carrega golden set ---
    golden_set = load_golden_set(EVAL_DIR / "golden_set.json")

    perguntas = [q for q in golden_set]
    if args.n:
        perguntas = perguntas[: args.n]

    print(f"[rubrica] Gerando respostas para {len(perguntas)} perguntas...\n")

    resultados = []
    for i, q in enumerate(perguntas, start=1):
        pergunta = q["pergunta"]
        categoria = q["categoria"]
        ev = q["evidencia_esperada"]

        print(f"  [{i:02d}/{len(perguntas)}] {pergunta[:70]}...")

        try:
            res = pipeline.query(pergunta, k=args.k, mode=args.mode, retriever=retriever_obj)
            resposta = res["answer"]
            fontes = [s["chunk_id"] for s in res["sources"]]
            latencia = res["latency"]
        except Exception as e:
            resposta = f"[ERRO: {e}]"
            fontes = []
            latencia = {}

        # Template de scores (para preenchimento manual)
        scores = {
            "groundedness": None,
            "correcao": None,
            "citacoes": None,
            "alucinacao": None,
            "recusa": None if categoria != "fora_do_corpus" else None,
        }

        resultados.append({
            "id": q["id"],
            "pergunta": pergunta,
            "categoria": categoria,
            "evidencia_esperada": ev,
            "resposta_gerada": resposta,
            "chunks_recuperados": fontes,
            "latencia_s": latencia,
            "scores": scores,
            "observacoes": "",
        })

        if i < len(perguntas):
            time.sleep(args.delay)

    # --- Salva JSON ---
    output_json = EVAL_DIR / "rubrica_respostas.json"
    payload = {
        "config": {
            "provider": args.provider,
            "mode": args.mode,
            "k": args.k,
            "n_perguntas": len(resultados),
        },
        "criterios": RUBRICA_CRITERIA,
        "avaliacoes": resultados,
    }
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n[rubrica] ✓ JSON salvo em: {output_json}")

    # --- Salva Markdown legível ---
    output_md = EVAL_DIR / "rubrica_respostas.md"
    lines = [
        "# Rubrica Qualitativa — RAG Normas Estruturais\n",
        f"\n**Provider:** {args.provider} | **Modo:** {args.mode} | **k:** {args.k}\n",
        "\n## Escala de avaliação\n",
        "\n| Critério | Escala |",
        "|---|---|",
    ]
    for crit, info in RUBRICA_CRITERIA.items():
        lines.append(f"| **{crit}** — {info['descricao']} | {info['escala']} |")

    lines.append("\n---\n")

    for r in resultados:
        ev = r["evidencia_esperada"]
        ev_str = ", ".join(ev) if isinstance(ev, list) else (str(ev) if ev else "*(fora do corpus)*")
        lines += [
            f"\n## Pergunta {r['id']} — `{r['categoria']}`\n",
            f"**Pergunta:** {r['pergunta']}\n",
            f"**Evidência esperada:** `{ev_str}`\n",
            f"**Chunks recuperados:** {', '.join([f'`{c}`' for c in r['chunks_recuperados']]) or '*(nenhum)*'}\n",
            "\n**Resposta gerada:**\n",
            f"> {r['resposta_gerada'].replace(chr(10), chr(10)+'> ')}\n",
            "\n**Avaliação:**\n",
            "| Critério | Score | Observação |",
            "|---|---|---|",
            "| Groundedness | ___ | |",
            "| Correção | ___ | |",
            "| Citações | ___ | |",
            "| Alucinação | ___ | |",
            "| Recusa | ___ | |",
            "\n---",
        ]

    output_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[rubrica] ✓ Markdown salvo em: {output_md}")
    print(f"\n[rubrica] Próximo passo: preencha os scores em {output_json}")


if __name__ == "__main__":
    main()
