"""
src/rag_pipeline.py
===================
Pipeline RAG (Retrieval-Augmented Generation) para normas estruturais.

Fluxo
-----
1. Recebe pergunta do usuário
2. Recupera top-k chunks mais relevantes via retriever FAISS
3. Monta prompt com grounding explícito (trechos normativos como contexto)
4. Envia ao LLM (Google Gemini) para geração de resposta
5. Retorna resposta com citações normativas + metadados de latência

Pré-requisitos
--------------
- Índice FAISS construído (execute build_index() e save_index())
- API key do Google Gemini em ``.env`` ou variável de ambiente ``GEMINI_API_KEY``
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from google import genai
from dotenv import load_dotenv

from src.indexer import load_index, retrieve
from src.prompts import build_prompt, format_context

# ---------------------------------------------------------------------------
# Carrega variáveis de ambiente do .env (raiz do projeto)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Configurações padrão
# ---------------------------------------------------------------------------
GEMINI_MODEL = "gemini-2.0-flash"


class RAGPipeline:
    """
    Pipeline RAG completo para consulta de normas estruturais.

    Conecta o retriever FAISS (construído na Trilha I) ao Google Gemini,
    com prompts de grounding que forçam respostas baseadas exclusivamente
    nos trechos normativos recuperados.

    Attributes
    ----------
    index : faiss.Index
        Índice FAISS carregado do disco.
    chunks : list[dict]
        Metadados dos chunks indexados.
    embed_model : SentenceTransformer
        Modelo de embedding para codificar queries.
    llm_model : genai.GenerativeModel
        Modelo Google Gemini para geração de respostas.
    mode : str
        Modo padrão do pipeline: ``'baseline'`` ou ``'improved'``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        gemini_model: str = GEMINI_MODEL,
        mode: str = "baseline",
        index_dir: str | Path | None = None,
    ):
        """
        Inicializa o pipeline RAG.

        Parâmetros
        ----------
        api_key : str | None
            API key do Google Gemini. Se None, usa ``GEMINI_API_KEY`` do
            ambiente / ``.env``.
        gemini_model : str
            Nome do modelo Gemini (padrão: ``gemini-2.0-flash``).
        mode : str
            Modo padrão: ``'baseline'`` ou ``'improved'``.
        index_dir : str | Path | None
            Diretório do índice FAISS. Se None, usa o padrão (``index/``).

        Raises
        ------
        ValueError
            Se nenhuma API key for encontrada.
        FileNotFoundError
            Se o índice FAISS não existir (execute build_index() e save_index()).
        """
        # --- Configura Google Gemini ---
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError(
                "API key do Gemini não encontrada. "
                "Configure GEMINI_API_KEY no arquivo .env ou passe api_key=."
            )
        self.llm_client = genai.Client(api_key=key)
        self._gemini_model = gemini_model
        self.mode = mode

        # --- Carrega índice FAISS + modelo de embedding ---
        print(f"[rag] Inicializando pipeline RAG (modo={mode})...")
        if index_dir:
            self.index, self.chunks, self.embed_model = load_index(index_dir)
        else:
            self.index, self.chunks, self.embed_model = load_index()

        print(f"[rag] Pipeline pronto. {self.index.ntotal} chunks indexados.")

    def query(
        self,
        question: str,
        k: int = 5,
        mode: str | None = None,
        retriever=None,
    ) -> dict[str, Any]:
        """
        Executa uma consulta RAG completa.

        Parâmetros
        ----------
        question : str
            Pergunta do usuário em linguagem natural.
        k : int
            Número de chunks a recuperar (recomendado: 3, 5 ou 10).
        mode : str | None
            Modo do prompt para esta consulta. Se None, usa ``self.mode``.
        retriever : object | None
            Retriever alternativo com método retrieve(query, k). Se None, usa FAISS.

        Retorna
        -------
        dict
            Dicionário com:
            - ``answer``  : str — resposta gerada pelo LLM
            - ``sources`` : list[dict] — chunks recuperados com metadados
            - ``mode``    : str — modo usado ('baseline' ou 'improved')
            - ``k``       : int — top-k usado
            - ``latency`` : dict — tempos em segundos (retrieval, generation, total)
        """
        current_mode = mode or self.mode

        # 1. Retrieval — busca os chunks mais relevantes
        t0 = time.time()
        if retriever is not None:
            results = retriever.retrieve(question, k=k)
        else:
            results = retrieve(
                query=question,
                index=self.index,
                chunks=self.chunks,
                model=self.embed_model,
                k=k,
            )
        t_retrieval = time.time() - t0

        # 2. Montagem do prompt com contexto normativo
        context = format_context(results)
        prompt = build_prompt(question, context, mode=current_mode)

        # 3. Geração de resposta via Google Gemini (com retry para rate limits)
        t1 = time.time()
        answer = ""
        max_retries = 3
        retry_delays = [10, 30, 60]  # segundos entre tentativas

        for attempt in range(max_retries + 1):
            try:
                response = self.llm_client.models.generate_content(
                    model=self._gemini_model,
                    contents=prompt,
                )
                answer = response.text
                break  # sucesso — sai do loop
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg and attempt < max_retries:
                    wait = retry_delays[attempt]
                    print(
                        f"[rag] Rate limit atingido. "
                        f"Tentativa {attempt + 1}/{max_retries}. "
                        f"Aguardando {wait}s..."
                    )
                    time.sleep(wait)
                else:
                    answer = (
                        f"⚠️ Erro na geração de resposta: {e}\n\n"
                        "Verifique sua API key e conexão com a internet."
                    )
                    break
        t_generation = time.time() - t1

        return {
            "answer": answer,
            "sources": results,
            "mode": current_mode,
            "k": k,
            "latency": {
                "retrieval_s": round(t_retrieval, 3),
                "generation_s": round(t_generation, 3),
                "total_s": round(t_retrieval + t_generation, 3),
            },
        }


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_pipeline(**kwargs: Any) -> RAGPipeline:
    """Atalho para criar uma instância do pipeline RAG."""
    return RAGPipeline(**kwargs)


# ---------------------------------------------------------------------------
# Teste direto
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pipe = RAGPipeline()

    test_questions = [
        "Qual o valor típico de carga acidental para um pavimento de escritório?",
        "Como calcular o preço do m³ de concreto para uma obra em Brasília?",
    ]

    for q in test_questions:
        print(f"\n{'='*70}")
        print(f"  Pergunta: {q}")
        print(f"{'='*70}")
        result = pipe.query(q, k=5)
        print(f"\nResposta ({result['mode']}):\n{result['answer']}")
        print(f"\nLatência: {result['latency']}")
        print(f"\nChunks recuperados:")
        for s in result["sources"]:
            print(f"  #{s['rank']} {s['chunk_id']} (score={s['score']:.3f})")
