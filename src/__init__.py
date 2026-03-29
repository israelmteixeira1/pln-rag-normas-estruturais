"""
RAG Normas Estruturais
======================
Pacote de ingestão, chunking, indexação, pipeline RAG e avaliação
do corpus normativo de engenharia estrutural.

Módulos — Trilha I (Ingestão e Indexação)
-----------------------------------------
- ingestion     : extração de texto e metadados dos PDFs
- chunker       : segmentação hierárquica dos documentos
- indexer       : embeddings e índice FAISS
- evaluator     : cálculo de Recall@k via golden_set.json

Módulos — Trilha E (Pipeline RAG)
----------------------------------
- prompts       : templates de prompt com grounding normativo
- rag_pipeline  : pipeline RAG completo (retriever + Gemini)
- hybrid_search : retriever híbrido BM25+FAISS via Reciprocal Rank Fusion
"""
