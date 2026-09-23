from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "xrag-workflow.png"
W, H = 2400, 3000
BG, INK, MUTED = "#F8F6F0", "#272725", "#62645F"
ACCENT, SAGE, LINE, WHITE = "#A94F36", "#4A6653", "#C8C4B8", "#FFFFFF"
SOFT, PALE = "#EEEAE0", "#E7EEE8"

font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
bold_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
title_font = ImageFont.truetype(bold_path, 82)
subtitle_font = ImageFont.truetype(font_path, 34)
section_font = ImageFont.truetype(bold_path, 34)
box_title = ImageFont.truetype(bold_path, 31)
box_body = ImageFont.truetype(font_path, 25)
small_font = ImageFont.truetype(font_path, 22)

im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)


def rounded_box(x, y, w, h, title, body="", fill=WHITE, border=LINE, title_color=INK):
    d.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=fill, outline=border, width=3)
    d.text((x + 28, y + 23), title, font=box_title, fill=title_color)
    if body:
        d.multiline_text((x + 28, y + 70), body, font=box_body, fill=MUTED, spacing=8)
    return (x, y, w, h)


def arrow(a, b, color=MUTED, width=6, dashed=False):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    start = (ax + aw / 2, ay + ah)
    end = (bx + bw / 2, by)
    if dashed:
        total = end[1] - start[1]
        yy = start[1]
        while yy < end[1] - 18:
            d.line((start[0], yy, end[0], min(yy + 18, end[1])), fill=color, width=width)
            yy += 32
    else:
        mid = (start[1] + end[1]) / 2
        d.line((start[0], start[1], start[0], mid, end[0], mid, end[0], end[1]), fill=color, width=width, joint="curve")
    d.polygon([(end[0], end[1]), (end[0] - 15, end[1] - 23), (end[0] + 15, end[1] - 23)], fill=color)


def horizontal_arrow(a, b, color=MUTED, width=6):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    start, end = (ax + aw, ay + ah / 2), (bx, by + bh / 2)
    d.line((start[0], start[1], end[0], end[1]), fill=color, width=width)
    d.polygon([(end[0], end[1]), (end[0] - 23, end[1] - 15), (end[0] - 23, end[1] + 15)], fill=color)


def section(y, number, title):
    d.text((100, y), number, font=section_font, fill=ACCENT)
    d.text((190, y), title, font=section_font, fill=INK)
    d.line((100, y + 50, W - 100, y + 50), fill=LINE, width=3)


d.text((100, 80), "XRAG end-to-end workflow", font=title_font, fill=INK)
d.text((100, 180), "Document ingestion, graph construction, grounded retrieval and evidence inspection", font=subtitle_font, fill=MUTED)
d.rounded_rectangle((1880, 77, 2295, 155), radius=18, fill=ACCENT)
d.text((1977, 95), "XRAG", font=section_font, fill=WHITE)

section(280, "01", "Authenticated document ingestion")
a = rounded_box(100, 370, 420, 140, "XRAG interface", "Authenticated workspace", fill=PALE, border=SAGE)
b = rounded_box(650, 370, 490, 140, "Extract text", "PDF.js  •  Mammoth  •  OCR")
c = rounded_box(1270, 370, 500, 140, "Validate upload", "Limits  •  origin  •  SHA-256")
e = rounded_box(1900, 370, 400, 140, "Clean and chunk", "~1,100 chars  •  140 overlap")
horizontal_arrow(a, b); horizontal_arrow(b, c); horizontal_arrow(c, e)

f = rounded_box(170, 650, 600, 155, "Create embeddings", "Nemotron 3 Embed 1B\n2,048 dimensions", fill=SOFT)
g = rounded_box(900, 650, 600, 155, "Extract graph facts", "Nemotron 3 Super\nEntities, relations and quotations", fill=SOFT)
h = rounded_box(1630, 650, 600, 155, "Validate graph output", "Schema, source IDs, endpoints\nand supporting quotations", fill=SOFT)
arrow(e, g); horizontal_arrow(f, g, color=LINE); horizontal_arrow(g, h)

section(900, "02", "Provenance-aware persistence")
i = rounded_box(170, 990, 820, 180, "D1 durable database", "Documents  •  passages  •  vectors\nentities  •  mentions  •  relations", fill=PALE, border=SAGE)
j = rounded_box(1120, 990, 520, 180, "R2 object storage", "Original uploaded files", fill=PALE, border=SAGE)
k = rounded_box(1770, 990, 460, 180, "Neo4j mirror", "Optional local graph analysis", fill=PALE, border=SAGE)
arrow(f, i); arrow(h, i); arrow(c, j); arrow(i, k, dashed=True)
d.text((1775, 1185), "optional export", font=small_font, fill=MUTED)

section(1310, "03", "Question answering with LangGraph")
q = rounded_box(100, 1400, 420, 155, "Question", "Choose lexical, vector,\ngraph or hybrid mode", fill=SOFT)
api = rounded_box(650, 1400, 470, 155, "Ask API", "Authenticate, validate and\napply rate limits", fill=SOFT)
ret = rounded_box(1250, 1400, 500, 155, "LangGraph  1  Retrieve", "Load the owner corpus and\nselect candidate evidence", fill=SOFT, border=ACCENT)
horizontal_arrow(q, api); horizontal_arrow(api, ret)

lex = rounded_box(190, 1720, 540, 140, "Lexical branch", "BM25: k1 = 1.2, b = 0.75")
vec = rounded_box(930, 1720, 540, 140, "Vector branch", "Cosine similarity > 0.30")
gra = rounded_box(1670, 1720, 540, 140, "Graph branch", "Up to 8 seeds and 2 hops")
arrow(ret, vec); horizontal_arrow(lex, vec, color=LINE); horizontal_arrow(vec, gra, color=LINE)

fusion = rounded_box(410, 2020, 690, 165, "Fuse and bound evidence", "RRF: Σ 1 / (60 + rank)\n6 passages, at most 3 per document", fill=PALE, border=SAGE)
gen = rounded_box(1300, 2020, 690, 165, "LangGraph  2  Generate", "At most 6 claims, each linked to\nsource IDs and exact quotations", fill=PALE, border=ACCENT)
arrow(lex, fusion); arrow(vec, fusion); arrow(gra, fusion); horizontal_arrow(fusion, gen)

val = rounded_box(410, 2330, 690, 165, "LangGraph  3  Validate", "Reject unknown source IDs and\nquotations absent from the passage", fill=PALE, border=ACCENT)
out = rounded_box(1300, 2330, 690, 165, "Grounded response", "Answer  •  passages  •  graph paths\nwarnings  •  abstention state", fill=PALE, border=SAGE)
arrow(gen, val); horizontal_arrow(val, out)

section(2610, "04", "Inspection, discovery and lifecycle")
rounded_box(100, 2700, 650, 150, "Evidence inspection", "Open citations and source documents", fill=SOFT)
rounded_box(875, 2700, 650, 150, "Knowledge discovery", "Graph exploration, experts and recommendations", fill=SOFT)
rounded_box(1650, 2700, 650, 150, "Coherent deletion", "Remove originals, derived records and stale history", fill=SOFT)
d.text((100, 2915), "Private academic pilot  •  500-passage workspace cap  •  Hosted graph in D1  •  Optional Neo4j export", font=small_font, fill=MUTED)

OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, quality=95, dpi=(180, 180))
print(OUT)
