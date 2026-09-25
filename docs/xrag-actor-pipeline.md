# XRAG responsibility pipeline

This document answers three questions for every step: who acts, what was actually used, and what the step produces. "Tool" means deterministic software written or configured in the project. "Model" means a learned NVIDIA model whose output must be validated. The user remains responsible for source permission, the question, and final judgment.

## A. Document indexing

1. **You choose the source.** You select a supported file, provide its title, and decide whether English OCR may be used. You are responsible for permission to process the document.
2. **Browser tools read the file.** The React interface calls PDF.js 6.3 for PDFs, Mammoth 1.12 for DOCX, the browser `File.text()` method for TXT/MD/CSV/JSON, and Tesseract.js 7 for optional English OCR. This happens in `lib/parse-file.ts`.
3. **XRAG code authenticates and validates.** The documents route reads the Sites identity header, checks request origin, applies a Zod schema, accepts only supported extensions, bounds file/page/text size, and applies five imports per minute per owner.
4. **XRAG code cleans and chunks.** `lib/core.ts` normalizes line endings and spacing. It creates passages of about 1,100 characters with about 140 characters of overlap, never crosses a page boundary, and accepts at most 64 passages per document.
5. **The embedding model creates passage vectors.** `nvidia/nemotron-3-embed-1b` receives `input_type=passage`. The verified vectors contain 2,048 values and are requested in batches of 16.
6. **The generative model proposes graph facts.** `nvidia/nemotron-3-super-120b-a12b` receives batches of four passages. It returns JSON containing entities, typed relations, and exact supporting quotations.
7. **XRAG code validates the model proposal.** Zod checks the schema. Project code checks passage IDs, source and target entities, normalized name presence, relation endpoints, and exact quotations. Malformed structured output gets at most one correction attempt.
8. **D1 and R2 persist the index.** R2 stores the original bytes. D1 stores documents, passages, JSON vectors, entities, mentions, and evidence-linked edges. The D1 batch is atomic. R2 and D1 do not share a distributed transaction, so XRAG uses compensation if the D1 batch fails.

## B. Question answering

9. **You ask and choose the mode.** You write a question and choose lexical, vector, graph, or hybrid retrieval.
10. **XRAG code guards the API.** `/api/ask` authenticates the owner, checks origin, validates a 3-to-2,000-character question with Zod, and permits 12 questions per minute per owner.
11. **LangGraph starts the explicit state machine.** `@langchain/langgraph` 1.4 runs `START -> retrieve -> generate -> validate -> END` in `lib/workflow.ts`.
12. **The embedding model represents the question.** Vector and hybrid modes call Nemotron 3 Embed 1B with `input_type=query`. Lexical and graph-only modes do not need this call. If indexed documents use another embedding model, XRAG requests re-indexing.
13. **XRAG code retrieves candidates.** Custom code in `lib/core.ts` runs BM25-style lexical ranking with `k1=1.2` and `b=0.75`, cosine similarity above `0.30`, and graph traversal with at most eight seeds and two hops. XRAG does not use a prebuilt LangChain retriever.
14. **XRAG code fuses and bounds evidence.** Reciprocal Rank Fusion adds `1/(60+rank)` across selected branches. The final context contains at most six passages and three from one document. Source IDs such as `S1` are assigned here.
15. **The generative model proposes grounded claims.** Nemotron 3 Super receives the question and selected passages. The prompt permits at most six JSON claims and requires source IDs plus one exact quotation for each citation.
16. **XRAG code validates or abstains.** `validateClaims` rejects unknown source IDs and quotations absent from the cited passage. Invalid claims are removed. If no valid claim remains, XRAG returns an insufficient-evidence abstention.
17. **D1 saves the result.** The `queries` table stores the complete answer object, mode, owner, and timestamp.
18. **Browser tools show inspectable evidence.** The React workspace shows the answer, passages, graph paths, warnings, timing, and workflow steps. You open citations and decide whether the evidence supports the answer.

## C. Inspection and lifecycle

19. **You choose the action.** You can inspect a passage, download the original, export the graph, clear history, or delete a document.
20. **XRAG code enforces ownership and cleanup.** Every route filters by owner. Deletion removes the document and dependent records, deletes orphan entities, and clears history that could cite deleted evidence.
21. **The data infrastructure applies the operation.** R2 serves or deletes original files. D1 reads or deletes structured evidence. Neo4j 5.26 Community is only an optional local export mirror and does not answer hosted XRAG questions.

## Responsibility rule

- **You:** provide authorised documents, define the question, choose the mode, inspect evidence, and make the final judgment.
- **Browser tools:** read files and present results. They follow deterministic code.
- **XRAG code:** authenticates, validates, ranks, fuses, stores, deletes, and verifies model output.
- **NVIDIA models:** create embeddings and propose language structures or claims. They do not decide whether their own output is accepted.
- **D1, R2, Workers, and Sites:** persist data and host execution. Storage does not reason.

XRAG does not train or fine-tune a model. Neo4j is not in the hosted query path. The project does not implement the full Microsoft community-summary GraphRAG pipeline.
