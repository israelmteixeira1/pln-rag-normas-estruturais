"""
src/prompts.py
==============
Templates de prompt para o pipeline RAG de normas estruturais.

Estratégia de Grounding
------------------------
O prompt instrui o LLM a responder EXCLUSIVAMENTE com base nos trechos
normativos recuperados pelo retriever, citando as fontes no formato
``[NBRxxxx#seção]``. Isso garante rastreabilidade técnica e evita
alucinações sobre conteúdo normativo.

Modos
-----
- baseline  : prompt direto com instrução de grounding e citações
- improved  : prompt com chain-of-thought, verificação cruzada entre
              normas e formato de resposta estruturado (Fase 5)
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Prompts do sistema
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_BASELINE = """\
Você é um assistente técnico especializado em normas brasileiras de \
engenharia estrutural (ABNT).

REGRAS OBRIGATÓRIAS:
1. Responda APENAS com base nos trechos normativos fornecidos abaixo.
2. Cite as fontes ao longo da resposta usando o formato [NBRxxxx#seção], \
por exemplo: [NBR6118#13.2.4].
3. Se a informação solicitada NÃO estiver nos trechos fornecidos, responda \
exatamente: "Não encontrei informação suficiente nas normas consultadas \
para responder esta pergunta."
4. NÃO invente, extrapole ou use conhecimento externo às normas.
5. Se a pergunta for sobre preços, orçamentos, marcas comerciais ou \
qualquer tema NÃO normativo, recuse educadamente explicando que o sistema \
consulta apenas normas técnicas ABNT.
6. Preserve valores numéricos, unidades e condições exatamente como \
aparecem nos trechos.
"""

SYSTEM_PROMPT_IMPROVED = """\
Você é um assistente técnico especializado em normas brasileiras de \
engenharia estrutural (ABNT).

INSTRUÇÕES DE RACIOCÍNIO:
Antes de responder, siga estas etapas mentalmente:
1. IDENTIFIQUE quais trechos normativos são relevantes para a pergunta.
2. VERIFIQUE se há informação suficiente nos trechos para uma resposta \
fundamentada.
3. Se múltiplas normas abordam o tema, CRUZE as referências para uma \
resposta integrada.
4. CONFIRME que cada afirmação na sua resposta é suportada por pelo menos \
um trecho fornecido.

REGRAS OBRIGATÓRIAS:
1. Responda APENAS com base nos trechos normativos fornecidos abaixo.
2. Cite as fontes ao longo da resposta usando o formato [NBRxxxx#seção], \
por exemplo: [NBR6118#13.2.4].
3. Se a informação solicitada NÃO estiver nos trechos fornecidos, responda \
exatamente: "Não encontrei informação suficiente nas normas consultadas \
para responder esta pergunta."
4. NÃO invente, extrapole ou use conhecimento externo às normas.
5. Se a pergunta for sobre preços, orçamentos, marcas comerciais ou \
qualquer tema NÃO normativo, recuse educadamente explicando que o sistema \
consulta apenas normas técnicas ABNT.
6. Preserve valores numéricos, unidades e condições exatamente como \
aparecem nos trechos.

FORMATO DE RESPOSTA:
- Comece com uma resposta objetiva e direta.
- Em seguida, detalhe com base nos trechos normativos, citando cada fonte.
- Se houver valores em tabelas, apresente-os de forma organizada.
- Finalize com a lista de referências normativas consultadas.
"""


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------


def format_context(results: list[dict[str, Any]]) -> str:
    """
    Formata os chunks recuperados como bloco de contexto para o prompt.

    Cada chunk é apresentado com um cabeçalho contendo o chunk_id, doc_id,
    seção e score de relevância, seguido do texto normativo.

    Parâmetros
    ----------
    results : list[dict]
        Resultados do retriever (retorno de ``indexer.retrieve()``).

    Retorna
    -------
    str
        Contexto formatado, pronto para inserção no prompt.
    """
    parts: list[str] = []
    for r in results:
        header = (
            f"[Fonte: {r['chunk_id']} | "
            f"{r['doc_id']} — Seção {r['secao']} | "
            f"Relevância: {r['score']:.3f}]"
        )
        parts.append(f"{header}\n{r['texto']}")
    return "\n\n---\n\n".join(parts)


def build_prompt(
    question: str,
    context: str,
    mode: str = "baseline",
) -> str:
    """
    Monta o prompt completo para envio ao LLM.

    Parâmetros
    ----------
    question : str
        Pergunta do usuário em linguagem natural.
    context : str
        Contexto formatado com os trechos normativos recuperados
        (retorno de ``format_context()``).
    mode : str
        ``'baseline'`` ou ``'improved'``.

    Retorna
    -------
    str
        Prompt completo pronto para envio ao LLM.
    """
    system = (
        SYSTEM_PROMPT_BASELINE if mode == "baseline"
        else SYSTEM_PROMPT_IMPROVED
    )

    return (
        f"{system}\n"
        f"TRECHOS NORMATIVOS RECUPERADOS:\n"
        f"{context}\n\n"
        f"PERGUNTA DO USUÁRIO:\n{question}\n\n"
        f"RESPOSTA:"
    )
