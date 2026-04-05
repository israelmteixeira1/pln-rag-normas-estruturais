# RAG — Normas Estruturais ABNT

Chatbot técnico baseado em **RAG (Retrieval-Augmented Generation)** para consulta às normas brasileiras de engenharia estrutural, com citações rastreáveis e avaliação experimental.

**Grupo:** Eduardo Braga, Israel Magalhães e Marcelo Carvalho

**Disciplina:** Processamento de Linguagem Natural — IFG Pós-IA

---

## Corpus

| Norma             | Conteúdo                                           | Seções |
| ----------------- | -------------------------------------------------- | ------ |
| **NBR 6120:2019** | Cargas para o cálculo de estruturas de edificações | 13     |
| **NBR 6123:2023** | Forças devidas ao vento em edificações             | 166    |

**Total:** 179 seções · ~331 k caracteres

### Metadados por chunk

| Campo      | Descrição                                    |
| ---------- | -------------------------------------------- |
| `chunk_id` | Identificador único (ex.: `NBR6120_secao_3`) |
| `doc_id`   | Documento de origem (`NBR6120` ou `NBR6123`) |
| `titulo`   | Título da norma completa                     |
| `fonte`    | Origem (`ABNT`)                              |
| `edicao`   | Edição/data da norma (ex.: `2019`)           |
| `secao`    | Número da seção normativa                    |
| `summary`  | Resumo gerado na segmentação                 |

### Estratégia de chunking

**Granularidade:** 1 seção normativa = 1 chunk — sem subdivisão adicional.

**Justificativa:** as seções das normas ABNT são unidades semânticas autocontidas — cada uma trata de um tema específico (ex.: cargas de vento por categoria de terreno). Subdividir introduziria fragmentação sem ganho de recall no domínio técnico-normativo.

**Detalhes:**

| Parâmetro          | Valor                                                          |
| ------------------ | -------------------------------------------------------------- |
| Tamanho médio      | ~1.850 chars/chunk (variável por seção)                        |
| Overlap            | Não aplicado (seções são semanticamente independentes)         |
| Títulos/cabeçalhos | Preservados como Markdown (`##`, `###`)                        |
| Tabelas            | Preservadas em Markdown (ex.: tabelas de coeficientes NBR6123) |
| Listas e fórmulas  | Preservadas como texto bruto                                   |

---

## Trilha implementada: A — Recuperação Híbrida (Sparse + Dense)

Três modos de retrieval disponíveis:

| Modo     | Tecnologia                   | Descrição                               |
| -------- | ---------------------------- | --------------------------------------- |
| `dense`  | BERTimbau + FAISS (baseline) | Busca semântica por cosseno             |
| `sparse` | BM25Okapi                    | Busca léxica por termos exatos          |
| `hybrid` | BM25 + FAISS via RRF         | Fusão Reciprocal Rank Fusion (k_RRF=60) |

### Parâmetros dos retrievers

**Dense (BERTimbau + FAISS):**

- Modelo: `neuralmind/bert-base-portuguese-cased` (dim=768)
- Índice: `IndexFlatIP` com vetores L2-normalizados (equivale a similaridade de cosseno exata)
- Justificativa: busca exata (FlatIP) é viável com 179 chunks e garante precisão máxima

**Sparse (BM25):**

- Implementação: `BM25Okapi` (parâmetros padrão: k1=1.5, b=0.75)
- Tokenização: lowercase → remoção de diacríticos → stemming RSLP PT-BR
- Justificativa: termos normativos específicos (ex.: "NBR 6120", "coeficiente de arrasto") se beneficiam de busca exata por token

**Hybrid (RRF):**

- Candidatos por retriever: `min(k×3, n_chunks)`
- Fusão: `score(chunk) = Σ 1/(60 + rank)` — score RRF padrão da literatura
- Deduplicação: via dicionário indexado por posição do chunk — cada chunk aparece uma única vez no resultado final
- Parâmetro k_RRF=60: valor padrão amplamente adotado, garante suavidade na fusão de rankings

---

## Pipeline RAG com citações

O chatbot executa o pipeline completo:

1. Recebe pergunta do usuário
2. Recupera top-k chunks via retriever selecionado
3. Monta prompt com o contexto normativo recuperado
4. Gera resposta **exclusivamente baseada nos trechos fornecidos**
5. Retorna resposta com **citações** no formato `[NBRxxxx, Seção Y.Y]`

### Grounding e recusa

O `src/prompts.py` define dois modos de prompt:

| Modo       | Técnicas                                                                                     |
| ---------- | -------------------------------------------------------------------------------------------- |
| `baseline` | Grounding obrigatório + formato de citação + recusa explícita                                |
| `improved` | Tudo do baseline + chain-of-thought + verificação cruzada entre normas + formato estruturado |

**Recusa adequada:** quando os trechos recuperados não contêm evidência suficiente, o modelo responde exclusivamente: _"Não encontrei informação suficiente nas normas consultadas para responder esta pergunta."_

**Guardrails:** perguntas fora do domínio normativo (preços, marcas comerciais, orçamentos) são recusadas com explicação.

### Transparência

A interface Gradio (Seção 10 do notebook) exibe:

- Resposta gerada com citações
- Trechos normativos recuperados (chunk_id, seção, score de relevância)
- Modo de retrieval ativo (dense / sparse / hybrid)

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

### Golden set

O arquivo `data/eval/golden_set.json` contém **21 perguntas** distribuídas em três categorias:

| Categoria        | Qtd | Descrição                                          |
| ---------------- | --- | -------------------------------------------------- |
| `factual_direta` | 17  | Perguntas com resposta em uma seção específica     |
| `multi_trecho`   | 3   | Perguntas que exigem combinar 2+ seções            |
| `fora_do_corpus` | 1   | Pergunta fora do domínio (testa recusa do chatbot) |

Cada entrada contém a pergunta, os `chunk_ids` relevantes esperados e a categoria.

### Recall@k (automático)

Execute a Seção 8 do notebook. Calcula Recall@k (k=3, 5, 10) para os 3 modos de retrieval usando o golden set.

### Rubrica qualitativa (manual)

Gere as respostas para os três modos de retrieval:

```bash
python scripts/gerar_rubrica.py                          # dense (padrão)
python scripts/gerar_rubrica.py --retriever sparse       # sparse
python scripts/gerar_rubrica.py --retriever hybrid       # hybrid
```

Os arquivos gerados em `data/eval/`:

| Arquivo                         | Conteúdo                                  |
| ------------------------------- | ----------------------------------------- |
| `rubrica_respostas.json`        | Perguntas + respostas do modo dense       |
| `rubrica_respostas_sparse.json` | Perguntas + respostas do modo sparse      |
| `rubrica_respostas_hybrid.json` | Perguntas + respostas do modo hybrid      |
| `rubrica_detalhada.md`          | Análise qualitativa manual completa       |
| `ragas_scores.json`             | Métricas automáticas RAGAS (faithfulness) |

**Critérios por resposta:**

| Critério     | Descrição                                  | Escala            |
| ------------ | ------------------------------------------ | ----------------- |
| Groundedness | Resposta suportada pelos trechos?          | 0–2               |
| Correção     | Resposta correta conforme as normas?       | 0–2               |
| Citações     | Cita trechos adequados?                    | 0–2               |
| Alucinação   | Inventou algo fora do corpus?              | 0=sim, 1=não      |
| Recusa       | Recusou corretamente quando sem evidência? | 0=não, 1=sim, N/A |

---

## Entregáveis

| Artefato          | Localização                | Descrição                                          |
| ----------------- | -------------------------- | -------------------------------------------------- |
| Repositório       | (este repositório)         | Código, corpus, índice e resultados de avaliação   |
| Relatório técnico | `RELATORIO.md`             | Decisões de chunking, retrieval, avaliação, trilha |
| Apresentação      | `apresentacao.md` / `.pdf` | Slides da apresentação oral                        |
| Interface         | Notebook Seção 10          | Gradio com citações e trechos recuperados visíveis |

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
│   │       ├── nbr6120/               # 13 seções
│   │       └── nbr6123/               # 166 seções
│   └── eval/
│       ├── golden_set.json            # 21 perguntas de avaliação
│       ├── rubrica_respostas.json     # respostas dense (após gerar_rubrica.py)
│       ├── rubrica_respostas_sparse.json   # respostas sparse
│       ├── rubrica_respostas_hybrid.json   # respostas hybrid
│       ├── rubrica_detalhada.md       # análise qualitativa manual
│       └── ragas_scores.json          # métricas RAGAS automáticas
├── index/                             # índice FAISS salvo (gerado pelo notebook)
├── notebooks/
│   └── rag_normas.ipynb              # notebook principal
├── scripts/
│   ├── convert_pdfs.py               # PDF → Markdown (Docling)
│   ├── split_sections_auto.py        # Markdown → seções (NBR6123)
│   ├── split_nbr6120_sections.py     # segmentação manual NBR6120
│   └── gerar_rubrica.py              # gera respostas para avaliação manual
├── src/
│   ├── ingestion.py                  # carrega seções com metadados
│   ├── chunker.py                    # gera chunks com metadados
│   ├── indexer.py                    # BERTimbau + FAISS
│   ├── hybrid_search.py              # BM25 + RRF (Trilha A)
│   ├── rag_pipeline.py               # pipeline completo RAG
│   ├── prompts.py                    # templates de prompt (grounding + recusa)
│   └── evaluator.py                  # Recall@k + rubrica
├── RELATORIO.md                      # relatório técnico completo
├── apresentacao.md                   # apresentação em Markdown
├── apresentacao.pdf                  # apresentação em PDF
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
| Busca léxica    | BM25Okapi (`rank-bm25`) + stemming RSLP PT-BR                |
| Fusão híbrida   | Reciprocal Rank Fusion (k_RRF=60)                            |
| LLM (geração)   | Groq (llama-3.3-70b) / Google Gemini / NVIDIA NIM            |
| Interface       | Gradio                                                       |
| Avaliação auto  | RAGAS (faithfulness)                                         |
