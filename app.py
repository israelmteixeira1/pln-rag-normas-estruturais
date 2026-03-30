"""
app.py
======
Interface Streamlit para o chatbot RAG de normas estruturais.

Executar com:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
import threading
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Armazenamento thread-safe para resultado da consulta em background
# (evita escrita em st.session_state fora da thread principal)
# ---------------------------------------------------------------------------
_query_store: dict = {"result": None, "cancelled": False}

# ---------------------------------------------------------------------------
# Configuração da página (DEVE ser a primeira chamada Streamlit)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="RAG — Normas Estruturais",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS customizado
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Tipografia */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
        padding: 1.8rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    .main-header h1 {
        color: #e2e8f0;
        font-size: 1.8rem;
        margin: 0;
        font-weight: 700;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
    }

    /* Cards de fonte */
    .source-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        backdrop-filter: blur(4px);
    }
    .source-header {
        color: #60a5fa;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.4rem;
    }
    .source-text {
        color: #cbd5e1;
        font-size: 0.82rem;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    .score-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
    }

    /* Métricas de latência */
    .latency-bar {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 6px;
        padding: 0.6rem 1rem;
        margin-top: 0.8rem;
        border: 1px solid rgba(59, 130, 246, 0.1);
        font-size: 0.8rem;
        color: #94a3b8;
    }

    /* Botões de demo */
    .stButton > button {
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        border-color: #3b82f6 !important;
        background: rgba(59, 130, 246, 0.1) !important;
    }

    /* Separador */
    .separator {
        border-top: 1px solid rgba(59, 130, 246, 0.1);
        margin: 1.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Verificação do índice FAISS
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent
INDEX_DIR = _PROJECT_ROOT / "index"


def _index_exists() -> bool:
    """Verifica se o índice FAISS já foi construído."""
    return (INDEX_DIR / "faiss.index").exists() and (
        INDEX_DIR / "chunks_metadata.json"
    ).exists()


# ---------------------------------------------------------------------------
# Carregamento do pipeline (cacheado — carrega apenas uma vez)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_pipeline():
    """Carrega o pipeline RAG (índice FAISS + modelo de embedding + Gemini)."""
    from src.rag_pipeline import RAGPipeline
    return RAGPipeline()


@st.cache_resource(show_spinner=False)
def load_hybrid_retriever():
    """Carrega o HybridRetriever (BM25+FAISS) cacheado."""
    from src.hybrid_search import HybridRetriever
    from src.indexer import load_index
    index, chunks, embed_model = load_index()
    return HybridRetriever(chunks, index, embed_model)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>🏗️ RAG — Normas Estruturais ABNT</h1>
        <p>Chatbot técnico com citações normativas rastreáveis
        &nbsp;·&nbsp; NBR 6118 &nbsp;·&nbsp; NBR 6120 &nbsp;·&nbsp; NBR 6123</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Verificação se o índice existe
# ---------------------------------------------------------------------------
if not _index_exists():
    st.error(
        "⚠️ **Índice FAISS não encontrado.**\n\n"
        "Execute as seções 0–3 do notebook `notebooks/rag_normas.ipynb` "
        "para construir o índice."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar — Controles
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configurações")

    mode = st.radio(
        "Modo do prompt",
        options=["baseline", "improved", "hybrid"],
        index=0,
        help=(
            "**Baseline**: prompt direto com grounding (retriever FAISS).\n\n"
            "**Improved**: prompt com chain-of-thought e "
            "verificação cruzada entre normas (retriever FAISS).\n\n"
            "**Hybrid**: BM25+FAISS com Reciprocal Rank Fusion "
            "(prompt improved)."
        ),
    )

    k = st.select_slider(
        "Top-k (chunks recuperados)",
        options=[3, 5, 10],
        value=5,
        help="Número de trechos normativos recuperados para cada consulta.",
    )

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    st.markdown("### 📋 Perguntas de demonstração")
    st.caption("Clique para testar:")

    demo_questions = [
        "Qual o valor de carga acidental para um pavimento de escritório?",
        "Quais fatores influenciam a velocidade de cálculo do vento?",
        "Qual a diferença entre estados-limite últimos e de serviço?",
        "Como considerar paredes divisórias sem posição definida?",
        "Como calcular o preço do m³ de concreto?",
    ]

    def _set_demo(q: str):
        st.session_state["question_box"] = q

    for dq in demo_questions:
        st.button(
            dq, key=f"demo_{dq[:30]}", use_container_width=True,
            on_click=_set_demo, args=(dq,),
        )

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    st.markdown("### ℹ️ Sobre")
    st.caption(
        "Projeto acadêmico — IFG Pós-IA / PLN.\n\n"
        "**Trilha I** (Israel): Ingestão, chunking, indexação.\n\n"
        "**Trilha E** (Eduardo): Pipeline RAG e interface.\n\n"
        "**Trilha M** (Marcelo): Avaliação e relatório.\n\n"
        "---\n"
        "Modelo de embedding: `bert-base-portuguese-cased`\n\n"
        "Índice: FAISS (cosseno)\n\n"
        "LLM: Google Gemini Flash"
    )

# ---------------------------------------------------------------------------
# Carrega pipeline
# ---------------------------------------------------------------------------
with st.spinner("🔄 Carregando pipeline RAG (primeira vez pode demorar)..."):
    pipeline = load_pipeline()

# ---------------------------------------------------------------------------
# Área principal — Entrada de pergunta
# ---------------------------------------------------------------------------
question = st.text_area(
    "💬 Faça sua pergunta técnica sobre normas estruturais:",
    height=80,
    placeholder="Ex.: Qual o valor de carga acidental para um pavimento de escritório?",
    key="question_box",
)

running = st.session_state.get("running", False)

def _clear():
    st.session_state["question_box"] = ""
    st.session_state["last_result"] = None

col_submit, col_cancel, col_clear = st.columns([1, 1, 4])
with col_submit:
    submit = st.button("🔍 Consultar", type="primary", use_container_width=True, disabled=running)
with col_cancel:
    cancel = st.button("❌ Cancelar", use_container_width=True, disabled=not running)
with col_clear:
    st.button("🗑️ Limpar", on_click=_clear, disabled=running)

# ---------------------------------------------------------------------------
# Cancelar consulta em andamento
# ---------------------------------------------------------------------------
if cancel and running:
    _query_store["cancelled"] = True
    st.session_state["running"] = False
    st.rerun()

# ---------------------------------------------------------------------------
# Inicia consulta em thread separada
# ---------------------------------------------------------------------------
if submit and question.strip():
    _q = question.strip()
    _k, _mode = k, mode
    _retriever = load_hybrid_retriever() if mode == "hybrid" else None
    _query_store["result"] = None
    _query_store["cancelled"] = False
    st.session_state["running"] = True

    def _run_query():
        try:
            res = pipeline.query(_q, k=_k, mode=_mode, retriever=_retriever)
        except Exception as e:
            res = {
                "answer": f"⚠️ Erro na consulta: {e}",
                "sources": [], "mode": _mode, "k": _k,
                "latency": {"retrieval_s": 0, "generation_s": 0, "total_s": 0},
            }
        if not _query_store["cancelled"]:
            _query_store["result"] = res

    threading.Thread(target=_run_query, daemon=True).start()
    st.rerun()

# ---------------------------------------------------------------------------
# Polling enquanto consulta roda
# ---------------------------------------------------------------------------
if st.session_state.get("running"):
    if _query_store["result"] is not None:
        st.session_state["last_result"] = _query_store["result"]
        _query_store["result"] = None
        st.session_state["running"] = False
        st.rerun()
    else:
        with st.spinner("Consultando normas..."):
            time.sleep(0.3)
        st.rerun()

# ---------------------------------------------------------------------------
# Exibe resultado
# ---------------------------------------------------------------------------
result = st.session_state.get("last_result")

if result:
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    # --- Resposta ---
    st.markdown("### 📝 Resposta")
    st.markdown(result["answer"])

    # --- Latência ---
    lat = result["latency"]
    st.markdown(
        f'<div class="latency-bar">'
        f'⏱️ Retrieval: <b>{lat["retrieval_s"]:.2f}s</b> &nbsp;|&nbsp; '
        f'Geração: <b>{lat["generation_s"]:.2f}s</b> &nbsp;|&nbsp; '
        f'Total: <b>{lat["total_s"]:.2f}s</b> &nbsp;|&nbsp; '
        f'Modo: <b>{result["mode"]}</b> &nbsp;|&nbsp; '
        f'Top-k: <b>{result["k"]}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # --- Trechos recuperados ---
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    with st.expander(
        f"📄 Trechos normativos recuperados ({len(result['sources'])} chunks)",
        expanded=False,
    ):
        for src in result["sources"]:
            preview = src["texto"][:500]
            if len(src["texto"]) > 500:
                preview += "..."

            st.markdown(
                f'<div class="source-card">'
                f'<div class="source-header">'
                f'#{src["rank"]} &nbsp; {src["chunk_id"]} &nbsp; '
                f'<span class="score-badge">score: {src["score"]:.3f}</span>'
                f'</div>'
                f'<div class="source-text">{preview}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
