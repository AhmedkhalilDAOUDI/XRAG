from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "xrag-workflow-keywords.png"
W, H = 2400, 3800
BG, INK, MUTED = "#F8F6F0", "#272725", "#62645F"
ACCENT, SAGE, LINE, WHITE = "#A94F36", "#4A6653", "#C8C4B8", "#FFFFFF"
PALE, SOFT = "#E7EEE8", "#EEEAE0"

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
title_font = ImageFont.truetype(BOLD, 76)
subtitle_font = ImageFont.truetype(FONT, 30)
card_title_font = ImageFont.truetype(BOLD, 32)
term_font = ImageFont.truetype(BOLD, 25)
body_font = ImageFont.truetype(FONT, 24)
footer_font = ImageFont.truetype(FONT, 21)

CATEGORIES = [
    ("01  SYSTEM AND ACCESS", [
        ("XRAG", "The platform: RAG enriched with a knowledge graph."),
        ("RAG", "Retrieves passages before an LLM writes an answer."),
        ("GraphRAG", "Adds entity relations and graph paths to retrieval."),
        ("Authenticated interface", "Private web workspace for uploads, questions and inspection."),
        ("Owner corpus", "Documents and derived records belonging to one signed-in owner."),
        ("API route", "Server endpoint that validates and executes a request."),
        ("Rate limit", "Caps requests per owner and time window."),
    ]),
    ("02  DOCUMENT INGESTION", [
        ("PDF.js", "Extracts text from PDF pages in the browser."),
        ("Mammoth", "Extracts readable content from DOCX files."),
        ("OCR", "Turns text in scans or images into machine-readable characters."),
        ("SHA-256", "Creates a stable content fingerprint for duplicate detection."),
        ("Deduplication", "Rejects repeated content in the same workspace."),
        ("Cleaning", "Normalizes text before it is indexed."),
        ("Chunk / passage", "A retrievable document segment of about 1,100 characters."),
        ("Overlap", "Repeats about 140 characters across adjacent chunks."),
    ]),
    ("03  MODELS AND GRAPH EXTRACTION", [
        ("LLM", "A language model used for extraction and answer generation."),
        ("NVIDIA NIM", "The server-side model API used by XRAG."),
        ("Nemotron 3 Embed 1B", "Creates 2,048-dimensional passage and question vectors."),
        ("Embedding", "A numeric representation of text meaning."),
        ("Nemotron 3 Super", "Extracts graph facts and generates grounded claims."),
        ("Entity", "A graph node: person, organisation, concept or project."),
        ("Relation", "A typed edge connecting two entities."),
        ("Mention", "A link from an entity back to its evidence passage."),
        ("Supporting quotation", "Exact source text supporting a fact or claim."),
        ("Schema / endpoint validation", "Checks output shape and relation endpoints."),
    ]),
    ("04  STORAGE AND PROVENANCE", [
        ("Provenance", "The trace from an answer or graph fact back to its source."),
        ("D1", "Hosted SQL storage for metadata, passages, vectors and graph records."),
        ("Metadata", "Identifiers, ownership, hashes, status and timestamps."),
        ("Property graph", "Knowledge represented as attributed nodes and edges."),
        ("R2", "Object storage that preserves original uploaded files."),
        ("Object storage", "Stores whole files by key rather than SQL rows."),
        ("Neo4j mirror", "Optional local copy for graph analysis; not the hosted query path."),
        ("Export", "A one-way graph copy, not automatic synchronization."),
    ]),
    ("05  LANGGRAPH AND RETRIEVAL", [
        ("LangGraph", "Runs the retrieve, generate and validate state machine."),
        ("Lexical retrieval", "Matches query words against passage words."),
        ("BM25", "Ranks term matches; k1 controls saturation and b adjusts for length."),
        ("Vector retrieval", "Matches the question to passages by meaning."),
        ("Cosine similarity", "Measures directional similarity between two vectors."),
        ("Similarity threshold", "Minimum vector score accepted as a candidate: > 0.30."),
        ("Graph traversal", "Follows relations from matching entities to evidence."),
        ("Seed", "A starting entity; XRAG uses at most eight."),
        ("Hop", "One crossed graph edge; XRAG uses at most two."),
        ("Hybrid retrieval", "Combines lexical, vector and graph result lists."),
    ]),
    ("06  FUSION AND EVIDENCE", [
        ("RRF", "Reciprocal Rank Fusion: sum of 1 / (60 + rank)."),
        ("Rank", "An item's position in one retrieval result list."),
        ("Bounded evidence", "At most six passages and three per document reach the LLM."),
        ("Claim", "One factual answer statement linked to supplied evidence."),
        ("Source ID", "Identifier of a retrieved passage available to the model."),
        ("Exact quotation", "Cited text that must occur verbatim in the source passage."),
        ("Citation validation", "Rejects unknown source IDs and absent quotations."),
    ]),
    ("07  OUTPUT AND EXPLAINABILITY", [
        ("Grounded response", "An answer tied to retrieved passages and graph paths."),
        ("Graph path", "An ordered sequence of entities and relations."),
        ("Warning", "Reports weak evidence or another recoverable limitation."),
        ("Abstention", "Returns no answer when valid evidence is insufficient."),
        ("Evidence inspection", "Opens citations and original source documents."),
        ("Graph exploration", "Lets the user inspect entities and relations directly."),
        ("Expert candidate", "A person linked to a domain by document evidence."),
        ("Recommendation", "A related document, procedure or project suggested by links."),
    ]),
    ("08  LIFECYCLE AND SCOPE", [
        ("Coherent deletion", "Removes originals and their derived records together."),
        ("Orphan entity", "An entity left without supporting mentions after deletion."),
        ("Stale history", "A saved answer that may cite deleted evidence."),
        ("Private academic pilot", "A tested PFE release for private evaluation."),
        ("500-passage cap", "Bounds storage, vector scanning, latency and model cost."),
    ]),
]


def wrap(text, font, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or d.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def card_height(items, width):
    height = 86
    for term, definition in items:
        height += 35
        height += len(wrap(definition, body_font, width - 58)) * 31 + 16
    return height + 22


def draw_card(x, y, width, title, items, accent):
    height = card_height(items, width)
    d.rounded_rectangle((x, y, x + width, y + height), radius=24, fill=WHITE, outline=LINE, width=3)
    d.rounded_rectangle((x, y, x + 16, y + height), radius=8, fill=accent)
    d.text((x + 40, y + 27), title, font=card_title_font, fill=accent)
    cursor = y + 84
    for term, definition in items:
        d.text((x + 40, cursor), term, font=term_font, fill=INK)
        cursor += 35
        lines = wrap(definition, body_font, width - 80)
        d.multiline_text((x + 40, cursor), "\n".join(lines), font=body_font, fill=MUTED, spacing=5)
        cursor += len(lines) * 31 + 16
    return height


im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
d.text((100, 76), "XRAG workflow keyword map", font=title_font, fill=INK)
d.text((100, 170), "Plain-English definitions for every technical term in the end-to-end workflow", font=subtitle_font, fill=MUTED)
d.rounded_rectangle((1880, 72, 2295, 150), radius=18, fill=ACCENT)
d.text((1975, 91), "XRAG", font=card_title_font, fill=WHITE)
d.line((100, 235, W - 100, 235), fill=LINE, width=3)

column_x = [100, 1220]
column_y = [285, 285]
card_width = 1080
accents = [ACCENT, SAGE]
for index, (title, items) in enumerate(CATEGORIES):
    column = min(range(2), key=lambda i: column_y[i])
    height = draw_card(column_x[column], column_y[column], card_width, title, items, accents[index % 2])
    column_y[column] += height + 34

assert max(column_y) < H - 140, "Glossary cards exceed the image canvas"
d.line((100, H - 125, W - 100, H - 125), fill=LINE, width=3)
d.text((100, H - 88), "Full explanations: docs/xrag-workflow-keywords.md  |  Workflow: docs/xrag-workflow.png", font=footer_font, fill=MUTED)
d.text((100, H - 52), "Values shown are the configured XRAG academic-pilot limits.", font=footer_font, fill=MUTED)

OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, quality=95, dpi=(180, 180))
print(OUT)
