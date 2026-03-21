"""
RAG Normas Estruturais — Fase 2
================================
Pacote de ingestão, chunking, indexação e avaliação do corpus normativo.

Módulos
-------
- ingestion  : extração de texto e metadados dos PDFs
- chunker    : segmentação hierárquica dos documentos
- indexer    : embeddings e índice FAISS
- evaluator  : cálculo de Recall@k via golden_set.json
"""
