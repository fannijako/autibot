# `autibot` — Update List

## Critical

- [ ] **Add tests.** None visible currently. Minimum bar:
  - Unit test on document chunking
  - Unit test on retrieval (mock vector store)
  - One integration test on the end-to-end RAG flow
- [ ] **Pin dependency versions** in `requirements.txt`. Bare requirements obscure the stack and break reproducibility.
- [ ] **README — document the RAG design decisions:**
  - Chunking strategy (size, overlap, splitter — character/token/semantic)
  - Embedding model + why (HF model name, dimension, language support — relevant since autism docs may be multilingual)
  - Vector store choice (Astra DB) + why over alternatives (Chroma, Qdrant, pgvector)
  - Retrieval params (top-k, similarity threshold)
  - Prompt template + system message
  - Hallucination mitigation approach (refusal rules, source citations, confidence thresholds)

## High-value

- [ ] **Add `eval/` folder** with:
  - 20-30 hand-graded Q&A pairs (`eval_set.jsonl`)
  - A notebook running recall@k and answer-quality scoring
  - Results table in README
  - Even rough numbers ("recall@5 = 0.78 on 30 hand-graded queries") beat zero numbers
- [ ] **Add CI workflow** to run tests on push/PR.
- [ ] **Document why custom RAG vs LangChain/LlamaIndex.** This is a defensible choice (less framework lock-in, simpler debugging, smaller attack surface) but only if you say so. Otherwise it reads as "didn't know the frameworks."
- [ ] **Add release tags.** Even `v0.1.0` shows discipline.

## Nice to have

- [ ] **Migrate to `pyproject.toml`** if currently `setup.py`/`requirements.txt`-only.
- [ ] **Add a `compose.dev.yaml`** for local development without Discord deps.
- [ ] **Cost/latency notes** in README — free-tier HF + Astra is a real architectural choice with trade-offs worth documenting.
- [ ] **Document data sources** (which autism documents, license/permission, refresh cadence).
- [ ] **Add a "future work" or "known limitations" section.**
