"""
src/evaluator.py
================
Módulo de avaliação de recall do retriever usando o golden_set.json.

Definição de Recall@k
----------------------
Para cada pergunta que possui evidência esperada (não-nula):

    hit(q, k) = 1  se algum chunk em top-k contém o doc_id da evidência
              = 0  caso contrário

    Recall@k = (nº de hits) / (nº total de perguntas avaliadas)

Tratamento de casos especiais
------------------------------
- ``fora_do_corpus`` (evidencia_esperada = null):
    Excluídas do cálculo de Recall@k. São registradas separadamente para
    futura verificação de recusa do chatbot (Fase 3).

- Multi-evidência (evidencia_esperada = lista):
    Conta como HIT se **pelo menos uma** das evidências esperadas estiver
    entre os top-k resultados (hit parcial suficiente).

Correspondência chunk_id ↔ evidência_esperada
----------------------------------------------
O golden_set usa referências como ``"NBR6120#Tabela_X"`` enquanto os
chunk_ids gerados têm formato ``"NBR6120#3.2_0012"``. Como o mapeamento
exato seção↔tabela requer leitura humana das normas, usamos uma correspondência
de doc_id: verificamos se o ``doc_id`` do chunk recuperado corresponde ao
``doc_id`` da evidência esperada. Isso é uma aproximação conservadora:

    Recall@k (baseline) ≤ Recall@k (ideal com chunk_ids exatos)

Após o domínio mapear os chunk_ids corretos, o golden_set pode ser
atualizado com os IDs exatos para uma avaliação mais precisa.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

# ---------------------------------------------------------------------------
# Caminho padrão para o golden_set
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_SET_PATH = _PROJECT_ROOT / "data" / "eval" / "golden_set.json"

# k's de avaliação
EVAL_K_VALUES = [3, 5, 10]


def load_golden_set(path: str | Path = GOLDEN_SET_PATH) -> list[dict[str, Any]]:
    """
    Carrega o golden_set.json com as perguntas de avaliação.

    Parâmetros
    ----------
    path : str | Path
        Caminho para o arquivo golden_set.json.

    Retorna
    -------
    list[dict]
        Lista de perguntas com ``id``, ``pergunta``, ``categoria``,
        ``evidencia_esperada`` e ``comentario``.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Golden set não encontrado: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    print(f"[evaluator] Golden set carregado: {len(data)} perguntas.")
    return data


def _extract_doc_id(evidencia: str) -> str:
    """
    Extrai o doc_id de uma string de evidência.

    Exemplos
    --------
    - ``"NBR6120#Tabela_X"``  →  ``"NBR6120"``
    - ``"NBR6118#13.2.4"``    →  ``"NBR6118"``
    - ``"NBR6123#Fatores"``   →  ``"NBR6123"``
    """
    return evidencia.split("#")[0]


def _is_hit(results: list[dict[str, Any]], evidencias: list[str]) -> bool:
    """
    Verifica se algum resultado recuperado corresponde a alguma evidência.

    Correspondência baseada em ``doc_id`` (ver docstring do módulo).

    Parâmetros
    ----------
    results : list[dict]
        Resultados do retriever (com chave ``doc_id``).
    evidencias : list[str]
        Lista de evidências esperadas (strings no formato ``"NBRxxxx#..."``)

    Retorna
    -------
    bool
        True se pelo menos um resultado corresponde a pelo menos uma evidência.
    """
    retrieved_doc_ids = {r["doc_id"] for r in results}
    expected_doc_ids = {_extract_doc_id(e) for e in evidencias}
    return bool(retrieved_doc_ids & expected_doc_ids)


def run_evaluation(
    retrieve_fn: Any,
    golden_set: list[dict[str, Any]] | None = None,
    k_values: list[int] = EVAL_K_VALUES,
    golden_set_path: str | Path = GOLDEN_SET_PATH,
) -> dict[str, Any]:
    """
    Executa a avaliação Recall@k completa.

    Parâmetros
    ----------
    retrieve_fn : callable
        Função de retrieval com assinatura ``retrieve_fn(query: str, k: int)``
        retornando lista de dicts com ao menos ``chunk_id`` e ``doc_id``.
    golden_set : list[dict] | None
        Dados do golden set. Se None, carrega de ``golden_set_path``.
    k_values : list[int]
        Lista de valores de k para avaliação (padrão: [3, 5, 10]).
    golden_set_path : str | Path
        Caminho para o golden_set.json (usado se ``golden_set`` é None).

    Retorna
    -------
    dict
        Dicionário com:
        - ``recall_at_k``    : dict {k: float} com recall para cada k
        - ``n_questions``    : int — total de perguntas avaliadas (excl. fora_corpus)
        - ``n_out_of_scope`` : int — perguntas fora_do_corpus (excluídas)
        - ``details_df``     : pd.DataFrame com detalhes por pergunta
        - ``summary_df``     : pd.DataFrame resumo de Recall@k
    """
    if golden_set is None:
        golden_set = load_golden_set(golden_set_path)

    # Separa perguntas avaliáveis das fora do corpus
    evaluable = [q for q in golden_set if q["evidencia_esperada"] is not None]
    out_of_scope = [q for q in golden_set if q["evidencia_esperada"] is None]

    print(f"[evaluator] Perguntas avaliáveis: {len(evaluable)}")
    print(f"[evaluator] Perguntas fora do corpus (excluídas): {len(out_of_scope)}")

    # --- Executa retrieval e calcula hits por pergunta ---
    rows = []
    max_k = max(k_values)

    for q in evaluable:
        # Normaliza evidência para lista
        ev_raw = q["evidencia_esperada"]
        evidencias = ev_raw if isinstance(ev_raw, list) else [ev_raw]

        # Recupera top-max_k uma única vez por eficiência
        results = retrieve_fn(q["pergunta"], k=max_k)

        hits = {}
        for k in k_values:
            top_k_results = results[:k]
            hits[k] = _is_hit(top_k_results, evidencias)

        row = {
            "id": q["id"],
            "categoria": q["categoria"],
            "pergunta": q["pergunta"][:80] + "...",
            "evidencias": ", ".join(evidencias),
        }
        for k in k_values:
            row[f"hit@{k}"] = hits[k]
            row[f"retrieved_docs@{k}"] = ", ".join(
                {r["doc_id"] for r in results[:k]}
            )
        rows.append(row)

    details_df = pd.DataFrame(rows)

    # --- Calcula Recall@k ---
    recall_at_k = {}
    summary_rows = []

    for k in k_values:
        hits_total = details_df[f"hit@{k}"].sum()
        recall = hits_total / len(evaluable)
        recall_at_k[k] = recall
        summary_rows.append({
            "k": k,
            "hits": int(hits_total),
            "total": len(evaluable),
            "recall@k": round(recall, 4),
        })

    summary_df = pd.DataFrame(summary_rows)

    return {
        "recall_at_k": recall_at_k,
        "n_questions": len(evaluable),
        "n_out_of_scope": len(out_of_scope),
        "details_df": details_df,
        "summary_df": summary_df,
    }


def print_evaluation_report(eval_results: dict[str, Any]) -> None:
    """
    Exibe um relatório formatado dos resultados de avaliação.

    Parâmetros
    ----------
    eval_results : dict
        Resultado retornado por ``run_evaluation()``.
    """
    print(f"\n{'='*70}")
    print("  RELATÓRIO DE AVALIAÇÃO — RECALL@K (RETRIEVER BASELINE)")
    print(f"{'='*70}")
    print(f"  Perguntas avaliadas    : {eval_results['n_questions']}")
    print(f"  Fora do corpus (excl.) : {eval_results['n_out_of_scope']}")
    print()

    summary = eval_results["summary_df"]
    print(summary.to_string(index=False))

    print(f"\n{'='*70}")
    print("  DETALHAMENTO POR PERGUNTA")
    print(f"{'='*70}")

    detail_cols = (
        ["id", "categoria", "evidencias"]
        + [c for c in eval_results["details_df"].columns if c.startswith("hit@")]
    )
    print(eval_results["details_df"][detail_cols].to_string(index=False))
    print(f"{'='*70}\n")


def save_evaluation_report(
    eval_results: dict[str, Any],
    output_path: str | Path | None = None,
) -> Path:
    """
    Salva o relatório de avaliação em CSV e JSON.

    Parâmetros
    ----------
    eval_results : dict
        Resultado retornado por ``run_evaluation()``.
    output_path : str | Path | None
        Diretório de destino. Se None, usa ``index/`` da raiz do projeto.

    Retorna
    -------
    Path
        Caminho do diretório onde os arquivos foram salvos.
    """
    if output_path is None:
        output_path = _PROJECT_ROOT / "index"

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Salva tabela de detalhes
    details_path = output_path / "eval_details.csv"
    eval_results["details_df"].to_csv(details_path, index=False, encoding="utf-8")

    # Salva resumo
    summary_path = output_path / "eval_summary.csv"
    eval_results["summary_df"].to_csv(summary_path, index=False, encoding="utf-8")

    # Salva recall por JSON
    recall_path = output_path / "recall_at_k.json"
    with open(recall_path, "w", encoding="utf-8") as f:
        json.dump(
            {f"recall@{k}": v for k, v in eval_results["recall_at_k"].items()},
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"[evaluator] Relatório salvo em: {output_path}")
    print(f"  - {details_path.name}")
    print(f"  - {summary_path.name}")
    print(f"  - {recall_path.name}")

    return output_path


def run_comparative_evaluation(
    faiss_retrieve_fn,
    sparse_retrieve_fn,
    hybrid_retrieve_fn,
    golden_set: list[dict] | None = None,
    k_values: list[int] = EVAL_K_VALUES,
    golden_set_path: str | Path = GOLDEN_SET_PATH,
) -> dict:
    """
    Executa avaliação comparativa Recall@k para os 3 modos de retrieval:
    dense (FAISS), sparse (BM25) e hybrid (BM25+FAISS+RRF).

    Retorna
    -------
    dict com:
    - ``modes``       : dict {mode_name: resultado de run_evaluation()}
    - ``comparison``  : pd.DataFrame com recall@k lado a lado
    """
    if golden_set is None:
        golden_set = load_golden_set(golden_set_path)

    modes = {
        "dense":  run_evaluation(faiss_retrieve_fn,   golden_set, k_values),
        "sparse": run_evaluation(sparse_retrieve_fn,  golden_set, k_values),
        "hybrid": run_evaluation(hybrid_retrieve_fn,  golden_set, k_values),
    }

    # Tabela comparativa
    rows = []
    for k in k_values:
        row = {"k": k}
        for mode_name, res in modes.items():
            row[f"recall@{k}_{mode_name}"] = round(res["recall_at_k"][k], 4)
        rows.append(row)

    comparison_df = pd.DataFrame(rows)

    return {"modes": modes, "comparison": comparison_df}


def print_comparative_report(comp_results: dict) -> None:
    """Exibe relatório comparativo dos 3 modos."""
    print(f"\n{'='*70}")
    print("  AVALIAÇÃO COMPARATIVA — RECALL@K (dense vs sparse vs hybrid)")
    print(f"{'='*70}")
    print(comp_results["comparison"].to_string(index=False))
    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Execução direta: avalia o retriever com o golden_set
    from src.indexer import load_index, retrieve as _retrieve

    idx, chks, mdl = load_index()

    def retrieve_fn(query: str, k: int) -> list[dict]:
        return _retrieve(query, idx, chks, mdl, k=k)

    gs = load_golden_set()
    results = run_evaluation(retrieve_fn, gs)
    print_evaluation_report(results)
    save_evaluation_report(results)
