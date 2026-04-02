# RAG — Normas Estruturais ABNT

Chatbot técnico baseado em **RAG (Retrieval-Augmented Generation)** para consulta às normas brasileiras de engenharia estrutural, com citações rastreáveis e avaliação experimental.

**Grupo:** Eduardo Braga · Israel Magalhães · Marcelo Carvalho
**Disciplina:** Processamento de Linguagem Natural — IFG Pós-IA

---

## Corpus

| Norma                           | Conteúdo                                           | Seções |
| ------------------------------- | -------------------------------------------------- | ------ |
| **NBR 6120:1980** (Errata 2000) | Cargas para o cálculo de estruturas de edificações | 13     |
| **NBR 6123:2023**               | Forças devidas ao vento em edificações             | 166    |

**Total:** 179 seções · ~331 k caracteres

A granularidade de segmentação é **1 seção = 1 chunk**. Cada chunk carrega `chunk_id`, `doc_id`, `titulo`, `fonte`, `edicao`, `secao` e `summary`.

---

## Trilha implementada: A — Recuperação Híbrida (Sparse + Dense)

Três modos de retrieval disponíveis:

| Modo     | Tecnologia                   | Descrição                               |
| -------- | ---------------------------- | --------------------------------------- |
| `dense`  | BERTimbau + FAISS (baseline) | Busca semântica por cosseno             |
| `sparse` | BM25Okapi                    | Busca léxica por termos exatos          |
| `hybrid` | BM25 + FAISS via RRF         | Fusão Reciprocal Rank Fusion (k_RRF=60) |

---

## Pré-requisitos

- Python 3.10+
- ~2 GB de espaço em disco (modelo BERTimbau + índice FAISS)
- Chave de API Groq (gratuita em [console.groq.com](https://console.groq.com))

---

## Instalação e configuração

### 1. Clone o repositório

```bash
git clone <url-do-repo>
cd pln-rag-normas-estruturais
```

### 2. Crie e ative o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as chaves de API

```bash
cp .env.example .env
```

Edite `.env`:

```env
GROQ_API_KEY=sua_chave_groq_aqui        # provider padrão (recomendado)
GEMINI_API_KEY=sua_chave_gemini_aqui    # opcional (fallback)
```

---

## Executando o pipeline completo

### Passo 0 — Opcional — Converter PDFs para Markdown (uma vez)

```bash
python scripts/convert_pdfs.py
```

Gera `data/norms/md/NBR6120_2019.md` e `data/norms/md/NBR6123_2023.md`.

> Os arquivos .md já estão versionados no repositório. Execute este passo apenas se substituir os PDFs originais.

### Passo 1 — Opcional — Dividir Markdown em seções (uma vez)

```bash
python scripts/split_sections_auto.py
```

Gera os arquivos de seção em `data/norms/sections/nbr6120/` e `data/norms/sections/nbr6123/`.

> As seções de ambas as normas são geradas automaticamente pelo script a partir dos PDFs convertidos para Markdown.

### Passo 2 — Abrir o notebook principal

```bash
jupyter notebook notebooks/rag_normas.ipynb
```

Execute as células em ordem:

| Seção | O que faz                                           |
| ----- | --------------------------------------------------- |
| 0     | Configura ambiente e variáveis                      |
| 1     | Carrega as 179 seções normativas                    |
| 2     | Gera chunks (1 por seção)                           |
| 3     | Carrega BERTimbau e constrói índice FAISS           |
| 4     | Testa retriever denso                               |
| 5     | Inicializa pipeline RAG (Groq) e testa perguntas    |
| 6     | Cria e testa retriever esparso (BM25)               |
| 7     | Cria e testa retriever híbrido (BM25 + FAISS + RRF) |
| 8     | Avaliação Recall@k — dense vs sparse vs hybrid      |
| 9     | Análise de trade-offs                               |
| 10    | Interface Gradio interativa                         |

---

## Google Colab

```python
# Célula 0.1 — instala dependências
!pip install -q sentence-transformers faiss-cpu rank-bm25 groq google-generativeai \
    python-dotenv tqdm pandas openai gradio

# Monte o Drive e aponte PROJECT_ROOT para a pasta do projeto
```

Na célula Gradio, troque `demo.launch()` por `demo.launch(share=True)` para URL pública.

---

## Avaliação

### Recall@k (automático)

Execute a Seção 8 do notebook. Calcula Recall@k (k=3, 5, 10) para os 3 modos de retrieval usando o golden set em `data/eval/golden_set.json`.

### Rubrica qualitativa (manual)

Gere as respostas para avaliação manual:

```bash
python scripts/gerar_rubrica.py
```

Preencha os scores em `data/eval/rubrica_scores.json` seguindo o template gerado em `data/eval/rubrica_respostas.json`.

**Critérios por resposta:**

| Critério     | Descrição                                  | Escala            |
| ------------ | ------------------------------------------ | ----------------- |
| Groundedness | Resposta suportada pelos trechos?          | 0–2               |
| Correção     | Resposta correta conforme as normas?       | 0–2               |
| Citações     | Cita trechos adequados?                    | 0–2               |
| Alucinação   | Inventou algo fora do corpus?              | 0=sim, 1=não      |
| Recusa       | Recusou corretamente quando sem evidência? | 0=não, 1=sim, N/A |

---

## Estrutura do projeto

```
pln-rag-normas-estruturais/
├── data/
│   ├── norms/
│   │   ├── NBR6120_2019.pdf          # norma original
│   │   ├── NBR6123_2023.pdf
│   │   ├── md/                        # markdown gerado pelo Docling
│   │   └── sections/                  # seções por norma
│   │       ├── nbr6120/               # 13 seções (manual)
│   │       └── nbr6123/               # 166 seções (auto)
│   └── eval/
│       ├── golden_set.json            # 21 perguntas de avaliação
│       └── rubrica_respostas.json     # respostas geradas (após gerar_rubrica.py)
├── index/                             # índice FAISS salvo (gerado pelo notebook)
├── notebooks/
│   └── rag_normas.ipynb              # notebook principal
├── scripts/
│   ├── convert_pdfs.py               # PDF → Markdown (Docling)
│   ├── split_sections_auto.py        # Markdown → seções
│   └── gerar_rubrica.py              # gera respostas para avaliação manual
├── src/
│   ├── ingestion.py                  # carrega seções com metadados
│   ├── chunker.py                    # gera chunks com metadados
│   ├── indexer.py                    # BERTimbau + FAISS
│   ├── hybrid_search.py              # BM25 + RRF (Trilha A)
│   ├── rag_pipeline.py               # pipeline completo RAG
│   ├── prompts.py                    # templates de prompt (grounding)
│   └── evaluator.py                  # Recall@k + rubrica
├── .env.example
├── requirements.txt
└── README.md
```

---

## Tecnologias

| Componente      | Tecnologia                                                   |
| --------------- | ------------------------------------------------------------ |
| Extração de PDF | Docling                                                      |
| Embeddings      | `neuralmind/bert-base-portuguese-cased` (BERTimbau, dim=768) |
| Índice vetorial | FAISS `IndexFlatIP` (cosseno exato)                          |
| Busca léxica    | BM25Okapi (`rank-bm25`)                                      |
| Fusão híbrida   | Reciprocal Rank Fusion (k_RRF=60)                            |
| LLM (geração)   | Groq (llama-3.3-70b) / Google Gemini / NVIDIA NIM            |
| Interface       | Gradio                                                       |
