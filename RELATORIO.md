# Relatório Chatbot RAG para Normas Estruturais ABNT

**Grupo:** Eduardo Braga, Israel Magalhães e Marcelo Carvalho
**Disciplina:** Processamento de Linguagem Natural
**Trilha escolhida:** A — Recuperação Híbrida (*Sparse* + *Dense*)

---

## 1. Domínio e Corpus

### Domínio

O sistema foi desenvolvido para auxiliar engenheiros, projetistas e estudantes na consulta a **normas técnicas brasileiras de engenharia estrutural**. O corpus é fechado e composto por documentos normativos da ABNT — documentos de alta precisão terminológica e com valores numéricos críticos, onde respostas incorretas podem ter consequências práticas graves.

O domínio justifica o uso de RAG em detrimento de um LLM direto: normas são atualizadas periodicamente, contêm tabelas e fórmulas específicas, e exigem rastreabilidade das fontes (citações normativas).

### Corpus

| Norma | Título | Edição | Seções |
| :---- | :---- | :---- | :---- |
| **NBR 6120** | Cargas para o cálculo de estruturas de edificações | 2019 (2ª edição) | 124 |
| **NBR 6123** | Forças devidas ao vento em edificações | 2023 | 166 |

**Total:** 290 seções · ~626 mil caracteres

**Metadados por documento:**

| Campo | Descrição |
| :---- | :---- |
| `doc_id` | `NBR6120` ou `NBR6123` |
| `titulo` | Título completo da norma |
| `fonte` | `ABNT` |
| `edicao` | Edição/ano da norma |

**Justificativa da escolha:** A NBR 6120 cobre cargas permanentes e acidentais em edificações, enquanto a NBR 6123 cobre forças de vento. Juntas, formam a base das ações externas consideradas no dimensionamento estrutural brasileiro, domínio de alta relevância prática.

A NBR 6118 (projeto de estruturas de concreto) foi inicialmente incluída mas removida do corpus: o PDF disponível apresenta codificação de caracteres corrompida em trechos significativos (fontes sem suporte Unicode), o que geraria *chunks* de baixa qualidade e potencial desinformação.

---

## 2. Segmentação (*Chunking*) — Decisões e Justificativas

### Estratégia: cada seção normativa corresponde a um *chunk*

Cada *chunk* corresponde a uma **seção semântica autocontida** da norma (subseção, tabela ou grupo de parágrafos relacionados). Essa estratégia respeita a organização hierárquica dos documentos normativos, evitando cortes arbitrários no meio de definições ou requisitos.

**Processo de geração:**

1. **PDF → Markdown** via [Docling](https://github.com/DS4SD/docling): preserva estrutura de cabeçalhos, tabelas e listas.
2. **Markdown → seções** via `scripts/split_sections_auto.py`: divide nos cabeçalhos `##` (nível 2), garantindo que cada *chunk* contenha um conceito ou conjunto de regras coeso.

**Metadados por *chunk*:**

| Campo | Descrição |
| :---- | :---- |
| `chunk_id` | `NBR6120#07_tabela2_cargas_verticais` (`doc_id` + radical do nome do arquivo) |
| `doc_id` | `NBR6120` ou `NBR6123` |
| `titulo` | Título completo do documento |
| `fonte` | `ABNT` |
| `edicao` | Edição da norma |
| `secao` | Título da seção (extraído do *frontmatter* YAML) |
| `summary` | Resumo gerado automaticamente da seção |
| `texto` | Conteúdo puro (para *embedding*) |
| `texto_md` | Conteúdo com *frontmatter* (para exibição) |
| `n_chars` | Tamanho em caracteres |

**Tamanho dos *chunks*:**

| Estatística | NBR 6120 | NBR 6123 |
| :---- | :---- | :---- |
| Mínimo | ~130 caracteres | ~6 caracteres |
| Máximo | ~3.600 caracteres | ~65.000 caracteres |
| Mediana | ~500 caracteres | ~500 caracteres |

Seções muito pequenas (< 20 caracteres, ex.: cabeçalhos isolados como "3.1") foram mantidas no índice, mas raramente são retornadas como *top-k* relevante e não prejudicaram a qualidade da recuperação.

**Decisões sobre tabelas:** Tabelas muito extensas (ex.: Tabela 1 de pesos específicos, Tabela 10 de cargas variáveis) são divididas em seções de continuação pelo *auto-split* (`tabela_10_continuação`, `tabela_10_conclusão`). Isso as torna recuperáveis de forma independente sem diluir o conteúdo narrativo do *chunk* principal.

**Sobreposição (*overlap*):** Nenhuma. A estrutura normativa já é hierarquicamente organizada — seções são unidades semânticas completas que não requerem sobreposição para manter coerência.

---

## 3. *Baseline* RAG

### *Retriever* denso

Para o *retriever* denso do *baseline*, utilizamos o BERTimbau, um modelo BERT pré-treinado em português brasileiro.

**Modelo:** `neuralmind/bert-base-portuguese-cased` (BERTimbau, dimensão 768)

- Pré-treinado em português, adequado ao vocabulário técnico da ABNT
- Não requer GPU para inferência (CPU viável no Colab)
- Sem dependência de API externa para a etapa de recuperação

**Índice:** FAISS `IndexFlatIP` com vetores L2-normalizados

- Busca exata por cosseno (sem aproximação)
- Com 290 *chunks*, busca exata é computacionalmente trivial

**Configuração:** k = 3, 5 ou 10 (configurável na interface Gradio)

### *Prompt* e *grounding*

O sistema utiliza um *template* de *prompt* com regras de *grounding* (`src/prompts.py`):

> REGRAS OBRIGATÓRIAS:
>
> 1. Responda APENAS com base nos trechos normativos fornecidos.
> 2. Cite as fontes usando o formato [NBRxxxx, Seção Y.Y].
> 3. Se a informação NÃO estiver nos trechos: "Não encontrei informação suficiente nas normas consultadas para responder esta pergunta."
> 4. NÃO invente, extrapole ou use conhecimento externo às normas.

### Citações

Cada resposta inclui referências no formato `[NBR6120, Seção 2.2.1]`. A interface Gradio mostra os trechos recuperados com `chunk_id`, pontuação de relevância e texto completo.

### Recusa adequada

O *prompt* instrui o LLM a recusar com frase canônica quando:

- A informação não está nos trechos recuperados
- A pergunta é sobre tema não normativo (preços, marcas comerciais etc.)

### LLM de geração

Provedor padrão: **Groq** (llama-3.3-70b-versatile). Alternativa: Google Gemini ou NVIDIA NIM (compatível com API OpenAI).

---

## 4. Trilha A — Recuperação Híbrida

### Motivação

O *retriever* denso (BERTimbau) captura semântica, mas pode falhar em termos muito específicos não vistos no pré-treino: valores numéricos (`kN/m²`), nomes de seções (`2.2.1.6`), ou termos técnicos raros. O BM25 captura termos exatos, mas ignora sinônimos e paráfrases. A fusão híbrida combina as vantagens de ambos.

### Implementação

O módulo `src/hybrid_search.py` implementa dois *retrievers* adicionais ao denso:

**SparseRetriever (BM25):**

- Tokenizador: *regex* alfanumérico, caixa baixa, com *stemming* PT-BR
- Modelo: `BM25Okapi` (`rank-bm25`)
- Pontuação: TF-IDF com normalização pelo comprimento do documento

**HybridRetriever (BM25 + FAISS + RRF):**

- Recupera `min(k×3, n_chunks)` candidatos de cada *retriever*
- Funde via **Reciprocal Rank Fusion**: `score(chunk) = Σ 1 / (60 + rank)`
- Deduplica por `chunk_id` antes da fusão (cada *chunk* conta uma vez por *retriever*)
- Parâmetro `k_RRF = 60` (valor padrão da literatura)

### Parâmetros

| Parâmetro | Valor | Justificativa |
| :---- | :---- | :---- |
| k\_RRF | 60 | Constante padrão RRF; equilibra contribuições de *retrievers* com *rankings* distintos |
| Candidatos por *retriever* | k×3 | Amplia o conjunto antes da fusão, reduzindo o risco de perder o *chunk* correto |
| Tokenização | *regex* `\W+` | Preserva números e unidades (`kN`, `m²`, `1,5`) como *tokens* relevantes |

### Análise de compromissos

Os resultados comparativos de Recall@k são apresentados na Seção 5.2. A seguir, discutimos os principais compromissos observados.

**Denso** apresentou *recall* muito baixo (0,05–0,20). Após a reorganização das seções da NBR 6120 para a edição 2019 (124 *chunks* com títulos técnicos longos), o BERTimbau não representa bem os novos `chunk_ids` semanticamente. O único acerto consistente foi Q11 (velocidade básica V0), onde a consulta contém os mesmos termos do *chunk*.

**Esparso (BM25)** dominou neste corpus: *recall* 0,75–0,85. A correspondência lexical exata captura termos técnicos normativos (ex.: "cargas variáveis", "garagem", "vento básico", "fator S2") que o denso não consegue mapear semanticamente.

**Híbrido** combina os dois: em k=10 atinge 0,90, o melhor resultado geral. Para k pequeno (3–5), o BM25 sozinho já é superior ao híbrido, pois o denso "contamina" o *ranking* com *chunks* irrelevantes via RRF.

**Latência:**

| Modo | Tempo típico de recuperação | Gargalo |
| :---- | :---- | :---- |
| Esparso | < 1 ms | — |
| Denso | 5–20 ms | Vetorização da consulta (BERTimbau) |
| Híbrido | 5–20 ms | Dominado pela vetorização do denso |

---

## 5. Avaliação

### 5.1 *Golden Set*

O conjunto de avaliação é composto por 21 perguntas cobrindo os dois documentos do corpus:

| Categoria | Quantidade | Descrição |
| :---- | :---- | :---- |
| `factual_direta` | 17 | Pergunta com resposta direta em uma seção |
| `multi_trecho` | 3 | Requer combinar 2–4 seções para responder |
| `fora_do_corpus` | 1 | Testa recusa (pergunta sobre preço de concreto) |

**Distribuição por norma:**

- NBR 6120: 10 perguntas (cargas permanentes, acidentais, tabelas de pesos)
- NBR 6123: 10 perguntas (velocidade do vento, fatores S1/S2/S3, pressão dinâmica, análise dinâmica)
- Fora do corpus: 1 pergunta (teste de recusa)

### 5.2 Recall@k

Executado via `src/evaluator.py` com o índice reconstruído sobre as 290 seções (NBR 6120:2019 + NBR 6123:2023). Das 21 perguntas, 20 são avaliáveis (1 `fora_do_corpus` excluída). Modo denso = BERTimbau + FAISS. Arquivos de detalhe em `index/eval_details.csv`.

| k | Denso (*baseline*) | Esparso (BM25) | Híbrido (RRF) |
| :---- | :---- | :---- | :---- |
| 3 | 0,05 (1/20) | 0,75 (15/20) | 0,45 (9/20) |
| 5 | 0,05 (1/20) | 0,80 (16/20) | 0,55 (11/20) |
| 10 | 0,20 (4/20) | 0,85 (17/20) | 0,90 (18/20) |

Arquivos gerados: `index/recall_at_k_all.json`, `index/eval_comparative.csv`.

**Perguntas com acerto no modo denso (k=10):** Q3 (peso próprio), Q11 (velocidade V0), Q12 (pressão dinâmica), Q20 (análise dinâmica).

**Interpretação:** O BERTimbau apresenta baixo *recall* nas seções da NBR 6120:2019 porque os `chunk_ids` têm títulos técnicos muito específicos que o modelo não representa bem semanticamente. O BM25 supera o denso em todas as configurações de k neste corpus. O híbrido atinge o melhor resultado global em k=10 (0,90), evidenciando o valor da fusão para *pools* maiores de candidatos.

### 5.3 Rubrica Qualitativa

A avaliação qualitativa foi realizada sobre 17 perguntas do *golden set* nos três modos de recuperação (denso / esparso / híbrido), com k=5 e *pipeline* `baseline` usando Groq llama-4-scout-17b como LLM de geração. As questões Q17–Q20 não foram incluídas nesta rubrica por limitações de tempo; os resultados de Recall@k dessas questões constam na Seção 5.2.

**Arquivo de detalhamento completo:** `data/eval/rubrica_detalhada.md` — contém as respostas integrais dos 3 modos e tabela de preenchimento por questão.

**Automação:** a coluna *Faithfulness* foi calculada via **RAGAS** (Groq llama-4-scout como LLM-*judge*). Essa métrica mede o grau em que as afirmações da resposta têm suporte nos trechos recuperados (escala 0–1). Pontuações completas para os 3 modos em `data/eval/ragas_scores.json`.

> **Limitação conhecida do RAGAS para recusas:** quando o *pipeline* responde "Não encontrei informação suficiente", o RAGAS atribui *Faithfulness* ≈ 0 (a expressão de recusa não aparece literalmente nos *chunks*). Isso **não indica alucinação** — indica apenas que a recusa é uma decisão do LLM, não uma inferência extraída dos trechos.

#### Critérios

| Critério | Opções | Pergunta-guia | Preenchimento |
| :---- | :---- | :---- | :---- |
| *Groundedness* | S / N | A resposta está suportada pelos trechos? | Automático (RAGAS) |
| **Correção** | **S / P / N** | Está factualmente correta conforme a norma? | **Manual (Marcelo)** |
| Citações | S / N | Cita trechos adequados e coerentes? | Automático (RAGAS) |
| Alucinação | S / N | Inventou algo fora do corpus? | Automático (RAGAS) |
| **Recusa** | **S / N / N/A** | Quando não havia evidência, recusou corretamente? | **Manual (Marcelo)** |

As colunas **Correção** (S = correta / P = parcial / N = incorreta) e **Recusa** (S = recusa correta / N = deveria ter recusado / N/A = respondeu) foram preenchidas manualmente por Marcelo Carvalho, engenheiro civil do grupo, com base em sua experiência profissional e consulta direta às normas. As demais colunas são derivadas automaticamente do *Faithfulness* RAGAS.

#### Tabela de avaliação — 3 modos (denso / esparso / híbrido)

O detalhamento completo das respostas está em `data/eval/rubrica_detalhada.md`.

| # | Pergunta (resumo) | Cat. | Acerto D/S/H | *Faith.* D / S / H | Correção | Recusa |
| :---- | :---- | :---- | :---: | :---: | :---: | :---: |
| Q1 | Carga acidental em escritório (kN/m²)? | fact | ✗/✗/✗ | 0,00 / 1,00 / 1,00 | N | N/A |
| Q2 | Carga acidental garagem veículos leves? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q3 | Peso próprio = que tipo de carga? | fact | ✗/✓/✓ | 0,50 / 1,00 / 0,67 | S | N/A |
| Q4 | Paredes divisórias sem posição — como tratar? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q5 | Peso específico do concreto armado? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q6 | Carga ao longo de parapeitos e balcões? | fact | ✗/✗/✗ | 1,00 / 0,75 / 1,00 | S | N/A |
| Q7 | Critérios de categoria para garagens? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q8 | Carga mínima em coberturas (manutenção)? | fact | ✗/✓/✓ | 0,00 / 0,86 / 0,83 | N | N/A |
| Q9 | Quando reduzir cargas acidentais? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q10 | Redução percentual — 6 ou mais pisos? | multi | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q11 | Definição da velocidade básica V0? | fact | ✓/✓/✓ | 1,00 / 1,00 / 0,80 | S | N/A |
| Q12 | Pressão dinâmica do vento — definição e cálculo? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q13 | Três fatores S1, S2, S3 para calcular Vk? | multi | ✗/✓/✓ | 0,83 / 1,00 / 0,25 | S | N/A |
| Q14 | O que considera o fator topográfico S1? | fact | ✗/✓/✓ | 0,00 / 1,00 / 1,00 | S | N/A |
| Q15 | O que considera o fator S2? | fact | ✗/✓/✓ | N/D / 1,00 / N/D | S | N/A |
| Q16 | Valor mínimo do fator S3 para residências? | fact | ✗/✓/✓ | 0,00 / 0,67 / 0,67 | S | N/A |
| Q21 | Preço do m³ de concreto para obra em Brasília? | fora | —/—/— | 0,00 / 0,00 / 0,00 ¹ | — | S |

*¹ RAGAS ≈ 0 para recusas por limitação estrutural do método (ver nota acima). Q13 híbrido Faith.=0,25: resposta com baixo grounding — ver Exemplo 3.*

#### Ganho do esparso/híbrido sobre o denso

Para evidenciar o ganho da Trilha A, a tabela abaixo cruza Acerto@5 dos três modos em questões representativas:

| # | Pergunta (resumo) | Acerto D/S/H | *Faith.* Denso | *Faith.* Esparso | *Faith.* Híbrido |
| :---- | :---- | :---: | :---: | :---: | :---: |
| Q2 | Carga garagem veículos leves | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |
| Q3 | Peso próprio = permanente? | ✗/✓/✓ | 0,50 | 1,00 | 0,67 |
| Q5 | Peso específico concreto armado | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |
| Q9 | Redução cargas acidentais — quando? | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |
| Q11 | Velocidade básica V0 | ✓/✓/✓ | 1,00 | 1,00 | 0,80 |
| Q12 | Pressão dinâmica do vento | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |
| Q14 | Fator topográfico S1 | ✗/✓/✓ | 0,00 | 1,00 | 1,00 |

**Síntese:** Os modos esparso e híbrido recuperam o *chunk* correto em 15–16 das 20 questões, contra apenas 1/20 do denso. O *Faithfulness* do esparso é ≈ 1,00 na maioria dos casos, confirmando que, quando o *chunk* certo é recuperado, o LLM gera respostas bem fundamentadas. O híbrido tem *Faithfulness* igualmente alta, com exceção de Q13 (0,25), onde a resposta apresentou baixo *grounding* — ver Exemplo 3.

#### Exemplos notáveis

**Exemplo 1 — Q11: resposta correta nos três modos**

*"Como é definida a velocidade básica do vento V0 pela NBR 6123?"*

> "A velocidade básica do vento, V0, é definida como a velocidade de uma rajada de 3 s, a 10 m acima do terreno, em campo aberto e plano, excedida em média uma vez em 50 anos [NBR6123, Seção 5.1]."

*Faithfulness* = 1,00. A definição reproduz fielmente o § 5.1 da NBR 6123:2023. Única questão onde o denso também acerta — o nome do *chunk* (`51_velocidade_básica_do_vento_v0`) é semanticamente próximo da consulta.

---

**Exemplo 2 — Q2: falha do denso, acerto do esparso**

*"Qual o valor de carga acidental para uma garagem de veículos leves?"*

Denso (sem acerto): *"Não encontrei informação suficiente nas normas consultadas para responder esta pergunta."*

Esparso (acerto): *"[NBR6120, Seção 6.6.1] A carga acidental para garagem de veículos leves é dada pela Tabela 13 da NBR 6120. Considerando veículos leves, a Categoria I é a mais adequada, com as seguintes cargas: Carga uniformemente distribuída: 3 kN/m². Carga concentrada (Qk): 12 kN, atuando em uma região de 10 cm × 10 cm."*

Esse exemplo ilustra o ganho direto do BM25 sobre o denso: a consulta contém "garagem" e "veículos leves", termos que o BM25 associou exatamente ao *chunk* `NBR6120#98_661_ações_em_garagens…`. O BERTimbau não fez essa associação semanticamente.

---

**Exemplo 3 — Q13: resposta parcial com risco de alucinação (denso)**

*"Quais são os três fatores que multiplicam V0 para obter a velocidade característica Vk?"*

Denso (*Faithfulness* = 0,83): *"…S2 é confirmado como um dos fatores. S1 e S3 são mencionados implicitamente como necessários para calcular Vk, mas seus valores ou como são obtidos não estão detalhados na seção A.1 fornecida. (…) SOMENTE S2 é apresentado [NBR6123, Seção A.1 Fator S2]."*

O LLM menciona a fórmula `Vk = S1·S2·S3·V0` sem encontrá-la nos *chunks* — potencial alucinação parcial. O esparso (acerto, *Faithfulness* = 1,00) recupera os *chunks* de S1, S2 e S3 e responde com precisão.

---

**Exemplo 4 — Q21: recusa correta**

*"Como calcular o preço do m³ de concreto para uma obra em Brasília?"*

> "Não encontrei informação suficiente nas normas consultadas para responder esta pergunta. (A consulta está limitada a normas técnicas ABNT, e a pergunta envolve tema não normativo, especificamente relacionado a preços e orçamentos.)"

Recusa correta e bem justificada — o corpus cobre apenas normas de cargas e vento, não precificação. O LLM ainda acrescentou a razão da recusa, o que é um comportamento desejável de *grounding*.

---

## 6. Limitações e Próximos Passos

### Limitações

**Corpus limitado:** O corpus cobre cargas permanentes, acidentais e forças de vento, mas deixa de fora normas importantes do projeto estrutural (NBR 6118 — concreto, NBR 7190 — madeira, NBR 8800 — aço). A NBR 6118 foi excluída por problemas de codificação no PDF disponível.

**Segmentação sem sobreposição:** Algumas respostas requerem informação distribuída entre o final de uma seção e o início de outra. Com sobreposição zero, o *retriever* pode não recuperar os dois *chunks* simultaneamente. Esse efeito é parcialmente mitigado pelo *retriever* híbrido (k×3 candidatos).

**Seções muito grandes:** A seção 6.2 (Cargas variáveis) da NBR 6120:2019 e algumas seções da NBR 6123 têm mais de 20.000 caracteres, acima do que modelos de *embedding* conseguem representar fielmente em um único vetor (limite típico: ~512 *tokens*). Em versões futuras, seria recomendável subdividir essas seções.

**Fórmulas não decodificadas:** O Docling converte fórmulas matemáticas para `<!-- formula-not-decoded -->` quando não consegue renderizá-las. Isso afeta algumas seções da NBR 6123 que contêm equações.

**Dependência de API externa:** A geração de respostas depende de APIs de LLM (Groq/Gemini). Para uso totalmente local, seria necessário integrar um modelo via `llama.cpp` ou Ollama.

### Próximos Passos

**Ampliação do corpus:** Incluir a NBR 6118 (projeto de estruturas de concreto) quando um PDF com codificação correta estiver disponível, além de outras normas complementares como NBR 7190 (madeira) e NBR 8800 (aço). Isso permitiria ao sistema cobrir o ciclo completo de dimensionamento estrutural.

**Subdivisão de seções extensas:** Implementar uma etapa de pós-processamento que subdivida automaticamente seções com mais de ~4.000 caracteres, preservando os metadados da seção original. Isso melhoraria a representação vetorial no *retriever* denso e potencialmente elevaria o *recall* do modo híbrido.

**Ajuste fino do modelo de *embeddings*:** Realizar *fine-tuning* do BERTimbau (ou de um modelo *sentence-transformer*) no domínio normativo, utilizando pares pergunta–seção extraídos do *golden set* ampliado. O *recall* extremamente baixo do denso (0,05 em k=3) sugere que a representação semântica genérica é insuficiente para este vocabulário técnico.

**Execução totalmente local:** Integrar um modelo de geração local (ex.: Ollama com Llama 3) para eliminar a dependência de APIs externas, viabilizando o uso do sistema em ambientes sem acesso à internet ou com restrições de confidencialidade.

---

## 7. Referências

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. *NBR 6118: Projeto de estruturas de concreto — Procedimento*. Rio de Janeiro: ABNT, 2023.

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. *NBR 6120: Cargas para o cálculo de estruturas de edificações*. 2. ed. Rio de Janeiro: ABNT, 2019.

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. *NBR 6123: Forças devidas ao vento em edificações*. Rio de Janeiro: ABNT, 2023.

BROWN, Dorian. *rank-bm25: A collection of BM25 algorithms in Python*. GitHub. Disponível em: [https://github.com/dorianbrown/rank_bm25](https://github.com/dorianbrown/rank_bm25). Acesso em: 3 abr. 2026.

ES, Shahul et al. *RAGAS documentation*. Disponível em: [https://docs.ragas.io](https://docs.ragas.io). Acesso em: 3 abr. 2026.

GRADIO. *Gradio documentation*. Disponível em: [https://www.gradio.app/docs](https://www.gradio.app/docs). Acesso em: 3 abr. 2026.

GROQ. *Groq API documentation*. Disponível em: [https://console.groq.com/docs](https://console.groq.com/docs). Acesso em: 3 abr. 2026.

HUGGING FACE. *Transformers documentation*. Disponível em: [https://huggingface.co/docs/transformers](https://huggingface.co/docs/transformers). Acesso em: 3 abr. 2026.

IBM RESEARCH. *Docling: document processing toolkit for generative AI pipelines*. GitHub, 2024. Disponível em: [https://github.com/DS4SD/docling](https://github.com/DS4SD/docling). Acesso em: 3 abr. 2026.

META AI. *FAISS: A library for efficient similarity search and clustering of dense vectors*. GitHub. Disponível em: [https://github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss). Acesso em: 3 abr. 2026.

TEIXEIRA, Israel Magalhães; BRAGA, Eduardo; CARVALHO, Marcelo. *pln-rag-normas-estruturais: Chatbot RAG para normas estruturais ABNT*. GitHub, 2026. Disponível em: [https://github.com/israelmteixeira1/pln-rag-normas-estruturais](https://github.com/israelmteixeira1/pln-rag-normas-estruturais). Acesso em: 3 abr. 2026.
