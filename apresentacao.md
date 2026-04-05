---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 22px;
    padding: 40px 60px;
  }
  h1 { color: #1a3a5c; font-size: 2em; }
  h2 { color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: 6px; }
  h3 { color: #2e6da4; }
  .highlight { background: #e8f0fe; border-left: 4px solid #2e6da4; padding: 8px 16px; margin: 8px 0; }
  table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
  th { background: #1a3a5c; color: white; padding: 6px 10px; }
  td { padding: 5px 10px; border: 1px solid #ccc; }
  tr:nth-child(even) { background: #f0f4f8; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; }
  section.title { background: #1a3a5c; color: white; }
  section.title h1 { color: white; font-size: 1.8em; }
  section.title h2 { color: #a8c8f0; border-color: #a8c8f0; }
  section.title p { color: #d0e4f7; }
  footer { font-size: 0.7em; color: #888; }
---

<!-- _class: title -->

# Chatbot RAG para Normas Estruturais ABNT

## Recuperação Híbrida: Dense + Sparse + RRF

**Eduardo Braga · Israel Magalhães · Marcelo Carvalho**
Processamento de Linguagem Natural — IFG Pós-IA

---

## O Problema

**Pergunta:** "Qual a carga acidental para garagem de veículos leves?"

- LLMs generativos alucinam ou ficam desatualizados
- Normas ABNT são periodicamente revisadas
- Valores numéricos errados = **consequências graves na engenharia**

<br>

### Solução: RAG — Retrieval-Augmented Generation

> A resposta sempre vem ancorada em um trecho **real e rastreável** da norma.

---

## Corpus: Normas ABNT

| Norma        | Título                                 | Edição        | Seções |
| ------------ | -------------------------------------- | ------------- | ------ |
| **NBR 6120** | Cargas para cálculo de estruturas      | 2019 (2ª ed.) | 124    |
| **NBR 6123** | Forças devidas ao vento em edificações | 2023          | 166    |

**Total: 290 seções · ~626 mil caracteres**

<br>

> **NBR 6118** (concreto) foi removida: PDF com encoding corrompido geraria chunks de baixa qualidade e potencial desinformação.

---

## Arquitetura do Pipeline

```
Pergunta do usuário
      │
      ▼
┌─────────────────────────────────┐
│        RETRIEVER HÍBRIDO        │
│  Dense (BERTimbau) + BM25  →  RRF  │
└─────────────────────────────────┘
      │  top-k chunks
      ▼
┌─────────────────────────────────┐
│     PROMPT com contexto         │
│  "Responda SOMENTE com base     │
│   nos trechos fornecidos"       │
└─────────────────────────────────┘
      │
      ▼
  LLM (Groq llama-3.3-70b)
      │
      ▼
Resposta com citação [NBR6120, §2.2]
```

---

## Chunking: 1 seção = 1 chunk

**Processo:**

1. PDF → Markdown via **Docling** (preserva tabelas, listas, headings)
2. Markdown → split por `##` (heading nível 2)
3. Frontmatter YAML automático por chunk

**Metadados por chunk:**
`chunk_id` · `doc_id` · `secao` · `summary` · `texto` · `n_chars`

<br>

**Decisões de design:**

- **Zero overlap** — seções são unidades semânticas completas
- Tabelas extensas divididas em continuação (`tabela_10_conclusão`)
- Rastreabilidade total: toda resposta tem `chunk_id` de origem

---

## Retriever Dense: BERTimbau + FAISS

**Embeddings:**

- Modelo: **BERTimbau** (BERT pré-treinado em português)
- Dimensão: 768 · Sem GPU · Sem API externa

**Índice:**

- `FAISS IndexFlatIP` — busca exata por similaridade de cosseno
- 290 chunks → busca exata é trivial computacionalmente

<br>

> Captura **semântica e paráfrases**, mas falha em termos técnicos muito específicos não vistos no pré-treino (`kN/m²`, `§ 2.2.1.6`)

---

## Retriever Esparso: BM25

- Algoritmo clássico de relevância léxica (TF-IDF com normalização por comprimento)
- Tokenização por **regex alfanumérico** — preserva números e unidades como tokens

<br>

**Por que BM25?**

| Consulta                         | Dense               | BM25          |
| -------------------------------- | ------------------- | ------------- |
| "carga acidental em escritório"  | ✓ semântica         | ✓ léxico      |
| "3 kN/m² garagem veículos leves" | ✗ não viu no treino | ✓ match exato |
| `§ 4.2.1.6`                      | ✗                   | ✓ token exato |

---

## Retrieval Híbrido com RRF

**Reciprocal Rank Fusion** — funde os dois rankings sem parâmetros de tuning:

$$\text{score}_{RRF}(d) = \sum_{r \in \{dense, sparse\}} \frac{1}{60 + rank_r(d)}$$

**Processo:**

1. Cada retriever recupera `k × 3` candidatos (pool ampliado)
2. Fusão via RRF
3. Deduplicação por `chunk_id` — cada chunk conta uma vez
4. Retorna top-k da fusão

> O `60` é a constante padrão da literatura — balanceia contribuições de ranks altos e baixos.

---

## Avaliação: Recall@k

**Golden set:** 21 perguntas (17 factuais · 3 multi-trecho · 1 fora do corpus)

|   k    | Dense | Sparse | **Hybrid** |
| :----: | :---: | :----: | :--------: |
|   3    | 0,05  |  0,75  |    0,45    |
|   5    | 0,05  |  0,80  |    0,55    |
| **10** | 0,20  |  0,85  |  **0,90**  |

<br>

**Dense** — recall muito baixo: títulos técnicos específicos não representados pelo BERTimbau
**Sparse** — domina em k pequeno: correspondência léxica excelente neste corpus
**Hybrid** — melhor em k=10: **0,90**, supera ambos os modos individuais

---

## Exemplo Concreto

**Pergunta:** "Qual a carga acidental para garagem de veículos leves?"

| Modo       | Resultado                                                                                     |
| ---------- | --------------------------------------------------------------------------------------------- |
| Dense      | Não encontrou chunk relevante                                                                 |
| **Sparse** | **"Carga uniformemente distribuída: 3 kN/m²** · Carga concentrada: 12 kN" — NBR6120, §correto |
| Hybrid@10  | Acertou também (junto com outros chunks relevantes)                                           |

> O BM25 casou exatamente `garagem` + `veículos leves` com o chunk da NBR 6120.

**Teste de recusa (Q21):** "Qual o preço do m³ de concreto?" → sistema recusou corretamente: _"Esta informação não está presente no corpus."_

---

## Trade-offs e Latência

| Modo       | Ponto forte                 | Limitação             | Latência |
| ---------- | --------------------------- | --------------------- | -------- |
| Dense      | Paráfrases, sinônimos       | Termos técnicos novos | 5–20 ms  |
| Sparse     | Valores, referências exatas | Sem semântica         | < 1 ms   |
| **Hybrid** | **Robustez geral**          | Leve overhead         | 5–20 ms  |

<br>

**Recomendação:** Hybrid para produção — captura ambos os casos e em k=10 supera os modos individuais.

---

## Interface Gradio

- Usuário digita pergunta, escolhe modo (`dense` / `sparse` / `hybrid`) e define k
- Exibe resposta com trechos recuperados, `chunk_id` e score
- `demo.launch(share=True)` gera URL pública no Colab

---

## Conclusão

**O que construímos:**

- Pipeline RAG funcional com 290 seções normativas
- 3 modos de retrieval com avaliação quantitativa (Recall@k)
- Comportamento de recusa para perguntas fora do corpus

**Principal aprendizado:**

> Para documentos técnicos com terminologia precisa e valores numéricos, BM25 superou embeddings com BERTimbal neste caso. O híbrido com RRF foi a escolha mais robusta testada.

**Limitações:** corpus restrito · fórmulas não decodificadas pelo Docling

**Próximos passos que pensamos experimentar:** incluir NBR 6118 · subdividir seções longas
