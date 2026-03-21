# 🚦 Fluxo recomendado de execução

## 🥇 Fase 1 — Definição técnica do domínio (liderança: M, apoio: I)

Objetivo: garantir que o corpus normativo faça sentido **antes** de codar.

**Passos**

1. Delimitar escopo nas normas:

   * NBR 6118 (estruturas de concreto)
   * NBR 6120 (ações permanentes e variáveis)
   * NBR 6123 (ações do vento)
2. Definir tipos de perguntas reais (interpretação de itens, leitura de tabelas, combinações entre normas, fora do corpus).
3. Definir **formato de citação normativa** (ex.: `[NBR6118#13.2.4]`).
4. Selecionar partes prioritárias (capítulos/itens mais consultados).

**Entregáveis**

* Escopo do corpus + padrões de citação.
* Lista inicial de ~10 perguntas-alvo (rascunho do golden set).

👉 Por que primeiro? Porque a estratégia de chunking depende da estrutura normativa.

---

## 🥈 Fase 2 — Corpus, chunking e índice (liderança: I, validação: M)

Objetivo: transformar as normas em unidades recuperáveis e rastreáveis.

**Passos**

1. Ingestão com metadados (doc_id, título, fonte, edição, tipo).
2. Chunking **hierárquico** (capítulo → seção → item; cuidado com tabelas).
3. Geração de embeddings e criação do índice vetorial.
4. Retriever baseline com top-k configurável (3, 5, 10) + logs de IDs.

**Validação de domínio (M)**

* Conferir se os chunks preservam contexto técnico.
* Checar se valores de tabelas não perderam unidade/condição.

**Entregáveis**

* Scripts reprodutíveis de ingestão e indexação.
* Índice pronto + exemplos de consultas e chunks recuperados.

---

## 🥉 Fase 3 — Pipeline RAG funcional (liderança: E)

Objetivo: chatbot que responde **apenas com base nas normas** e cita corretamente.

**Passos**

1. Montagem do prompt com grounding explícito.
2. Geração de resposta + citações `[NBRxxxx#item]`.
3. Política de recusa (“não encontrei na base”).
4. Interface simples (CLI/Streamlit/Gradio) com opção de ver trechos recuperados.

**Entregáveis**

* Baseline RAG rodando ponta a ponta.
* Demonstração com 5 perguntas técnicas.

---

## 🧪 Fase 4 — Golden set e avaliação baseline (liderança: M, apoio: E)

Objetivo: medir antes de melhorar.

**Passos**

1. Construir ~20 perguntas balanceadas (factual, multi-trecho, fora do corpus).
2. Definir evidência esperada (chunks normativos corretos).
3. Rodar Recall@k (3, 5, 10) do retriever.
4. Aplicar rubrica qualitativa (groundedness, correção técnica, citações, recusa).

**Entregáveis**

* Scripts de avaliação.
* Tabela de resultados do baseline + exemplos comentados.

---

## 🚀 Fase 5 — Implementar a trilha de melhoria (liderança: E, validação: M)

Objetivo: mostrar ganho mensurável sobre o baseline.

**Passos**

1. Implementar a trilha escolhida (ex.: Prompt Engineering avançado ou Reranking).
2. Reexecutar o golden set.
3. Comparar métricas e exemplos (qualidade vs latência).

**Entregáveis**

* Modo baseline vs melhoria.
* Evidência de ganho com métricas/rubrica.

---

## 📊 Fase 6 — Consolidação e relatório (liderança: M, apoio: I e E)

Objetivo: transformar o trabalho em narrativa científica reprodutível.

**Passos**

1. Descrever corpus e decisões de chunking.
2. Documentar arquitetura RAG e trilha escolhida.
3. Apresentar resultados e limitações.
4. Preparar demo com perguntas técnicas.

**Entregáveis**

* Relatório final.
* README com instruções completas.
* Roteiro da apresentação.

---

# 🔗 Dependências entre trilhas (quem espera quem)

* **I depende de M** para saber como segmentar normas corretamente.
* **E depende de I** para ter índice e logs estáveis.
* **M depende de E** para rodar avaliações e comparar melhorias.

Fluxo resumido:
**M define → I estrutura → E integra → M avalia → E melhora → M conclui**