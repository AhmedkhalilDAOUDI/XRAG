from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "xrag-workflow-fr.png"
W, H = 2400, 3000
BG, INK, MUTED = "#F8F6F0", "#272725", "#62645F"
ACCENT, SAGE, LINE, WHITE = "#A94F36", "#4A6653", "#C8C4B8", "#FFFFFF"
SOFT, PALE = "#EEEAE0", "#E7EEE8"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
title_font = ImageFont.truetype(BOLD, 78)
subtitle_font = ImageFont.truetype(FONT, 32)
section_font = ImageFont.truetype(BOLD, 33)
box_title = ImageFont.truetype(BOLD, 29)
box_body = ImageFont.truetype(FONT, 23)
small_font = ImageFont.truetype(FONT, 21)

im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)


def box(x, y, w, h, title, body="", fill=WHITE, border=LINE):
    d.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=fill, outline=border, width=3)
    d.text((x + 26, y + 22), title, font=box_title, fill=INK)
    if body:
        d.multiline_text((x + 26, y + 68), body, font=box_body, fill=MUTED, spacing=7)
    return x, y, w, h


def arrow(a, b, color=MUTED, width=6):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    start, end = (ax + aw / 2, ay + ah), (bx + bw / 2, by)
    mid = (start[1] + end[1]) / 2
    d.line((start[0], start[1], start[0], mid, end[0], mid, end[0], end[1]), fill=color, width=width, joint="curve")
    d.polygon([(end[0], end[1]), (end[0] - 15, end[1] - 23), (end[0] + 15, end[1] - 23)], fill=color)


def horizontal(a, b, color=MUTED, width=6):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    start, end = (ax + aw, ay + ah / 2), (bx, by + bh / 2)
    d.line((start[0], start[1], end[0], end[1]), fill=color, width=width)
    d.polygon([(end[0], end[1]), (end[0] - 23, end[1] - 15), (end[0] - 23, end[1] + 15)], fill=color)


def section(y, number, title):
    d.text((100, y), number, font=section_font, fill=ACCENT)
    d.text((190, y), title, font=section_font, fill=INK)
    d.line((100, y + 50, W - 100, y + 50), fill=LINE, width=3)


d.text((100, 80), "Workflow XRAG de bout en bout", font=title_font, fill=INK)
d.text((100, 180), "Ingestion, construction du graphe, recherche fondee sur les sources et inspection", font=subtitle_font, fill=MUTED)
d.rounded_rectangle((1880, 77, 2295, 155), radius=18, fill=ACCENT)
d.text((1977, 95), "XRAG", font=section_font, fill=WHITE)

section(280, "01", "Ingestion documentaire authentifiee")
a = box(100, 370, 420, 140, "Interface XRAG", "Espace authentifie", fill=PALE, border=SAGE)
b = box(650, 370, 490, 140, "Extraire le texte", "PDF.js  •  Mammoth  •  OCR")
c = box(1270, 370, 500, 140, "Valider l'import", "Limites  •  origine  •  SHA-256")
e = box(1900, 370, 400, 140, "Nettoyer et decouper", "~1 100 car.  •  chev. 140")
horizontal(a, b); horizontal(b, c); horizontal(c, e)

f = box(170, 650, 600, 155, "Creer les embeddings", "Nemotron 3 Embed 1B\n2 048 dimensions", fill=SOFT)
g = box(900, 650, 600, 155, "Extraire les faits", "Nemotron 3 Super\nEntites, relations et citations", fill=SOFT)
h = box(1630, 650, 600, 155, "Valider le graphe", "Schema, IDs, extremites\net citations justificatives", fill=SOFT)
arrow(e, g); horizontal(f, g, color=LINE); horizontal(g, h)

section(900, "02", "Persistance avec provenance")
i = box(170, 990, 820, 180, "Base durable D1", "Documents  •  passages  •  vecteurs\nentites  •  mentions  •  relations", fill=PALE, border=SAGE)
j = box(1120, 990, 520, 180, "Stockage d'objets R2", "Fichiers originaux", fill=PALE, border=SAGE)
k = box(1770, 990, 460, 180, "Miroir Neo4j", "Analyse locale optionnelle", fill=PALE, border=SAGE)
arrow(f, i); arrow(h, i); arrow(c, j)
d.text((1775, 1185), "export optionnel depuis D1", font=small_font, fill=MUTED)

section(1310, "03", "Reponse aux questions avec LangGraph")
q = box(100, 1400, 420, 155, "Question", "Choisir lexical, vectoriel,\ngraphe ou hybride", fill=SOFT)
api = box(650, 1400, 470, 155, "API de question", "Authentifier, valider et\nlimiter le debit", fill=SOFT)
ret = box(1250, 1400, 500, 155, "LangGraph  1  Rechercher", "Charger le corpus proprietaire\net choisir les preuves", fill=SOFT, border=ACCENT)
horizontal(q, api); horizontal(api, ret)

lex = box(190, 1720, 540, 140, "Branche lexicale", "BM25 : k1 = 1.2, b = 0.75")
vec = box(930, 1720, 540, 140, "Branche vectorielle", "Similarite cosinus > 0.30")
gra = box(1670, 1720, 540, 140, "Branche graphe", "8 graines et 2 sauts max.")
arrow(ret, vec); horizontal(lex, vec, color=LINE); horizontal(vec, gra, color=LINE)

fusion = box(410, 2020, 690, 165, "Fusionner et limiter", "RRF : Σ 1 / (60 + rang)\n6 passages, 3 par document max.", fill=PALE, border=SAGE)
gen = box(1300, 2020, 690, 165, "LangGraph  2  Generer", "6 affirmations max., liees aux\nIDs et citations exactes", fill=PALE, border=ACCENT)
arrow(lex, fusion); arrow(vec, fusion); arrow(gra, fusion); horizontal(fusion, gen)

val = box(410, 2330, 690, 165, "LangGraph  3  Valider", "Rejeter les IDs inconnus et les\ncitations absentes du passage", fill=PALE, border=ACCENT)
out = box(1300, 2330, 690, 165, "Reponse fondee", "Reponse  •  passages  •  chemins\navertissements  •  abstention", fill=PALE, border=SAGE)
arrow(gen, val); horizontal(val, out)

section(2610, "04", "Inspection, decouverte et cycle de vie")
box(100, 2700, 650, 150, "Inspection des preuves", "Ouvrir citations et documents", fill=SOFT)
box(875, 2700, 650, 150, "Decouverte", "Graphe, experts et recommandations", fill=SOFT)
box(1650, 2700, 650, 150, "Suppression coherente", "Originaux, derives et historique obsolete", fill=SOFT)
d.text((100, 2915), "Pilote academique prive  •  500 passages max.  •  Graphe heberge dans D1  •  Export Neo4j optionnel", font=small_font, fill=MUTED)

OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, quality=95, dpi=(180, 180))
print(OUT)
