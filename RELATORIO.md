# Relatório Chatbot RAG para Normas Estruturais ABNT

**Grupo:** Eduardo Braga, Israel Magalhães e Marcelo Carvalho   
**Disciplina:** Processamento de Linguagem Natural   
**Trilha escolhida:** A Recuperação Híbrida (Sparse \+ Dense)

---

## 1\. Domínio e Corpus

### Domínio

O sistema foi desenvolvido para auxiliar engenheiros, projetistas e estudantes na consulta a **normas técnicas brasileiras de engenharia estrutural**. O corpus é fechado e composto por documentos normativos da ABNT, documentos de alta precisão terminológica e com valores numéricos críticos, onde respostas incorretas podem ter consequências práticas graves.

O domínio justifica o uso de RAG em detrimento de um LLM direto: normas são atualizadas periodicamente, contêm tabelas e fórmulas específicas, e exigem rastreabilidade das fontes (citações normativas).

### Corpus

| Norma | Título | Edição | Seções |
| :---- | :---- | :---- | :---- |
| **NBR 6120** | Cargas para o cálculo de estruturas de edificações | 2019 (2ª edição) | 124 |
| **NBR 6123** | Forças devidas ao vento em edificações | 2023 | 166 |

**Total:** 290 seções · \~626 mil caracteres

**Metadados por documento:**

| Campo | Descrição |
| :---- | :---- |
| `doc_id` | `NBR6120` ou `NBR6123` |
| `titulo` | Título completo da norma |
| `fonte` | `ABNT` |
| `edicao` | Edição/ano da norma |

**Justificativa da escolha:** A NBR 6120 cobre cargas permanentes e acidentais em edificações, enquanto a NBR 6123 cobre forças de vento. Juntas, formam a base das ações externas consideradas no dimensionamento estrutural brasileiro, domínio de alta relevância prática.

A NBR 6118 (projeto de estruturas de concreto) foi inicialmente incluída mas removida do corpus: o PDF disponível apresenta encoding corrompido em partes significativas (fontes não-Unicode), o que geraria chunks de baixa qualidade e potencial desinformação.

---

## 2\. Chunking Decisões e Justificativas

### Estratégia: 1 seção normativa \= 1 chunk

Cada chunk corresponde a uma **seção semântica auto-contida** da norma (subseção, tabela ou grupo de parágrafos relacionados).

**Processo de geração:**

1. **PDF → Markdown** via [Docling](https://github.com/DS4SD/docling): preserva estrutura de headings, tabelas e listas  
2. **Markdown → seções** via `scripts/split_sections_auto.py`: divide nos headings `##` (nível 2), garantindo que cada chunk contenha um conceito ou conjunto de regras coeso

**Metadados por chunk:**

| Campo | Descrição |
| :---- | :---- |
| `chunk_id` | `NBR6120#07_tabela2_cargas_verticais` (doc\_id \+ stem do arquivo) |
| `doc_id` | `NBR6120` ou `NBR6123` |
| `titulo` | Título completo do documento |
| `fonte` | `ABNT` |
| `edicao` | Edição da norma |
| `secao` | Título da seção (extraído do frontmatter YAML) |
| `summary` | Resumo gerado automaticamente da seção |
| `texto` | Conteúdo puro (para embedding) |
| `texto_md` | Conteúdo com frontmatter (para exibição) |
| `n_chars` | Tamanho em caracteres |

**Tamanho dos chunks:**

| Estatística | NBR6120 | NBR6123 |
| :---- | :---- | :---- |
| Mínimo | \~130 chars | \~6 chars |
| Máximo | \~3.600 chars | \~65.000 chars |
| Mediana | \~500 chars | \~500 chars |

Seções muito pequenas (\< 20 chars, e.g., headings isolados como "3.1") são mantidas no índice mas raramente retornadas como top-k relevante, não prejudicam a qualidade do retrieval.

**Decisões sobre tabelas:** Tabelas muito extensas (e.g., Tabela 1 de pesos específicos, Tabela 10 de cargas variáveis) são divididas em seções de continuação pelo auto-split (`tabela_10_continuação`, `tabela_10_conclusão`). Isso as torna retrievable de forma independente sem diluir o conteúdo narrativo do chunk principal.

**Overlap:** Nenhum. A estrutura normativa já é hierarquicamente organizada, seções são unidades semânticas completas que não requerem overlap para manter coerência.

---

## 3\. Baseline RAG

### Retriever (denso)

**Modelo:** `neuralmind/bert-base-portuguese-cased` (BERTimbau, dim=768)

- Pré-treinado em português, adequado ao vocabulário técnico da ABNT  
- Não requer GPU para inferência (CPU viável no Colab)  
- Sem dependência de API externa para embeddings

**Índice:** FAISS `IndexFlatIP` com vetores L2-normalizados

- Busca exata por cosseno (sem aproximação)  
- Com 179 chunks, busca exata é computacionalmente trivial

**Configuração:** k \= 3, 5 ou 10 (configurável na interface Gradio)

### Prompt e Grounding

O sistema utiliza dois templates de prompt (`src/prompts.py`):

**Baseline:**

REGRAS OBRIGATÓRIAS:

1\. Responda APENAS com base nos trechos normativos fornecidos.

2\. Cite as fontes usando o formato \[NBRxxxx, Seção Y.Y\].

3\. Se a informação NÃO estiver nos trechos: "Não encontrei informação

   suficiente nas normas consultadas para responder esta pergunta."

4\. NÃO invente, extrapole ou use conhecimento externo às normas.

**Melhorado (modo `improved`):** Adiciona chain-of-thought (identificar → verificar → cruzar referências → confirmar suporte) e formato estruturado de resposta (resposta objetiva → detalhamento → lista de referências).

### Citações

Cada resposta inclui referências no formato `[NBR6120, Seção 2.2.1]`. A interface Gradio mostra os trechos recuperados com chunk\_id, score de relevância e texto completo.

### Recusa adequada

O prompt instrui o LLM a recusar com frase canônica quando:

- A informação não está nos trechos recuperados  
- A pergunta é sobre tema não normativo (preços, marcas comerciais, etc.)

### LLM de geração

Provider padrão: **Groq** (llama-3.3-70b-versatile). Fallback: Google Gemini ou NVIDIA NIM (OpenAI-compatible).

---

## 4\. Trilha A Recuperação Híbrida

### Motivação

O retriever denso (BERTimbau) captura semântica mas pode falhar em termos muito específicos não vistos no pré-treino: valores numéricos (`kN/m²`), nomes de seções (`§ 2.2.1.6`), ou termos técnicos raros. O BM25 captura termos exatos mas ignora sinônimos e paráfrases. A fusão híbrida combina as vantagens de ambos.

### Implementação

**`src/hybrid_search.py`** dois retrievers:

**SparseRetriever (BM25):**

- Tokenizador: regex alfanumérico, lowercase, sem stemming  
- Modelo: `BM25Okapi` (`rank-bm25`)  
- Score: TF-IDF com normalização pelo comprimento do documento

**HybridRetriever (BM25 \+ FAISS \+ RRF):**

- Recupera `min(k×3, n_chunks)` candidatos de cada retriever  
- Funde via **Reciprocal Rank Fusion**: `score(chunk) = Σ 1 / (60 + rank)`  
- Deduplica por `chunk_id` antes da fusão (cada chunk conta uma vez por retriever)  
- Parâmetro `k_RRF = 60` (valor padrão da literatura)

### Parâmetros

| Parâmetro | Valor | Justificativa |
| :---- | :---- | :---- |
| k\_RRF | 60 | Constante padrão RRF, equilibra contribuições de retrievers com rankings distintos |
| Candidatos por retriever | k×3 | Amplia o pool antes da fusão, reduzindo o risco de perder o chunk correto |
| Tokenização | regex `\W+` | Preserva números e unidades (`kN`, `m²`, `1,5`) como tokens relevantes |

### Avaliação Recall@k comparativo

Executado via `src/evaluator.py` com o índice reconstruído sobre as 290 seções (NBR 6120:2019 \+ NBR 6123:2023). 20 perguntas avaliáveis (1 `fora_do_corpus` excluída).

| k | Dense (baseline) | Sparse (BM25) | Hybrid (RRF) |
| :---- | :---- | :---- | :---- |
| 3 | 0,05 (1/20) | 0,75 (15/20) | 0,45 (9/20) |
| 5 | 0,05 (1/20) | 0,80 (16/20) | 0,55 (11/20) |
| 10 | 0,20 (4/20) | 0,85 (17/20) | 0,90 (18/20) |

Arquivos gerados: `index/recall_at_k_all.json`, `index/eval_comparative.csv`.

### Análise de trade-offs

**Dense** apresentou recall muito baixo (0,05–0,20). Após a refatoração das seções da NBR 6120 para a edição 2019 (124 chunks com títulos técnicos longos), o BERTimbau não representa bem os novos chunk\_ids semanticamente. O único acerto consistente foi Q11 (velocidade básica V0), onde a query contém os mesmos termos do chunk.

**Sparse (BM25)** dominou neste corpus: recall 0,75–0,85. A correspondência lexical exata captura termos técnicos normativos (ex.: "cargas variáveis", "garagem", "vento básico", "fator S2") que o dense não consegue mapear semanticamente.

**Hybrid** combina os dois: em k=10 atinge 0,90, o melhor resultado geral. Para k pequeno (3–5), o BM25 sozinho já é superior ao hybrid, pois o dense "contamina" o ranking com chunks irrelevantes via RRF.

**Latência:**

| Modo | Retrieval típico | Gargalo |
| :---- | :---- | :---- |
| Sparse | \< 1 ms | — |
| Dense | 5–20 ms | Encoding da query (BERTimbau) |
| Hybrid | 5–20 ms | Dominado pelo encoding Dense |

---

## 5\. Avaliação

### 5.1 Golden Set

21 perguntas cobrindo os dois documentos do corpus:

| Categoria | Quantidade | Descrição |
| :---- | :---- | :---- |
| `factual_direta` | 17 | Pergunta com resposta direta em uma seção |
| `multi_trecho` | 3 | Requer combinar 2–4 seções para responder |
| `fora_do_corpus` | 1 | Testa recusa (pergunta sobre preço de concreto) |

**Distribuição por norma:**

- NBR 6120: 10 perguntas (cargas permanentes, acidentais, tabelas de pesos)  
- NBR 6123: 10 perguntas (velocidade do vento, fatores S1/S2/S3, pressão dinâmica, análise dinâmica)

### 5.2 Recall@k

Executado via `src/evaluator.py` — 20 perguntas avaliáveis (1 `fora_do_corpus` excluída). Modo dense \= BERTimbau \+ FAISS. Arquivos de detalhe em `index/eval_details.csv`.

| k | Dense (baseline) | Sparse (BM25) | Hybrid (RRF) |
| :---- | :---- | :---- | :---- |
| 3 | 0,05 (1/20) | 0,75 (15/20) | 0,45 (9/20) |
| 5 | 0,05 (1/20) | 0,80 (16/20) | 0,55 (11/20) |
| 10 | 0,20 (4/20) | 0,85 (17/20) | 0,90 (18/20) |

**Perguntas com HIT no modo dense (k=10):** Q3 (peso próprio), Q11 (velocidade V0), Q12 (pressão dinâmica), Q20 (análise dinâmica).

**Interpretação:** O BERTimbau apresenta baixo recall nas seções da NBR 6120:2019 porque os novos chunk\_ids têm títulos técnicos muito específicos que o modelo não representa bem semanticamente. BM25 supera o dense em todas as configurações de k neste corpus.

### 5.3 Rubrica Qualitativa

Avaliação de 17 perguntas do golden set nos três modos de retrieval (dense / sparse / hybrid), k=5, pipeline `baseline` com Groq llama-4-scout-17b.

**Ficheiro de detalhe completo:** `data/eval/rubrica_detalhada.md` — contém as respostas integrais dos 3 modos \+ tabela de preenchimento por questão.

**Automação:** a coluna *Faithfulness* foi calculada via **RAGAS** (Groq llama-4-scout como LLM-judge). Mede o grau em que as afirmações da resposta têm suporte nos trechos recuperados (0–1). Scores completos para os 3 modos em `data/eval/ragas_scores.json`.

⚠ **Limitação conhecida do RAGAS para recusas:** quando o pipeline responde "Não encontrei informação suficiente", o RAGAS atribui Faithfulness ≈ 0 (a expressão de recusa não aparece literalmente nos chunks). Isso **não indica alucinação** — indica apenas que a recusa é uma decisão do LLM, não uma inferência extraída dos trechos.

#### Critérios

| Critério | Opções | Pergunta-guia | Preenchimento |
| :---- | :---- | :---- | :---- |
| Groundedness | S / N | A resposta está suportada pelos trechos? | Automático (RAGAS) |
| **Correção** | **S / P / N** | Está factualmente correta conforme a norma? | **Marcelo** |
| Citações | S / N | Cita trechos adequados e coerentes? | Automático (RAGAS) |
| Alucinação | S / N | Inventou algo fora do corpus? | Automático (RAGAS) |
| **Recusa** | **S / N / N/A** | Quando não havia evidência, recusou corretamente? | **Marcelo** |

**Marcelo preenche apenas 2 colunas:** `Correção` (S/P/N) e `Recusa` (S/N/N/A). Para as demais, o RAGAS já fornece o valor de referência via *Faithfulness*. Respostas de recusa têm RAGAS ≈ 0 por limitação do método — isso **não significa alucinação**.

#### Tabela de avaliação — 3 modos (dense / sparse / hybrid)

Consulte `data/eval/rubrica_detalhada.md` para ver a resposta completa de cada modo.

| \# | Pergunta (resumo) | Cat | Hit D/S/H | Faith D / S / H | Correção | Recusa |
| :---- | :---- | :---- | :---: | :---: | :---- | :---- |
| Q1 | Carga acidental em escritório (kN/m²)? | fact | ✗/✗/✗ | 0,00 / 1,00 / 1,00 | N | N/A |
| Q2 | Carga acidental garagem veículos leves? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q3 | Peso próprio \= que tipo de carga? | fact | ✗/✓/✓ | 0,50 / 1,00 / 0,67 | S | N/A |
| Q4 | Paredes divisórias sem posição — como tratar? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q5 | Peso específico do concreto armado? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q6 | Carga ao longo de parapeitos e balcões? | fact | ✗/✗/✗ | 1,00 / 0,75 / 1,00 | S | N/A |
| Q7 | Critérios categoria projeto para garagens? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q8 | Carga mínima em coberturas (manutenção)? | fact | ✗/✓/✓ | 0,00 / 0,86 / 0,83 | N | N/A |
| Q9 | Quando reduzir cargas acidentais? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q10 | Redução percentual — 6 ou mais pisos? | multi | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q11 | Definição velocidade básica V0? | fact | ✓/✓/✓ | 1,00 / 1,00 / 0,80 | S | N/A |
| Q12 | Pressão dinâmica do vento — definição e cálculo? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q13 | Três fatores S1, S2, S3 para calcular Vk? | multi | ✗/✓/✓ | 0,83 / 1,00 / 0,25 ⚠ | S | N/A |
| Q14 | O que considera o fator topográfico S1? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q15 | O que considera o fator S2? | fact | ✗/✓/✓ | N/D / 1,00 / N/D | S | N/A |
| Q16 | Valor mínimo do fator S3 para residências? | fact | ✗/✓/✓ | 0,00 / 0,67 / 0,67 | S | N/A |
| Q21 | Preço m³ concreto para obra em Brasília? | fora | —/—/— | 0,00 / 0,00 / 0,00 ¹ | — | S |

*¹ RAGAS ≈ 0 para recusas por limitação estrutural do método (ver nota acima). ⚠ Q13 hybrid Faith=0,25: resposta com baixo grounding — ver Exemplo 3\.*

#### Ganho do Sparse/Hybrid sobre o Dense

Para evidenciar o ganho da Trilha A, a tabela abaixo cruza Hit@5 dos três modos:

| \# | Pergunta (resumo) | Hit D/S/H | Faith Dense | Faith Sparse | Faith Hybrid |
| :---- | :---- | :---: | :---: | :---: | :---: |
| Q1 | Carga acidental escritório | ✗/✗/✗ | 0,00 | 1,00 | 1,00 |
| Q2 | Carga garagem veículos leves | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |
| Q3 | Peso próprio \= permanente? | ✗/✓/✓ | 0,50 | 1,00 | 0,67 |
| Q5 | Peso específico concreto armado | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |
| Q9 | Redução cargas acidentais — quando? | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |
| Q11 | Velocidade básica V0 | ✓/✓/✓ | 1,00 | 1,00 | 0,80 |
| Q12 | Pressão dinâmica do vento | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |
| Q14 | Fator topográfico S1 | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |

**Síntese:** Sparse e Hybrid recuperam o chunk correto em 15–16/20 questões contra 1/20 do Dense. Faithfulness do Sparse ≈ 1,00 na maioria dos casos confirma que, quando o chunk certo é recuperado, o LLM gera respostas bem fundamentadas. Hybrid tem Faithfulness igualmente alta, com exceção de Q13 (0,25) onde a resposta é confusa — ver Exemplo 3\.

#### Exemplos notáveis

---

**Exemplo 1 — Q11: resposta correta (dense e sparse)** *"Como é definida a velocidade básica do vento V0 pela NBR 6123?"*

Dense/Sparse: *"A velocidade básica do vento, V0, é definida como a velocidade de uma rajada de 3 s, a 10 m acima do terreno, em campo aberto e plano, excedida em média uma vez em 50 anos \[NBR6123, Seção 5.1\]."*

Faithfulness \= 1,00. A definição reproduz fielmente o §5.1 da NBR 6123:2023. Única questão onde o dense também acerta (o nome do chunk `51_velocidade_básica_do_vento_v0` é semânticamente próximo da query).

---

**Exemplo 2 — Q2: falha dense, acerto sparse** *"Qual o valor de carga acidental para uma garagem de veículos leves?"*

Dense (Hit ✗): *"Não encontrei informação suficiente nas normas consultadas para responder esta pergunta."*

Sparse (Hit ✓): *"\[NBR6120, Seção 6.6.1\] A carga acidental para garagem de veículos leves é dada pela Tabela 13 da NBR6120. Considerando veículos leves, a Categoria I é a mais adequada, com as seguintes cargas: Carga uniformemente distribuída: 3 kN/m². Carga concentrada (Qk): 12 kN, atuando em uma região de 10 cm × 10 cm."*

Ilustra o ganho direto do BM25 sobre o dense: a query contém "garagem" e "veículos leves", termos que o BM25 casou exatamente com `NBR6120#98_661_ações_em_garagens…`. O BERTimbau não fez essa associação semanticamente.

---

**Exemplo 3 — Q13: resposta parcial com risco de alucinação (dense)** *"Quais são os três fatores que multiplicam V0 para obter a velocidade característica Vk?"*

Dense (Faithfulness \= 0,83): *"…S2 é confirmado como um dos fatores. S1 e S3 são mencionados implicitamente como necessários para calcular Vk, mas seus valores ou como são obtidos não estão detalhados na seção A.1 fornecida. (…) SOMENTE S2 é apresentado \[NBR6123, Seção A.1 Fator S2\]."*

O LLM menciona a fórmula `Vk = S1·S2·S3·V0` sem encontrá-la nos chunks — potencial alucinação parcial. Sparse (Hit ✓, Faith 1,00) recupera todos os chunks de S1/S2/S3 e responde com precisão.  

---

**Exemplo 4 — Q21: recusa correta** *"Como calcular o preço do m³ de concreto para uma obra em Brasília?"*

Dense/Sparse: *"Não encontrei informação suficiente nas normas consultadas para responder esta pergunta. (A consulta está limitada a normas técnicas ABNT, e a pergunta envolve tema não normativo, especificamente relacionado a preços e orçamentos.)"*

Recusa correta e bem justificada — o corpus cobre apenas normas de cargas e vento, não precificação. O LLM ainda acrescentou a razão da recusa, o que é um comportamento desejável de grounding. Recusa \= 1 ✓.

---

---

## 6\. Limitações e Próximos Passos

### Limitações

**Corpus limitado:** O corpus cobre cargas permanentes, acidentais e forças de vento, mas deixa de fora normas importantes do projeto estrutural (NBR 6118 — concreto, NBR 7190 — madeira, NBR 8800 — aço). A NBR 6118 foi excluída por problemas de encoding no PDF disponível.

**Chunking sem sobreposição:** Algumas respostas requerem informação que está no início de uma seção narrativa e no final de outra. Com overlap zero, o retriever pode não recuperar os dois chunks simultaneamente, mitigado pelo hybrid retriever (k×3 candidatos).

**Seções muito grandes:** A seção `6.2 Cargas variáveis` da NBR 6120 (nova edição 2019\) e algumas seções da NBR 6123 têm \> 20.000 chars, acima do que modelos de embedding conseguem representar fielmente em um único vetor (limite típico: \~512 tokens). Em versões futuras, seria recomendável sub-dividir essas seções.

**Formulas não decodificadas:** O Docling converte fórmulas matemáticas para `<!-- formula-not-decoded -->` quando não consegue renderizá-las. Isso afeta algumas seções da NBR 6123 que contêm equações.

**Dependência de API externa:** A geração de respostas depende de APIs de LLM (Groq/Gemini). Para uso totalmente local, seria necessário integrar um modelo como `llama.cpp` ou `Ollama`.

## 7\. Referências

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. *NBR 6118: Projeto de estruturas de concreto — Procedimento*. Rio de Janeiro: ABNT, 2023\.

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. *NBR 6120: Cargas para o cálculo de estruturas de edificações*. 2\. ed. Rio de Janeiro: ABNT, 2019\.

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. *NBR 6123: Forças devidas ao vento em edificações*. Rio de Janeiro: ABNT, 2023\.

BROWN, Dorian. *rank-bm25: A collection of BM25 algorithms in Python*. GitHub. Disponível em: [https://github.com/dorianbrown/rank\_bm25](https://github.com/dorianbrown/rank_bm25). Acesso em: 3 abr. 2026\.

ES, Shahul et al. *RAGAS documentation*. Disponível em: [https://docs.ragas.io](https://docs.ragas.io). Acesso em: 3 abr. 2026\.

GRADIO. *Gradio documentation*. Disponível em: [https://www.gradio.app/docs](https://www.gradio.app/docs). Acesso em: 3 abr. 2026\.

GROQ. *Groq API documentation*. Disponível em: [https://console.groq.com/docs](https://console.groq.com/docs). Acesso em: 3 abr. 2026\.

HUGGING FACE. *Transformers documentation*. Disponível em: [https://huggingface.co/docs/transformers](https://huggingface.co/docs/transformers). Acesso em: 3 abr. 2026\.

IBM RESEARCH. *Docling: document processing toolkit for generative AI pipelines*. GitHub, 2024\. Disponível em: [https://github.com/DS4SD/docling](https://github.com/DS4SD/docling). Acesso em: 3 abr. 2026\.

META AI. *FAISS: A library for efficient similarity search and clustering of dense vectors*. GitHub. Disponível em: [https://github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss). Acesso em: 3 abr. 2026\.

TEIXEIRA, Israel Magalhães; BRAGA, Eduardo; CARVALHO, Marcelo. *pln-rag-normas-estruturais: Chatbot RAG para normas estruturais ABNT*. GitHub, 2026\. Disponível em: [https://github.com/israelmteixeira1/pln-rag-normas-estruturais](https://github.com/israelmteixeira1/pln-rag-normas-estruturais). Acesso em: 3 abr. 2026\.  
