# OTHER IDEAS — XRAG Improvement Roadmap

This document is a backlog of realistic improvements for XRAG. It describes ideas that **could** be implemented; it does not claim that they already exist. Each item states the problem, the proposed change, its value, and the main risk.

XRAG currently combines lexical, vector, and bounded graph retrieval; fuses their rankings; asks an NVIDIA model to answer from at most six passages; and validates citation identifiers and exact quotations. The priorities below strengthen that foundation before adding more autonomous behavior.

## How to read the roadmap

| Label | Meaning |
|---|---|
| **P0** | Reliability, security, and evaluation work required before wider production use |
| **P1** | High-value product or retrieval improvement |
| **P2** | Useful enhancement after the foundation is stable |
| **Research** | Experimental idea that must beat the baseline in a controlled evaluation |
| **S / M / L** | Small, medium, or large estimated implementation effort |

An idea should move from this document into the product only after it has an owner, acceptance criteria, tests, measurable results, documentation, and a rollback or feature flag where appropriate.

## Recommended implementation order

1. Expand the evaluation set and define measurable acceptance thresholds.
2. Add retrieval diagnostics, tracing, cost measurement, and regression tests.
3. Improve chunking, metadata, reranking, and answerability detection.
4. Strengthen citation entailment, access control, ingestion recovery, and backups.
5. Replace in-memory vector scanning and synchronous ingestion before increasing corpus limits.
6. Improve entity resolution, graph quality, and multi-hop retrieval.
7. Test Jev and other research ideas behind feature flags.
8. Add agentic or autonomous behavior only after deterministic workflows are reliable.

## 1. Evaluation and scientific validity

These changes should come first because XRAG cannot prove that another change is an improvement without a trustworthy benchmark.

### 1.1 Larger human-labelled benchmark — P0 / M

- Build a representative test set from permitted documents.
- Include direct fact, paraphrase, cross-document, multi-hop, temporal, table, unanswerable, ambiguous, and adversarial questions.
- Have humans identify the supporting passages and acceptable answers.
- Keep training/development questions separate from the final test questions.
- Report sample size and confidence intervals instead of relying only on averages.

**Measure:** Recall@k, Precision@k, MRR, nDCG, answer correctness, citation correctness, abstention precision/recall, latency, and cost.

### 1.2 Retrieval regression suite — P0 / S

Save a fixed set of questions and expected evidence identifiers. Run it whenever chunking, embeddings, graph construction, ranking, or thresholds change. Fail continuous integration when a protected metric falls below its agreed threshold.

### 1.3 Blind answer evaluation — P0 / M

Ask evaluators to compare answers without seeing which retrieval mode produced them. This reduces confirmation bias when comparing lexical, vector, graph, hybrid, reranked, and Jev-assisted versions.

### 1.4 Error taxonomy and failure dashboard — P0 / S

Classify failures as extraction, chunking, missing metadata, retrieval miss, entity-resolution error, wrong relationship, generation error, citation error, or incorrect abstention. Fix the most frequent causes instead of changing the model without evidence.

### 1.5 Production feedback loop — P1 / M

Let authorized users mark an answer as useful, incorrect, unsupported, incomplete, or outdated and optionally select the problematic citation. Store feedback separately from source truth and use reviewed feedback to extend the benchmark.

### 1.6 Evaluation dataset versioning — P1 / S

Version the corpus snapshot, questions, labels, model identifiers, prompts, thresholds, and code revision so every reported result is reproducible.

## 2. Retrieval quality

### 2.1 Learned reranker — P1 / M

Retrieve a broader candidate set, such as 20–50 passages, and use a cross-encoder or dedicated reranking model to score each question–passage pair before selecting the final six passages.

**Benefit:** better precision than cosine similarity or rank fusion alone.  
**Risk:** added latency, cost, and possible false negatives. Keep a non-reranked fallback.

### 2.2 Jev relevance filter and answerability gate — Research / M

Use Jev only for bounded decisions after XRAG's existing retrieval:

```text
Lexical + vector + graph retrieval
              ↓
      Reciprocal rank fusion
              ↓
Jev: relevance score for each candidate
              ↓
Jev: is the available evidence sufficient?
              ↓
Generation → deterministic citation checks → answer or abstain
```

Possible typed questions:

- **Choice or Score:** how relevant is this passage to the question?
- **Noul:** does this passage contain evidence needed to answer the question?
- **Noul:** do the selected passages provide enough evidence to answer?
- **Choice:** which existing graph relationship should be followed next?

Jev should receive only the minimum necessary text, run on the server, and be protected by timeouts, retries, a feature flag, and a fallback to the current pipeline. It should never invent graph identifiers or replace XRAG's deterministic source and quotation checks.

**Potential benefits:** typed results, probabilities, improved precision, better abstention, and constrained selection among real graph edges.  
**Risks:** another external provider, data-processing implications, extra latency and cost, model/version drift, and reduced recall if correct evidence is filtered out. Jev does not generate XRAG's final explanatory answer.

**Keep Jev only if:** it improves precision or unsupported-answer detection on a held-out benchmark without an unacceptable loss of recall, latency, privacy, or cost.

### 2.3 Automatic retrieval routing — P1 / M

The interface currently lets the user select lexical, vector, graph, or hybrid mode. Add a tested router that selects a mode from question characteristics, with hybrid as the safe fallback. Log the selected route and let the user override it.

Example rules or learned decisions:

- exact identifier or quoted phrase → lexical;
- semantic paraphrase → vector;
- relationship or multi-hop question → graph plus vector;
- uncertain classification → hybrid.

### 2.4 Query expansion and multi-query retrieval — P1 / M

Generate a small number of controlled paraphrases, aliases, acronyms, and entity names, retrieve for each, then fuse the results. Cap the number of variants and preserve the original query to limit drift.

### 2.5 HyDE experiment — Research / S

Generate a hypothetical answer or passage, embed it, and retrieve documents close to that representation. Evaluate carefully because a fabricated hypothesis can pull retrieval toward incorrect evidence.

### 2.6 Dynamic fusion weights — Research / M

Replace equal reciprocal-rank fusion with weights learned or tuned on the development set. Use separate weights for factual, relationship, and exact-match questions. Guard against overfitting.

### 2.7 Diversity-aware selection — P1 / S

Use maximal marginal relevance or a similar method to avoid returning six near-duplicate passages. Balance relevance with coverage across sections and documents.

### 2.8 Metadata filtering — P1 / M

Allow retrieval by document type, department, project, author, date, confidentiality level, language, version, and access group. Apply authorization filters before ranking, not after retrieval.

### 2.9 Parent–child retrieval — P1 / M

Embed small child chunks for precise matching, then return their larger parent section to the answer model. This preserves context without weakening retrieval precision.

### 2.10 Contextualized chunk embeddings — Research / M

Prepend a short document and section description before embedding each chunk. Keep the original passage text unchanged for citations. Compare results with the current embedding baseline.

### 2.11 Temporal and version-aware retrieval — P1 / L

Represent effective dates, document versions, superseded procedures, and publication dates. Prefer the latest valid information while preserving historical answers when a question specifies a date.

### 2.12 Retrieval caching — P2 / M

Cache normalized question embeddings and retrieval results by owner, corpus revision, retrieval mode, model version, and configuration. Invalidate the cache whenever the relevant corpus changes.

## 3. Chunking, parsing, and document understanding

### 3.1 Structure-aware chunking — P1 / M

Split by headings, paragraphs, lists, tables, and semantic boundaries before applying size limits. Record each passage's heading path. Avoid splitting a definition, list, or table across unrelated chunks.

### 3.2 Document hierarchy — P1 / M

Store document → chapter → section → subsection → passage relationships. Use the hierarchy for navigation, parent–child retrieval, summaries, and explainable retrieval paths.

### 3.3 Better PDF layout extraction — P1 / L

Detect columns, headings, footnotes, captions, headers, page numbers, reading order, and scanned pages. Preserve page coordinates so the interface can highlight the exact cited region in the original PDF.

### 3.4 Table extraction — P1 / L

Parse tables into structured rows and columns while retaining the original table text and page reference. Add table-specific retrieval and answer rendering instead of treating every CSV, JSON object, or PDF table as plain text.

### 3.5 Multilingual OCR and retrieval — P1 / L

Support at least English, French, and Arabic OCR and language detection. Evaluate multilingual embeddings and cross-language retrieval rather than assuming English accuracy transfers to other languages.

### 3.6 Image and diagram understanding — P2 / L

Extract captions, labels, and accessible descriptions from meaningful images and diagrams. Cite the source page and clearly mark machine-generated visual descriptions for human review.

### 3.7 Ingestion preview and correction — P1 / M

Before indexing, show extracted text, detected language, headings, tables, OCR confidence, and warnings. Let an authorized user correct metadata or reject poor extraction.

### 3.8 Content-quality scoring — P2 / M

Detect empty pages, OCR corruption, duplicate passages, navigation-only text, repeated headers, and unusually noisy chunks. Quarantine low-quality content instead of silently indexing it.

### 3.9 Exact and near-duplicate detection — P1 / M

Keep SHA-256 exact deduplication and add near-duplicate detection for renamed or lightly edited documents. Preserve legitimate versions and show their relationships rather than deleting them automatically.

### 3.10 Incremental re-indexing — P1 / L

Reprocess only changed sections when a document version is uploaded. Track which passages, embeddings, entities, edges, and cached results were invalidated.

## 4. Knowledge graph quality

### 4.1 Domain ontology — P1 / L

Define allowed entity types, relationship types, direction, required properties, and examples for the target organisation. Validate extracted triples against this ontology.

### 4.2 Entity resolution and alias management — P1 / L

Merge spelling variants, abbreviations, translations, and duplicate people or organisations while keeping evidence for every alias. Require review for low-confidence merges because an incorrect merge can contaminate many graph paths.

### 4.3 Relationship confidence and provenance — P1 / M

Store extraction confidence, source passage, model version, extraction prompt, timestamp, and review status for every edge. Never expose an inferred relationship as confirmed fact without its evidence.

### 4.4 Contradiction representation — P1 / L

Allow the graph to preserve conflicting claims from different sources and versions. Show both pieces of evidence and their dates rather than forcing one value to overwrite another.

### 4.5 Human graph review — P1 / M

Create an approval queue for uncertain entities, aliases, and relationships. Record who accepted, edited, or rejected each item and retain the original machine proposal for auditability.

### 4.6 Graph-aware path scoring — Research / M

Score paths using question relevance, edge confidence, source quality, recency, path length, and repeated entities. Compare this with the current fixed two-hop traversal.

### 4.7 Adaptive graph depth — Research / M

Use one hop for direct relations and expand only when the question and evidence justify another hop. Enforce cycle detection, branch limits, time budgets, and maximum depth.

### 4.8 Jev-guided graph traversal — Research / M

At a graph node, give Jev only the real adjacent edges as predefined choices and ask which edge is most likely to advance toward the question's goal. Beam-search the strongest choices and stop at a strict budget. This can improve navigation while preventing invented nodes or relationships.

### 4.9 Community detection and hierarchical summaries — Research / L

Detect graph communities, create evidence-linked summaries at several levels, and use them for broad questions about themes or the whole corpus. This would move XRAG closer to a community-summary GraphRAG design and requires separate evaluation from local passage retrieval.

### 4.10 Live graph database path — P2 / L

Evaluate whether a managed graph database is justified by corpus size and query needs. If Neo4j becomes part of the deployed path, implement synchronization, deletion, access control, backups, health checks, and consistency monitoring. Do not add it only for branding.

## 5. Answer generation and groundedness

### 5.1 Semantic citation-entailment check — P0 / M

The current validator proves that a cited identifier exists and that the exact quotation occurs in the source. Add a separate check that the quotation actually supports the complete claim. Keep deterministic checks as the first gate and evaluate the semantic judge's false-accept and false-reject rates.

### 5.2 Claim decomposition — P1 / M

Require one independently verifiable fact per claim. Split compound statements before validation so one valid quotation cannot appear to support several unsupported facts.

### 5.3 Contradiction check across evidence — P1 / M

Before answering, detect whether selected passages disagree. If they do, present the disagreement with dates and sources or abstain when the conflict cannot be resolved.

### 5.4 Calibrated answerability — P1 / M

Combine retrieval coverage, reranker scores, source diversity, citation validation, and optional Jev decisions into an answerability policy. Calibrate thresholds on labelled data and explain abstention to the user.

### 5.5 Citation coverage measurement — P1 / S

Measure what proportion of factual answer sentences have valid supporting citations and whether every cited source was actually used. Reject or revise answers that fail the configured threshold.

### 5.6 Evidence-first answer view — P1 / M

Let users expand each claim to see the exact quotation, page, section, retrieval branch, graph path, and original document. Visually distinguish direct evidence, system inference, and unresolved uncertainty.

### 5.7 Model routing — P2 / M

Use a smaller model for simple extraction or formatting and the stronger model for synthesis or multi-hop questions. The routing policy must be measurable, reversible, and unable to bypass evidence validation.

### 5.8 Response streaming with delayed verification — P2 / M

Stream only clearly marked provisional output, then publish the final answer after validation. A safer alternative is to stream workflow progress and evidence while withholding factual answer text until checks complete.

### 5.9 Prompt and model version registry — P0 / S

Record prompt version, model identifier, parameters, retrieval configuration, and validator version with each saved query. This makes regressions and academic results traceable.

## 6. LangGraph workflow improvements

### 6.1 Explicit retry and fallback nodes — P1 / M

Add bounded retries for temporary provider failures and deterministic fallbacks such as hybrid → lexical plus graph when embeddings are unavailable. Record every fallback in the answer metadata.

### 6.2 Retrieve-again loop — Research / M

If evidence is insufficient, rewrite the query once and retrieve again. Limit the loop count and compare it with a single-pass baseline to prevent latency and cost from growing silently.

### 6.3 Human-review node — P1 / M

Route high-risk, low-confidence, contradictory, or access-sensitive questions to an authorized reviewer. Preserve the full evidence and decision trace.

### 6.4 Durable workflow state — P1 / L

Persist ingestion and long-running query state so work can resume after a crash. Use idempotency keys to prevent duplicate document versions or repeated provider calls.

### 6.5 Workflow-level time and cost budgets — P1 / S

Set maximum provider calls, tokens, graph expansions, retries, and wall-clock time per request. Abort safely with a clear explanation when the budget is exhausted.

## 7. Scale, performance, and reliability

### 7.1 Approximate nearest-neighbour vector index — P0 before scaling / L

Replace full in-memory vector scanning when the corpus exceeds the current bounded pilot. Benchmark candidate services or indexes using recall, latency, filtering support, isolation, operational complexity, and cost.

### 7.2 Durable ingestion queue — P0 before scaling / L

Move parsing, OCR, embedding, and graph extraction into retryable background jobs. Show status per stage and place repeatedly failing jobs in a review queue.

### 7.3 Atomic ingestion and reconciliation — P0 / L

Track the desired and actual state of D1 rows, R2 objects, embeddings, and graph data. Add a reconciliation job that repairs or reports incomplete uploads and deletions after crashes.

### 7.4 Backup and restore drills — P0 / M

Define retention, restore D1 and R2 into an isolated environment, verify document hashes and graph counts, and record recovery time and recovery-point results. A backup is not proven until restoration succeeds.

### 7.5 Load and capacity testing — P0 / M

Measure concurrent uploads, questions, graph rendering, large documents, provider slowdowns, and database limits. Define safe corpus and concurrency limits from evidence.

### 7.6 Caching and request coalescing — P1 / M

Cache embeddings, document summaries, and identical retrieval requests. Coalesce simultaneous identical work and use corpus-version keys to avoid stale results.

### 7.7 Provider circuit breakers — P1 / M

Detect repeated NVIDIA, OCR, Jev, or storage failures and stop sending calls temporarily. Return a controlled degraded response and expose provider status to operators.

### 7.8 Data lifecycle jobs — P1 / M

Detect orphan R2 objects, unused entities, broken edges, stale cache entries, old query history, and expired documents. Run repair in report-only mode before allowing mutation.

## 8. Security, privacy, and governance

### 8.1 Document-level and passage-level authorization — P0 / L

Enforce access rules during retrieval, graph traversal, recommendations, exports, and history queries. Test that restricted content cannot leak through embeddings, graph neighbors, summaries, or cached results.

### 8.2 Organisation and role management — P0 / L

Add explicit organisations, membership, roles, document groups, administrator controls, and revocation. Do not infer enterprise authorization only from an email string.

### 8.3 Prompt-injection defence evaluation — P0 / M

Maintain adversarial documents that attempt to change instructions, request secrets, forge citations, or redirect tool use. Test ingestion, retrieval, generation, export, and UI rendering against them.

### 8.4 Sensitive-data detection and redaction — P1 / L

Detect configured personal, financial, legal, or secret values before external model calls. Let policy block, redact, or require review while keeping an auditable record of what was transformed.

### 8.5 Encryption and key management review — P0 / M

Document encryption in transit and at rest for the gateway, D1, R2, provider calls, exports, and backups. Establish secret rotation and incident procedures.

### 8.6 Audit log — P0 / M

Record authentication events, uploads, deletions, exports, access-policy changes, graph reviews, and administrative actions in an append-oriented audit trail with retention controls.

### 8.7 Configurable retention and deletion — P1 / M

Define retention periods for source files, derived passages, embeddings, graph data, query history, logs, caches, and backups. Verify deletion across every derived representation.

### 8.8 Security review and dependency scanning — P0 / M

Add dependency, secret, static-analysis, and container checks to continuous integration. Perform a focused review of authentication boundaries, file parsing, injection, rate limits, exports, and tenant isolation.

### 8.9 Content-security controls — P1 / S

Harden response headers and safely render document-derived text. Prevent uploaded HTML, Markdown, filenames, graph labels, and citations from becoming executable content.

## 9. Observability and operations

### 9.1 End-to-end tracing — P0 / M

Assign a request identifier and trace retrieval branches, scores, selected evidence, graph expansions, model calls, validation results, fallbacks, latency, and cost without logging confidential text by default.

### 9.2 Operational dashboards and alerts — P1 / M

Track error rates, p50/p95 latency, ingestion backlog, provider failures, token usage, cost, corpus size, abstention rate, citation rejection rate, cache hit rate, and authorization failures.

### 9.3 Live dependency health — P1 / S

Keep the cheap internal health endpoint and add controlled synthetic checks for critical dependencies. Separate readiness, liveness, and external-provider status.

### 9.4 Runbooks — P0 / M

Document provider outage, bad deployment, failed migration, corrupt ingestion, accidental deletion, credential exposure, access leak, restore, and rollback procedures. Test the procedures periodically.

### 9.5 Deployment promotion and rollback — P0 / M

Promote an exact tested revision through environments, validate migrations before traffic, retain the previous version, and define automatic and manual rollback triggers.

### 9.6 Cost controls — P1 / S

Set per-user and organisation budgets, alerts, maximum document sizes, maximum provider calls, and administrative reports. Treat every optional judge, reranker, query rewrite, and agent loop as additional cost.

## 10. User experience and knowledge management

### 10.1 Source viewer with exact highlighting — P1 / M

Open the original page and highlight the cited quotation. If coordinates are unavailable, show the nearest verified text block and explain the limitation.

### 10.2 Search and chat history controls — P2 / M

Add folders, tags, rename, export, retention controls, and deletion for saved questions. Make it clear when an old answer was produced from an older corpus or model version.

### 10.3 Corpus and freshness dashboard — P1 / M

Show document count, indexing state, failed files, languages, versions, duplicates, stale content, latest update, and passages with weak extraction or graph confidence.

### 10.4 Explain retrieval mode — P1 / S

Show why lexical, vector, graph, hybrid, reranked, or Jev-assisted retrieval was used and what each contributed. Avoid presenting model probabilities as certainty.

### 10.5 Expert identification safeguards — P1 / M

Call people “documented expert candidates” unless the organisation verifies expertise. Show the source evidence, time range, and reason for the suggestion, and let administrators correct it.

### 10.6 Recommendation explanations — P1 / S

For every recommended document or project, show shared entities, similar passages, relevant relationships, and freshness. Let users dismiss irrelevant recommendations.

### 10.7 Accessibility and responsive review — P1 / M

Test keyboard navigation, focus, screen readers, contrast, reduced motion, zoom, mobile layouts, graph alternatives, and non-colour status indicators against WCAG 2.1 AA.

### 10.8 Internationalisation — P2 / L

Localize the interface, errors, dates, number formats, OCR selection, and answer language. Preserve source quotations in their original language and optionally provide clearly labelled translations.

## 11. APIs, integrations, and administration

### 11.1 Versioned API and generated schema — P1 / M

Publish authenticated, versioned endpoints with request/response schemas, stable error codes, pagination, idempotency, rate limits, and examples. Generate documentation from the actual schema.

### 11.2 Connectors with change detection — P2 / L

Add read-only connectors for approved repositories such as SharePoint, Google Drive, Confluence, or internal stores. Respect source permissions, detect changes, preserve provenance, and provide a safe disconnect and deletion path.

### 11.3 Webhooks and job status API — P2 / M

Notify trusted systems when ingestion succeeds, fails, or requires review. Sign webhook payloads, retry safely, and prevent duplicate handling.

### 11.4 Administrative configuration — P1 / M

Manage allowed file types, corpus limits, models, thresholds, retention, feature flags, provider budgets, and review policies without editing source code. Record every change in the audit log.

### 11.5 Export portability — P2 / M

Export documents, metadata, passages, embeddings metadata, entities, relationships, evidence links, and configuration in a documented versioned format. Do not export secrets or inaccessible content.

## 12. Model and embedding experiments

### 12.1 Embedding benchmark — P1 / M

Compare the current `nvidia/nemotron-3-embed-1b` baseline with multilingual and domain-relevant alternatives on the same labelled corpus. Measure retrieval quality, dimension, storage, latency, cost, language coverage, and migration effort.

### 12.2 Embedding migration workflow — P1 / M

Support background re-embedding into a new versioned index, dual-read evaluation, validation, cutover, and rollback. Never mix incompatible vector dimensions or model spaces.

### 12.3 Generator model comparison — P2 / M

Compare grounded answer quality, instruction resistance, structured-output reliability, latency, and cost. Keep retrieval and evaluation data fixed during the comparison.

### 12.4 Local or private model option — Research / L

Evaluate deployment in a controlled environment when confidentiality or connectivity requires it. Include hardware, operations, model quality, patching, and total ownership cost.

### 12.5 Domain adaptation — Research / L

Consider fine-tuning only after retrieval, prompts, ontology, and evaluation expose a repeated model limitation that cannot be solved more safely with data or deterministic logic.

## 13. Advanced research directions

### 13.1 Multi-agent research workflow — Research / L

Separate planning, retrieval, graph analysis, evidence criticism, and writing into bounded roles. All agents must share the same authorization filters, evidence contract, budgets, and final deterministic validation. This is unsuitable as a first fix for weak retrieval.

### 13.2 Causal and temporal knowledge graphs — Research / L

Represent events, time intervals, claimed causes, and uncertainty explicitly. Do not infer causality merely from textual co-occurrence.

### 13.3 Active learning — Research / L

Select uncertain retrieval, entity-resolution, or relationship cases for human labelling and use the reviewed examples to tune thresholds or train a small classifier.

### 13.4 Personalization with strict boundaries — Research / L

Use role, team, and approved preferences to rank accessible information. Prevent personalization from changing factual evidence or weakening access control.

### 13.5 Federated retrieval — Research / L

Query several separately governed corpora without copying all documents into one store. Merge only authorized evidence and preserve each source's identity and policy.

### 13.6 Knowledge-gap discovery — Research / M

Aggregate unanswered questions and low-confidence areas to identify missing, outdated, or contradictory documentation. Require human review before turning usage patterns into organisational conclusions.

## 14. Ideas that should not be added without evidence

- Unlimited autonomous browsing or tool execution.
- Removing citations to make answers look cleaner.
- Treating an LLM or Jev confidence value as proof of correctness.
- Increasing graph depth without branch, cycle, latency, and cost limits.
- Replacing deterministic authorization or citation checks with a model judge.
- Adding Neo4j, an agent framework, or another provider only to make the technology list longer.
- Fine-tuning before establishing a reproducible baseline and failure taxonomy.
- Raising corpus limits while vectors are still scanned in memory and ingestion remains synchronous.
- Claiming production readiness from unit tests or a small synthetic evaluation set.

## 15. Suggested first five implementation tickets

### Ticket 1 — Expand and version the benchmark

**Acceptance criteria:** at least 100 reviewed questions across the defined categories, evidence labels, unanswerable examples, a frozen test split, and a reproducible evaluation report.

### Ticket 2 — Add retrieval diagnostics

**Acceptance criteria:** per-branch ranks and scores, fused rank, selected sources, latency, model versions, corpus revision, and rejection reasons are traceable without exposing source text in normal logs.

### Ticket 3 — Add a reranker experiment

**Acceptance criteria:** feature flag, fixed candidate budget, timeout and fallback, benchmark comparison, latency/cost report, and no material Recall@k regression.

### Ticket 4 — Add semantic claim support checking

**Acceptance criteria:** deterministic checks remain mandatory; the semantic checker is tested on supported, partially supported, contradictory, and unsupported claims; false accepts and false rejects are reported.

### Ticket 5 — Add Jev as an experimental answerability gate

**Acceptance criteria:** server-side key, minimum necessary state, feature flag, timeout, fallback, model-version logging, privacy review, baseline comparison, and a documented removal decision if results do not justify the dependency.

## References for the Jev experiment

- [TypeSafe AI documentation](https://docs.typesafe.ai/introduction)
- [Jev AI overview and typed-decision examples](https://github.com/jev-ai)
- [Neo4j experiment: navigating a knowledge graph with Jev](https://neo4j.com/blog/genai/navigating-a-neo4j-knowledge-graph-with-jev/)
- [Open-source Jev RAG experiment](https://github.com/SheaCrow/jev-rag)

These references describe current products and experiments, not independent proof that Jev will improve XRAG. The XRAG benchmark must decide that.
