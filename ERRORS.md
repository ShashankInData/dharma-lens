# Errors

## 2026-06-28 - pytest missing

Command:
`python3 -m pytest tests/test_ingest.py -v`

Error:
`No module named pytest`

Fix:
Created `.venv`, installed `requirements.txt`, then ran tests with `.venv/bin/python`.

## 2026-06-28 - expected RED failure: ingest module missing

Command:
`. .venv/bin/activate && python -m pytest tests/test_ingest.py -v`

Error:
`ModuleNotFoundError: No module named 'src.ingest'`

Reason:
This was the expected TDD RED state before implementing ingestion.

Fix:
Created `src/ingest.py`, then tests passed.

## 2026-06-28 - expected RED failure: chunking module missing

Command:
`. .venv/bin/activate && python -m pytest tests/test_chunking.py -v`

Error:
`ModuleNotFoundError: No module named 'src.chunking'`

Reason:
Expected TDD RED state before implementing chunking.

Fix:
Created `src/chunking.py`, then tests passed.

## 2026-06-28 - expected RED failure: retrieval module missing

Command:
`. .venv/bin/activate && python -m pytest tests/test_retrieval.py -v`

Error:
`ModuleNotFoundError: No module named 'src.retrieval'`

Reason:
Expected TDD RED state before implementing retrieval.

Fix:
Created `src/retrieval.py`, then tests passed.

## 2026-06-28 - pickle class identity issue

Command:
`python -m src.evaluate_retrieval --index indexes/dharma_lens_vector_index.pkl ...`

Error:
`AttributeError: Can't get attribute 'VectorIndex' on <module 'src.evaluate_retrieval' ...>`

Reason:
The index was built through `python -m src.retrieval`, so pickle stored the dataclass as coming from the CLI execution context.

Fix:
Changed `save_index` to pickle primitive payload `{chunks, vectors}` and `load_index` to reconstruct `VectorIndex`. Rebuilt the index. Evaluation then passed.

## 2026-06-28 - expected RED failure: answer module missing

Command:
`. .venv/bin/activate && python -m pytest tests/test_answer.py -v`

Error:
`ModuleNotFoundError: No module named 'src.answer'`

Reason:
Expected TDD RED state before implementing answer generation.

Fix:
Created `src/answer.py`, then tests passed.

## 2026-06-28 - answer chunk selection duplicated context

Issue:
The first deterministic sample answer included overlapping/repetitive chunks and an irrelevant adjacent verse.

Fix:
Added `select_answer_chunks` and changed extractive answer generation to use a smaller concise context set. Re-ran tests and regenerated sample answer.
