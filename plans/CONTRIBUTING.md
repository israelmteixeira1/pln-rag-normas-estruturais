# 🧩 Trilha I — Ingestão, Corpus Normativo e Indexação

Responsável por transformar as normas em dados estruturados e recuperáveis.

### 🎯 Foco no corpus de normas estruturais

* Coleta das normas e materiais auxiliares (ex.: guias, comentários técnicos permitidos).
* Padronização de metadados por documento:

  * doc_id, título, fonte (ABNT), data/edição, tipo (“norma”, “comentário”, “tabela”).
* Estruturação por **capítulo → seção → item → tabela/figura** (quando aplicável).

### 🔧 Chunking orientado a normas

* Segmentação respeitando a hierarquia normativa (ex.: item 13.2.4).
* Estratégia para **tabelas e valores normativos** (manter contexto mínimo).
* Definição de tamanho/overlap com justificativa.

### 🧠 Indexação e Retrieval Base

* Embeddings + índice vetorial.
* Top-k configurável (3, 5, 10).
* Log com identificadores de norma + item (ex.: NBR6118#13.2.4).

### ♻️ Reprodutibilidade

* Pipeline ingestão → chunking → indexação.
* Script para reconstruir o índice a partir das normas.

👉 Essa trilha garante que o conhecimento técnico esteja **corretamente estruturado** para consulta.

---

# 🤖 Trilha E — Pipeline RAG e Comportamento do Chatbot Técnico

Responsável por como o sistema responde perguntas de engenharia.

### 🧱 Pipeline RAG com grounding forte

* Prompt que obriga resposta **apenas com base nas normas**.
* Citações normativas no formato:

  * [NBRxxxx#item.seção]
* Política de recusa para perguntas fora do corpus ou de projeto estrutural aplicado.

### 💬 Interface técnica

* Entrada de perguntas típicas de engenharia estrutural.
* Exibição dos trechos normativos recuperados.
* Alternância baseline vs melhoria.

### 🚀 Implementação da trilha de melhoria escolhida

(Ex.: Prompt Engineering avançado ou Reranking, que funcionam muito bem com normas.)

* Comparação baseline vs melhoria.
* Registro de latência e mudanças de comportamento.

👉 Essa trilha garante **respostas tecnicamente rastreáveis** e bem fundamentadas.

---

# 📊 Trilha M — Especialista de Domínio + Avaliação Científica

Agora é a trilha mais ligada ao **conteúdo de Engenharia Estrutural**.

### 🏗️ Curadoria técnica do corpus

* Validação de relevância das partes das normas para o domínio escolhido.
* Definição de **perguntas típicas de engenharia estrutural** que o chatbot deve responder.
* Garantia de consistência terminológica (ex.: ações, combinações, estados-limite).

### 🎯 Construção do Golden Set (com expertise de engenharia)

* ~20 perguntas reais de prática técnica, como:

  * interpretação de itens normativos
  * leitura de tabelas
  * combinação de requisitos entre normas
  * perguntas fora do escopo normativo
* Definição dos **chunks normativos esperados** como evidência.

### 📏 Avaliação quantitativa e qualitativa

* Recall@k (3, 5, 10) com base nos itens corretos da norma.
* Rubrica técnica:

  * aderência normativa (groundedness)
  * correção técnica
  * precisão das citações
  * ausência de extrapolação não normativa
  * recusa adequada

### 🧪 Análise técnica dos resultados

* Exemplos comentados (por que a resposta está correta/insuficiente).
* Trade-offs práticos (precisão vs latência).
* Limitações do sistema frente à interpretação normativa.

### 📄 Relatório com ênfase no domínio

* Descrição do corpus normativo.
* Justificativas técnicas de chunking e avaliação.
* Discussão de aplicabilidade em engenharia estrutural.

👉 Essa trilha garante que o sistema seja **tecnicamente válido no domínio** e não apenas funcional.


# 🔗 Fluxo de trabalho recomendado

1️⃣ M define perguntas técnicas e valida corpus normativo
2️⃣ I estrutura e indexa as normas
3️⃣ E implementa RAG e melhoria
4️⃣ M avalia tecnicamente as respostas
5️⃣ E ajusta → M valida ganho
6️⃣ M lidera a redação técnica do relatório