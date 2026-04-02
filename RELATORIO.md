# Relatório Chatbot RAG para Normas Estruturais ABNT

**Grupo:** Eduardo Braga, Israel Magalhães e Marcelo Carvalho
**Disciplina:** Processamento de Linguagem Natural
**Trilha escolhida:** A Recuperação Híbrida (Sparse + Dense)

---

## 1. Domínio e Corpus

### Domínio

O sistema foi desenvolvido para auxiliar engenheiros, projetistas e estudantes na consulta a **normas técnicas brasileiras de engenharia estrutural**. O corpus é fechado e composto por documentos normativos da ABNT, documentos de alta precisão terminológica e com valores numéricos críticos, onde respostas incorretas podem ter consequências práticas graves.

O domínio justifica o uso de RAG em detrimento de um LLM direto: normas são atualizadas periodicamente, contêm tabelas e fórmulas específicas, e exigem rastreabilidade das fontes (citações normativas).

### Corpus

| Norma        | Título                                             | Edição           | Seções |
| ------------ | -------------------------------------------------- | ---------------- | ------ |
| **NBR 6120** | Cargas para o cálculo de estruturas de edificações | 2019 (2ª edição) | 124    |
| **NBR 6123** | Forças devidas ao vento em edificações             | 2023             | 166    |

**Total:** 290 seções · ~626 mil caracteres

**Metadados por documento:**

| Campo    | Descrição                |
| -------- | ------------------------ |
| `doc_id` | `NBR6120` ou `NBR6123`   |
| `titulo` | Título completo da norma |
| `fonte`  | `ABNT`                   |
| `edicao` | Edição/ano da norma      |

**Justificativa da escolha:** A NBR 6120 cobre cargas permanentes e acidentais em edificações, enquanto a NBR 6123 cobre forças de vento. Juntas, formam a base das ações externas consideradas no dimensionamento estrutural brasileiro, domínio de alta relevância prática.

A NBR 6118 (projeto de estruturas de concreto) foi inicialmente incluída mas removida do corpus: o PDF disponível apresenta encoding corrompido em partes significativas (fontes não-Unicode), o que geraria chunks de baixa qualidade e potencial desinformação.

---

## 2. Chunking Decisões e Justificativas

### Estratégia: 1 seção normativa = 1 chunk

Cada chunk corresponde a uma **seção semântica auto-contida** da norma (subseção, tabela ou grupo de parágrafos relacionados).

**Processo de geração:**

1. **PDF → Markdown** via [Docling](https://github.com/DS4SD/docling): preserva estrutura de headings, tabelas e listas
2. **Markdown → seções** via `scripts/split_sections_auto.py`: divide nos headings `##` (nível 2), garantindo que cada chunk contenha um conceito ou conjunto de regras coeso

**Metadados por chunk:**

| Campo      | Descrição                                                        |
| ---------- | ---------------------------------------------------------------- |
| `chunk_id` | `NBR6120#07_tabela2_cargas_verticais` (doc_id + stem do arquivo) |
| `doc_id`   | `NBR6120` ou `NBR6123`                                           |
| `titulo`   | Título completo do documento                                     |
| `fonte`    | `ABNT`                                                           |
| `edicao`   | Edição da norma                                                  |
| `secao`    | Título da seção (extraído do frontmatter YAML)                   |
| `summary`  | Resumo gerado automaticamente da seção                           |
| `texto`    | Conteúdo puro (para embedding)                                   |
| `texto_md` | Conteúdo com frontmatter (para exibição)                         |
| `n_chars`  | Tamanho em caracteres                                            |

**Tamanho dos chunks:**

| Estatística | NBR6120      | NBR6123       |
| ----------- | ------------ | ------------- |
| Mínimo      | ~130 chars   | ~6 chars      |
| Máximo      | ~3.600 chars | ~65.000 chars |
| Mediana     | ~500 chars   | ~500 chars    |

Seções muito pequenas (< 20 chars, e.g., headings isolados como "3.1") são mantidas no índice mas raramente retornadas como top-k relevante, não prejudicam a qualidade do retrieval.

**Decisões sobre tabelas:** Tabelas muito extensas (e.g., Tabela 1 de pesos específicos, Tabela 10 de cargas variáveis) são divididas em seções de continuação pelo auto-split (`tabela_10_continuação`, `tabela_10_conclusão`). Isso as torna retrievable de forma independente sem diluir o conteúdo narrativo do chunk principal.

**Overlap:** Nenhum. A estrutura normativa já é hierarquicamente organizada, seções são unidades semânticas completas que não requerem overlap para manter coerência.

---

## 3. Baseline RAG

### Retriever (denso)

**Modelo:** `neuralmind/bert-base-portuguese-cased` (BERTimbau, dim=768)

- Pré-treinado em português, adequado ao vocabulário técnico da ABNT
- Não requer GPU para inferência (CPU viável no Colab)
- Sem dependência de API externa para embeddings

**Índice:** FAISS `IndexFlatIP` com vetores L2-normalizados

- Busca exata por cosseno (sem aproximação)
- Com 179 chunks, busca exata é computacionalmente trivial

**Configuração:** k = 3, 5 ou 10 (configurável na interface Gradio)

### Prompt e Grounding

O sistema utiliza dois templates de prompt (`src/prompts.py`):

**Baseline:**

```
REGRAS OBRIGATÓRIAS:
1. Responda APENAS com base nos trechos normativos fornecidos.
2. Cite as fontes usando o formato [NBRxxxx, Seção Y.Y].
3. Se a informação NÃO estiver nos trechos: "Não encontrei informação
   suficiente nas normas consultadas para responder esta pergunta."
4. NÃO invente, extrapole ou use conhecimento externo às normas.
```

**Melhorado (modo `improved`):** Adiciona chain-of-thought (identificar → verificar → cruzar referências → confirmar suporte) e formato estruturado de resposta (resposta objetiva → detalhamento → lista de referências).

### Citações

Cada resposta inclui referências no formato `[NBR6120, Seção 2.2.1]`. A interface Gradio mostra os trechos recuperados com chunk_id, score de relevância e texto completo.

### Recusa adequada

O prompt instrui o LLM a recusar com frase canônica quando:

- A informação não está nos trechos recuperados
- A pergunta é sobre tema não normativo (preços, marcas comerciais, etc.)

### LLM de geração

Provider padrão: **Groq** (llama-3.3-70b-versatile). Fallback: Google Gemini ou NVIDIA NIM (OpenAI-compatible).

---

## 4. Trilha A Recuperação Híbrida

### Motivação

O retriever denso (BERTimbau) captura semântica mas pode falhar em termos muito específicos não vistos no pré-treino: valores numéricos (`kN/m²`), nomes de seções (`§ 2.2.1.6`), ou termos técnicos raros. O BM25 captura termos exatos mas ignora sinônimos e paráfrases. A fusão híbrida combina as vantagens de ambos.

### Implementação

**`src/hybrid_search.py`** dois retrievers:

**SparseRetriever (BM25):**

- Tokenizador: regex alfanumérico, lowercase, sem stemming
- Modelo: `BM25Okapi` (`rank-bm25`)
- Score: TF-IDF com normalização pelo comprimento do documento

**HybridRetriever (BM25 + FAISS + RRF):**

- Recupera `min(k×3, n_chunks)` candidatos de cada retriever
- Funde via **Reciprocal Rank Fusion**: `score(chunk) = Σ 1 / (60 + rank)`
- Deduplica por `chunk_id` antes da fusão (cada chunk conta uma vez por retriever)
- Parâmetro `k_RRF = 60` (valor padrão da literatura)

### Parâmetros

| Parâmetro                | Valor       | Justificativa                                                                      |
| ------------------------ | ----------- | ---------------------------------------------------------------------------------- |
| k_RRF                    | 60          | Constante padrão RRF, equilibra contribuições de retrievers com rankings distintos |
| Candidatos por retriever | k×3         | Amplia o pool antes da fusão, reduzindo o risco de perder o chunk correto          |
| Tokenização              | regex `\W+` | Preserva números e unidades (`kN`, `m²`, `1,5`) como tokens relevantes             |

### Avaliação Recall@k comparativo

_Os valores abaixo serão preenchidos após execução do notebook (Seção 8)._

| k   | Dense (baseline) | Sparse (BM25) | Hybrid (RRF) |
| --- | ---------------- | ------------- | ------------ |
| 3   | —                | —             | —            |
| 5   | —                | —             | —            |
| 10  | —                | —             | —            |

### Análise de trade-offs

**Dense** se destaca em perguntas paráfrasticas (ex.: "peso próprio da estrutura" → recupera seção de "carga permanente" sem overlap léxico exato).

**Sparse** se destaca em perguntas com termos muito específicos: valores numéricos (`3 kN/m²`), referências a parágrafos (`§ 2.2.1.6`), nomes de materiais (`granito`, `concreto armado`).

**Hybrid** tende a igualar ou superar os dois modos isolados, especialmente para perguntas multi_trecho que exigem cruzar uma seção narrativa com uma tabela.

**Latência:**

| Modo   | Retrieval típico | Gargalo                       |
| ------ | ---------------- | ----------------------------- |
| Sparse | < 1 ms           | —                             |
| Dense  | 5–20 ms          | Encoding da query (BERTimbau) |
| Hybrid | 5–20 ms          | Dominado pelo encoding Dense  |

---

## 5. Avaliação

### 5.1 Golden Set

21 perguntas cobrindo os dois documentos do corpus:

| Categoria        | Quantidade | Descrição                                       |
| ---------------- | ---------- | ----------------------------------------------- |
| `factual_direta` | 17         | Pergunta com resposta direta em uma seção       |
| `multi_trecho`   | 3          | Requer combinar 2–4 seções para responder       |
| `fora_do_corpus` | 1          | Testa recusa (pergunta sobre preço de concreto) |

**Distribuição por norma:**

- NBR 6120: 10 perguntas (cargas permanentes, acidentais, tabelas de pesos)
- NBR 6123: 10 perguntas (velocidade do vento, fatores S1/S2/S3, pressão dinâmica, análise dinâmica)

### 5.2 Recall@k

_Preencher com resultados após execução da Seção 8 do notebook._

### 5.3 Rubrica Qualitativa

_Avaliação manual de 15+ respostas geradas pelo pipeline (modo dense, k=5)._

A rubrica foi aplicada por **Marcelo Carvalho** (engenheiro civil), garantindo que o critério **Correção** seja avaliado com expertise no domínio normativo.

**Critérios:**

| Critério     | Escala                                       |
| ------------ | -------------------------------------------- |
| Groundedness | 0–2 (não suportada → totalmente suportada)   |
| Correção     | 0–2 (incorreta → correta conforme as normas) |
| Citações     | 0–2 (ausentes/erradas → adequadas)           |
| Alucinação   | 0=sim / 1=não                                |
| Recusa       | 0=falhou / 1=correta / N/A                   |

_Tabela de scores: ver `data/eval/rubrica_respostas.json`_

---

## 6. Limitações e Próximos Passos

### Limitações

**Corpus limitado:** O corpus cobre cargas permanentes, acidentais e forças de vento, mas deixa de fora normas importantes do projeto estrutural (NBR 6118 — concreto, NBR 7190 — madeira, NBR 8800 — aço). A NBR 6118 foi excluída por problemas de encoding no PDF disponível.

**Chunking sem sobreposição:** Algumas respostas requerem informação que está no início de uma seção narrativa e no final de outra. Com overlap zero, o retriever pode não recuperar os dois chunks simultaneamente, mitigado pelo hybrid retriever (k×3 candidatos).

**Seções muito grandes:** A seção `6.2 Cargas variáveis` da NBR 6120 (nova edição 2019) e algumas seções da NBR 6123 têm > 20.000 chars, acima do que modelos de embedding conseguem representar fielmente em um único vetor (limite típico: ~512 tokens). Em versões futuras, seria recomendável sub-dividir essas seções.

**Formulas não decodificadas:** O Docling converte fórmulas matemáticas para `<!-- formula-not-decoded -->` quando não consegue renderizá-las. Isso afeta algumas seções da NBR 6123 que contêm equações.

**Dependência de API externa:** A geração de respostas depende de APIs de LLM (Groq/Gemini). Para uso totalmente local, seria necessário integrar um modelo como `llama.cpp` ou `Ollama`.

### Próximos Passos

1. **Incluir NBR 6118** quando um PDF com encoding correto estiver disponível
2. **Sub-dividir seções longas** (> 2.000 chars) para melhorar qualidade dos embeddings
3. **Reranking** (Trilha B) como camada adicional sobre o hybrid retriever
4. **Avaliação com RAGAS** para automatizar parte da rubrica qualitativa
5. **Interface standalone** (Streamlit ou FastAPI) desacoplada do notebook Jupyter
