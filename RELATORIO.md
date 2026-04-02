# Relatório — Chatbot RAG para Normas Estruturais ABNT

**Grupo:** Eduardo Braga · Israel Magalhães · Marcelo Carvalho  
**Disciplina:** Processamento de Linguagem Natural — IFG Pós-IA  
**Trilha:** A — Recuperação Híbrida (Sparse + Dense)

---

## 1. Domínio e Corpus

O sistema foi desenvolvido para auxiliar engenheiros, projetistas e estudantes na consulta a normas técnicas brasileiras de engenharia estrutural. O corpus é formado por documentos da ABNT — textos de alta precisão terminológica, com tabelas de valores e fórmulas específicas, onde uma resposta incorreta pode ter consequências práticas sérias.

Esse domínio justifica o uso de RAG em detrimento de um LLM direto por três razões principais: normas são revisadas periodicamente (a NBR 6120 teve sua segunda edição em 2019, substituindo a de 1980); os valores numéricos e coeficientes precisam ser exatos e rastreáveis; e qualquer citação deve referenciar a seção normativa de origem.

### Corpus

| Norma | Título | Edição | Seções |
|---|---|---|---|
| **NBR 6120** | Cargas para o cálculo de estruturas de edificações | 2019 (2ª edição) | 124 |
| **NBR 6123** | Forças devidas ao vento em edificações | 2023 | 166 |

**Total:** 290 seções · ~626 mil caracteres

Juntas, as duas normas cobrem as principais ações externas no dimensionamento estrutural brasileiro: cargas permanentes, cargas acidentais de uso e forças de vento. A NBR 6118 (estruturas de concreto) foi inicialmente cogitada mas excluída porque o PDF disponível apresenta encoding corrompido em partes significativas, o que comprometeria a qualidade dos chunks gerados.

---

## 2. Chunking

### Estratégia: uma seção normativa por chunk

Cada chunk corresponde a uma seção semântica da norma — uma subseção, uma tabela ou um grupo de parágrafos relacionados. A divisão segue dois passos:

1. **PDF → Markdown** via [Docling](https://github.com/DS4SD/docling), que preserva headings, tabelas e listas com fidelidade ao documento original.
2. **Markdown → seções** via `scripts/split_sections_auto.py`, que divide o texto a cada heading de nível 2 (`##`).

Cada arquivo de seção recebe um frontmatter YAML com os metadados que depois identificam o chunk no índice:

| Campo | Valor típico |
|---|---|
| `chunk_id` | `NBR6120#91_62_cargas_variáveis` |
| `doc_id` | `NBR6120` ou `NBR6123` |
| `edicao` | `2019 (2ª edição)` ou `2023` |
| `secao` | Título da seção (ex.: "6.2 Cargas variáveis") |
| `summary` | Primeira sentença não-vazia do conteúdo |

### Tamanho dos chunks

| | NBR 6120 | NBR 6123 |
|---|---|---|
| Mínimo | ~130 caracteres | ~6 caracteres |
| Máximo | ~40.000 caracteres | ~65.000 caracteres |
| Mediana | ~500 caracteres | ~500 caracteres |

### Decisões de projeto

**Tabelas extensas.** Tabelas muito longas (Tabela 1 de pesos específicos, Tabela 10 de cargas variáveis) ficam divididas em seções de continuação geradas automaticamente (`tabela_10_continuação`, `tabela_10_conclusão`). Isso as torna recuperáveis de forma independente sem diluir o conteúdo narrativo do chunk principal.

**Sem overlap.** A estrutura hierárquica das normas já garante que cada seção seja uma unidade semântica completa. Overlap introduziria duplicatas no índice sem ganho de cobertura.

**Seções muito pequenas.** Headings isolados (e.g., "3.1") geram chunks com menos de 20 caracteres. Eles são mantidos no índice mas praticamente nunca aparecem entre os top-k resultados, por isso não prejudicam a qualidade do retrieval.

---

## 3. Pipeline RAG (Baseline)

### Retriever e índice

O retriever denso utiliza o modelo `neuralmind/bert-base-portuguese-cased` (BERTimbau, dimensão 768), pré-treinado em português e adequado ao vocabulário técnico da ABNT. A escolha elimina dependência de API externa para geração de embeddings e permite execução em CPU no Google Colab.

O índice é um `FAISS IndexFlatIP` com vetores L2-normalizados, o que equivale a busca exata por similaridade de cosseno. Com 290 chunks, a busca exata é computacionalmente trivial. O parâmetro k é configurável em 3, 5 ou 10.

### Prompt e grounding

O sistema usa dois templates de prompt, ambos em `src/prompts.py`:

**Modo baseline** — instrução direta:

```
REGRAS OBRIGATÓRIAS:
1. Responda APENAS com base nos trechos normativos fornecidos.
2. Cite as fontes usando o formato [NBRxxxx, Seção Y.Y].
3. Se a informação NÃO estiver nos trechos: "Não encontrei informação
   suficiente nas normas consultadas para responder esta pergunta."
4. NÃO invente, extrapole ou use conhecimento externo às normas.
```

**Modo melhorado** — adiciona chain-of-thought explícito (identificar → verificar → cruzar referências → confirmar suporte) e formato estruturado de saída (resposta objetiva → detalhamento → lista de referências).

### Citações e recusa

Cada resposta inclui referências no formato `[NBR6120, Seção 6.2]`. A interface Gradio exibe os trechos recuperados com o `chunk_id`, o score de relevância e o texto completo, permitindo verificar a cadeia de evidências.

A recusa é ativada quando nenhum trecho recuperado suporta a resposta, ou quando a pergunta é sobre tema fora do corpus (preços, marcas, recomendações de projeto não normativas). A frase canônica é: *"Não encontrei informação suficiente nas normas consultadas para responder esta pergunta."*

**LLM de geração:** Groq (`llama-3.3-70b-versatile`), com fallback para Google Gemini ou NVIDIA NIM.

---

## 4. Trilha A — Recuperação Híbrida

### Motivação

O retriever denso captura relações semânticas bem, mas pode falhar quando a consulta usa termos muito específicos ausentes do pré-treino: valores numéricos (`3 kN/m²`), referências a parágrafos (`§ 6.3`) ou nomes de materiais (`granito`, `concreto armado`). O BM25, por outro lado, lida bem com termos exatos mas é cego a sinônimos e paráfrases. A recuperação híbrida combina as vantagens dos dois.

### Implementação

O módulo `src/hybrid_search.py` implementa dois retrievers adicionais ao baseline:

**SparseRetriever (BM25Okapi):** tokenização por regex alfanumérico em lowercase (sem stemming), o que preserva números e unidades (`kN`, `m²`, `1,5`) como tokens relevantes.

**HybridRetriever (BM25 + FAISS + RRF):** cada retriever contribui com `min(k×3, n_chunks)` candidatos, que são fundidos via *Reciprocal Rank Fusion*:

$$\text{score}(c) = \sum_{\text{retriever}} \frac{1}{60 + \text{rank}(c)}$$

A constante 60 é o valor padrão da literatura de RRF. Após a fusão, os chunks são deduplicados por `chunk_id` e os top-k são retornados.

| Parâmetro | Valor | Justificativa |
|---|---|---|
| k_RRF | 60 | Constante padrão — equilibra retrievers com distribuições de ranking distintas |
| Candidatos por retriever | k × 3 | Amplia o pool antes da fusão para reduzir falsos negativos |
| Tokenização | regex `\W+` | Preserva unidades técnicas como tokens individuais |

### Análise de trade-offs

**Dense** se destaca em consultas semânticas: "peso próprio da estrutura" recupera a seção de ações permanentes mesmo sem sobreposição lexical exata.

**Sparse** se destaca quando a consulta contém termos muito específicos: valores numéricos exatos (`25 kN/m³`), referências de seção (`§ 6.12`) ou nomes de materiais.

**Hybrid** tende a igualar ou superar ambos, especialmente em perguntas que exigem cruzar uma seção narrativa com uma tabela — casos onde os dois retrievers recuperam chunks complementares.

**Latência:**

| Modo | Retrieval típico | Gargalo |
|---|---|---|
| Sparse (BM25) | < 1 ms | — |
| Dense (FAISS) | 5–20 ms | Encoding da query pelo BERTimbau |
| Hybrid (RRF) | 5–20 ms | Dominado pelo encoding dense |

---

## 5. Avaliação

### 5.1 Golden Set

O golden set contém 21 perguntas que cobrem os dois documentos do corpus:

| Categoria | Qtd. | Descrição |
|---|---|---|
| `factual_direta` | 17 | Resposta direta em uma única seção |
| `multi_trecho` | 3 | Requer combinar 2 ou mais seções |
| `fora_do_corpus` | 1 | Testa recusa (pergunta sobre preço de concreto) |

As 20 perguntas com evidência definida são usadas no cálculo de Recall@k. A pergunta fora do corpus é excluída dessa métrica e avaliada apenas pela rubrica qualitativa (critério de recusa).

### 5.2 Recall@k — Comparativo por modo de retrieval

> **Marcelo:** preencha com os valores impressos pela célula 8.2 do notebook
> (`print_comparative_report(comp_results)`). Use o formato `0,XX` (ex.: `0,75`).

| k | Dense (baseline) | Sparse (BM25) | Hybrid (RRF) |
|---|---|---|---|
| 3 | | | |
| 5 | | | |
| 10 | | | |

*(20 perguntas avaliáveis — pergunta fora do corpus excluída)*

**Destaque:** *(após preencher a tabela, descreva aqui em 2–3 linhas em qual k o híbrido mais ganhou sobre o baseline e se houve caso em que o sparse superou o dense)*

### 5.3 Rubrica Qualitativa

> **Marcelo:** para cada pergunta abaixo, execute a consulta no chatbot (modo dense, k=5)
> e preencha os scores conforme a escala. Para a pergunta #21, o único critério relevante é
> **Recusa** — os demais ficam N/A.
>
> **Escala:**
> - **Groundedness** — 0 = resposta não suportada pelos trechos; 1 = parcialmente suportada; 2 = totalmente suportada pelos trechos recuperados
> - **Correção** — 0 = incorreta conforme a norma; 1 = parcialmente correta; 2 = correta
> - **Citações** — 0 = ausentes ou erradas; 1 = presentes mas incompletas; 2 = adequadas e precisas
> - **Alucinação** — 0 = inventou algo fora do corpus; 1 = não inventou
> - **Recusa** — 0 = deveria recusar e não recusou; 1 = recusou corretamente; N/A = pergunta tem resposta no corpus

| # | Pergunta | G | C | Cit | Al | R |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | Qual o valor típico de carga acidental para um pavimento de escritório? | | | | | N/A |
| 2 | Qual o valor de carga acidental para uma garagem de veículos leves? | | | | | N/A |
| 3 | O peso próprio da estrutura deve ser considerado como que tipo de carga? | | | | | N/A |
| 4 | Como tratar paredes divisórias cuja posição não é definida no projeto? | | | | | N/A |
| 5 | Qual o peso específico do concreto armado? | | | | | N/A |
| 6 | Qual a carga que deve ser considerada ao longo de parapeitos e balcões? | | | | | N/A |
| 7 | Quais critérios determinam a categoria de projeto para garagens e áreas de circulação de veículos? | | | | | N/A |
| 8 | Qual a carga variável mínima a considerar em coberturas com acesso apenas para manutenção? | | | | | N/A |
| 9 | Quando é permitido reduzir as cargas acidentais em um edifício? | | | | | N/A |
| 10 | Qual a redução percentual de cargas acidentais quando há 6 ou mais pisos? | | | | | N/A |
| 11 | Como é definida a velocidade básica do vento V₀ pela NBR 6123? | | | | | N/A |
| 12 | O que é a pressão dinâmica do vento e como é calculada? | | | | | N/A |
| 13 | Quais são os três fatores que multiplicam V₀ para obter a velocidade característica Vk? | | | | | N/A |
| 14 | O que considera o fator topográfico S1 no cálculo do vento? | | | | | N/A |
| 15 | O que considera o fator S2 no cálculo da velocidade do vento? | | | | | N/A |
| 16 | Para uma residência normal, qual o valor mínimo do fator estatístico S3? | | | | | N/A |
| 17 | O que são sobrepressão e sucção no contexto dos coeficientes de pressão do vento? | | | | | N/A |
| 18 | Como é considerada a pressão interna do vento em edificações com aberturas? | | | | | N/A |
| 19 | Em que situações a NBR 6123 indica o uso de ensaios em túnel de vento? | | | | | N/A |
| 20 | Quando estruturas altas e esbeltas precisam considerar análise dinâmica além da análise estática? | | | | | N/A |
| 21 | Como calcular o preço do m³ de concreto para uma obra em Brasília? | N/A | N/A | N/A | N/A | |

*(G = Groundedness · C = Correção · Cit = Citações · Al = Alucinação · R = Recusa)*

**Exemplos de respostas avaliadas**

> **Marcelo:** escolha 2 ou 3 respostas representativas (uma boa, uma com limitação, e
> a de recusa #21) e transcreva abaixo o texto gerado pelo chatbot com seus comentários.
> Isso demonstra a aplicação concreta da rubrica.

---

**Exemplo 1 — pergunta #___ ("___________________________")**

> *[cole aqui a resposta gerada pelo chatbot]*

Avaliação: *(comente brevemente por que deu os scores que deu)*

---

**Exemplo 2 — pergunta #___ ("___________________________")**

> *[cole aqui a resposta gerada pelo chatbot]*

Avaliação: *(comente brevemente)*

---

**Exemplo 3 — pergunta #21 (recusa)**

> *[cole aqui a resposta gerada pelo chatbot]*

Avaliação: *(o chatbot recusou corretamente? A frase usada foi adequada?)*

---

## 6. Limitações e Próximos Passos

### Limitações

**Corpus restrito.** O corpus cobre cargas permanentes, acidentais e forças de vento, mas deixa de fora normas essenciais para o projeto estrutural completo — NBR 6118 (concreto), NBR 7190 (madeira), NBR 8800 (aço). A NBR 6118 foi excluída por problemas de encoding no PDF disponível.

**Seções muito longas.** As seções `6.2 Cargas variáveis` (NBR 6120) e algumas da NBR 6123 ultrapassam 20.000 caracteres — acima do limite prático de representação fiel por um único vetor de embedding (~512 tokens). Isso pode reduzir a precisão do retrieval denso nessas seções.

**Fórmulas não decodificadas.** O Docling converte equações matemáticas para `<!-- formula-not-decoded -->` quando não consegue renderizá-las, afetando seções da NBR 6123 com equações de pressão dinâmica e fatores S1/S2.

**Dependência de API externa.** A geração de respostas depende de APIs de LLM (Groq/Gemini). Para uso totalmente local e offline, seria necessário integrar um modelo como `llama.cpp` ou Ollama.

### Próximos Passos

1. **Incluir NBR 6118** quando um PDF com encoding correto estiver disponível.
2. **Subdividir seções longas** (> 2.000 caracteres) para melhorar a qualidade dos embeddings.
3. **Reranking** (Trilha B) como camada adicional sobre o retriever híbrido.
4. **Avaliação com RAGAS** para automatizar parte da rubrica qualitativa.
5. **Interface standalone** (FastAPI ou Streamlit) desacoplada do notebook Jupyter.
