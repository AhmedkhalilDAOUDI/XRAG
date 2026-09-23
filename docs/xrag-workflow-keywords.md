# XRAG workflow glossary

This glossary explains the technical vocabulary in the XRAG end-to-end workflow. Read it with the [workflow diagram](xrag-workflow.png). The explanations describe the implemented academic pilot; they do not claim that every named technology serves the hosted query path.

## 1. System and access

**XRAG** is the platform name. It combines retrieval-augmented generation with a knowledge graph so that answers can use text passages and relationships between concepts.

**RAG (Retrieval-Augmented Generation)** retrieves evidence from a document collection before an LLM writes an answer. The retrieved passages constrain the answer and provide material for citations.

**GraphRAG** adds graph data to retrieval. XRAG can follow entity-relation paths as well as match words and vectors. This project implements a bounded property-graph workflow; it is not the complete Microsoft GraphRAG community-summary pipeline.

**Authenticated interface** is the private web interface through which a signed-in user uploads documents, asks questions, inspects evidence, and explores the graph.

**Workspace / owner corpus** is the collection of documents and derived records that belong to one authenticated owner. Owner checks prevent one user from querying another user's corpus.

**API route** is a server endpoint such as `/api/ask` or `/api/documents`. It validates the request, applies access controls, runs the relevant workflow, and returns structured data.

**Rate limit** bounds how often an owner may call an endpoint during a time window. It protects the service and model quota from accidental or abusive traffic.

## 2. Document ingestion

**Supported document** is a file type the ingestion layer knows how to read: PDF, DOCX, TXT, MD, CSV, or JSON. CSV and JSON are treated as text in this release.

**PDF.js** is the PDF parser used to extract text from PDF pages in the browser.

**Mammoth** extracts readable text from DOCX files. It focuses on document content rather than reproducing Word page layout.

**OCR (Optical Character Recognition)** converts text visible in an image or scanned page into machine-readable characters. XRAG uses optional English OCR with Tesseract when normal PDF text extraction is insufficient.

**Server validation** checks file size, type, ownership, request limits, and required fields before persistence.

**SHA-256** is a cryptographic hash function. XRAG hashes document content to obtain a stable fingerprint for duplicate detection.

**Deduplication** rejects a repeated file when its content hash already exists in the same owner workspace.

**Cleaning** normalizes extracted text and removes unusable spacing or characters before indexing.

**Chunk / passage** is a bounded piece of a document used for retrieval and citation. XRAG targets about 1,100 characters per passage.

**Overlap** repeats a small amount of text between adjacent chunks. The approximate 140-character overlap reduces the risk of splitting a sentence or fact at a chunk boundary.

## 3. Models and knowledge extraction

**LLM (Large Language Model)** is a model trained to process and generate language. XRAG uses an LLM for structured graph extraction and evidence-grounded answer generation.

**NVIDIA NIM** is the model API used by XRAG. The API key stays in the server environment and must never be committed to GitHub or sent to browser code.

**Nemotron 3 Embed 1B** is the embedding model configured for the verified release. It converts passages and questions into 2,048-dimensional vectors.

**Embedding** is a numerical representation of meaning. Texts with related meaning should have vectors that point in similar directions.

**Vector dimension** is the number of numeric coordinates in an embedding. XRAG stores 2,048 values for each vector produced by its configured embedding model.

**Nemotron 3 Super** is the configured generative model. XRAG uses it to extract graph facts and generate claims from retrieved evidence.

**Entity** is a concept or named thing represented as a graph node, such as a person, organisation, technology, procedure, or project.

**Relation** is a typed connection between two entities, such as `USES`, `AUTHORED_BY`, or `RELATED_TO`.

**Mention** links an entity to the passage where it appears. Mentions preserve the route from a graph node back to textual evidence.

**Supporting quotation** is the exact passage text that supports an extracted relation or generated claim.

**Schema** defines the required shape and types of model output. Schema validation rejects malformed graph records before they reach storage.

**Endpoint validation** verifies that the source and target of every relation refer to known entities.

## 4. Persistence and provenance

**Provenance** records where a fact or answer came from. XRAG connects documents, passages, entities, relations, quotations, and answer citations so the user can inspect the evidence chain.

**D1** is the hosted SQL database. It stores document metadata, passages, vectors, entities, mentions, relations, and question history for the deployed pilot.

**Durable database** means application records survive individual requests and process restarts.

**Metadata** describes a record rather than containing the original file itself. Examples include document ID, title, owner ID, content hash, status, and creation time.

**Property graph** represents knowledge as nodes and edges with attributes. XRAG stores this graph in D1 tables for its hosted query path.

**R2** is object storage for the original uploaded files. The database keeps references and derived records while R2 preserves the file bytes.

**Object storage** stores whole files as objects addressed by keys. It differs from SQL tables, which store structured rows and relationships.

**Neo4j** is a graph database used here as an optional local analysis mirror. It does not serve the deployed XRAG query path.

**Mirror / export** is a copy of the D1-backed graph sent to Neo4j for local exploration. It is not automatic two-way synchronisation.

## 5. LangGraph and retrieval

**LangGraph** orchestrates the question-answering state machine. In XRAG it runs three explicit stages: retrieve evidence, generate claims, and validate citations.

**Retrieval mode** selects lexical, vector, graph, or hybrid search.

**Lexical retrieval** matches query words against passage words. It is strong when names and exact terminology matter.

**BM25** ranks passages from term frequency, term rarity, and passage length. XRAG uses `k1 = 1.2` to control term-frequency saturation and `b = 0.75` to normalize for passage length.

**Vector retrieval** embeds the question and compares its vector with stored passage vectors. It can match similar meaning even when the words differ.

**Cosine similarity** measures the angle between two vectors. A larger value means their directions, and therefore their represented meanings, are more similar.

**Similarity threshold** is the minimum vector score accepted as a candidate. The workflow displays a threshold greater than `0.30`.

**Graph traversal** follows relations from matched seed entities to nearby nodes and evidence passages.

**Seed** is a starting entity selected from the question or initial matches. XRAG bounds traversal to at most eight seeds.

**Hop** is one graph edge crossed during traversal. XRAG limits retrieval to two hops to control latency and topic drift.

**Hybrid retrieval** combines lexical, vector, and graph result lists rather than trusting one retrieval method for every question.

**RRF (Reciprocal Rank Fusion)** combines ranked lists with the score `sum(1 / (60 + rank))`. It rewards items that rank well in one or more retrieval branches without requiring their raw scores to share a scale.

**Bounded evidence selection** limits the context sent to the LLM. XRAG sends at most six passages and at most three passages from one document.

## 6. Generation, validation, and output

**Claim** is one factual statement produced for the final answer. XRAG requests at most six claims and requires each one to reference evidence.

**Source ID** is the identifier assigned to a retrieved passage. The validation stage rejects citations to IDs that were not supplied to the model.

**Exact quotation** is a cited text fragment that must occur verbatim in its source passage. This check catches invented quotations, although it does not prove semantic entailment.

**Grounded response** is an answer tied to retrieved passages and graph paths rather than generated from model memory alone.

**Citation validation** checks that every cited source ID exists and that each quoted string appears in the cited passage.

**Graph path** is an ordered sequence of entities and relations used to show how concepts connect.

**Warning** reports a recoverable limitation, such as weak evidence or a rejected citation.

**Abstention state** tells the interface that XRAG does not have enough valid evidence to answer safely.

## 7. Inspection, discovery, and lifecycle

**Evidence inspection** lets the user open the passages and original documents behind an answer.

**Saved history** stores previous questions and outputs for the authenticated owner.

**Graph exploration** displays entities and relations so the user can inspect connections directly.

**Expert candidate** is a person associated with a domain by evidence in the uploaded documents. The label is a documented candidate, not an independently verified assessment of expertise.

**Recommendation** is a related document, procedure, or project proposed from shared entities and graph relationships.

**Coherent deletion** removes an original file and its derived passages, vectors, mentions, and relations as one controlled lifecycle operation.

**Orphan entity** is an entity with no remaining supporting mentions after document deletion. XRAG removes these entities during cleanup.

**Stale query history** is a saved answer that may refer to deleted evidence. XRAG removes owner history during document deletion to avoid presenting invalid citations.

**Private academic pilot** describes the release boundary: the system is a tested PFE implementation for private evaluation, not an independently certified enterprise product.

**500-passage workspace cap** bounds storage, in-memory vector scanning, latency, and model costs in the current deployment. A larger production corpus needs a vector index, background ingestion queue, load testing, backup validation, and organisation-specific access controls.
