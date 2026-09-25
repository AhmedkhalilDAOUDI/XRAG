from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 3600, 5920
BG, INK, MUTED = "#F8F6F0", "#272725", "#62645F"
ACCENT, SAGE, BLUE, PURPLE, GOLD = "#A94F36", "#4A6653", "#426B78", "#6B5876", "#8A6A2D"
LINE, WHITE = "#C8C4B8", "#FFFFFF"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
title_font = ImageFont.truetype(BOLD, 78)
subtitle_font = ImageFont.truetype(FONT, 31)
lane_font = ImageFont.truetype(BOLD, 28)
phase_font = ImageFont.truetype(BOLD, 34)
step_title_font = ImageFont.truetype(BOLD, 26)
step_body_font = ImageFont.truetype(FONT, 21)
number_font = ImageFont.truetype(BOLD, 21)
small_font = ImageFont.truetype(FONT, 20)
footer_font = ImageFont.truetype(BOLD, 20)

LANE_COLORS = [ACCENT, BLUE, SAGE, PURPLE, GOLD]
LANE_X = [105, 802, 1499, 2196, 2893]
LANE_W = 602

COPY = {
    "en": {
        "out": "xrag-actor-pipeline.png",
        "title": "XRAG pipeline: who does each step?",
        "subtitle": "The exact hand-offs between you, browser tools, deterministic XRAG code, NVIDIA models, and data infrastructure",
        "lanes": [
            ("YOU", "Intent and judgment"),
            ("BROWSER TOOLS", "Interface and file reading"),
            ("XRAG CODE", "Rules and orchestration"),
            ("NVIDIA MODELS", "Learned language operations"),
            ("DATA & INFRA", "Persistence and hosting"),
        ],
        "phases": [(390, "A", "DOCUMENT INDEXING"), (2440, "B", "QUESTION ANSWERING"), (4950, "C", "INSPECTION AND LIFECYCLE")],
        "steps": [
            (1, 0, 520, "Choose the source", "Select file, title and OCR option.\nYou decide what may be indexed."),
            (2, 1, 750, "Read the file", "React interface + PDF.js 6.3,\nMammoth 1.12, File.text();\nTesseract.js 7 for English OCR."),
            (3, 2, 980, "Authenticate and validate", "Sites identity header, origin check,\nZod request schema, file/type limits,\n5 imports per minute. documents route."),
            (4, 2, 1210, "Clean and chunk", "lib/core.ts: normalize spacing;\n~1,100 characters, ~140 overlap;\n64 passages per document maximum."),
            (5, 3, 1440, "Create passage embeddings", "nvidia/nemotron-3-embed-1b;\ninput_type=passage; 2,048 dimensions;\nbatches of 16."),
            (6, 3, 1670, "Propose graph facts", "nvidia/nemotron-3-super-120b-a12b;\n4 passages per batch; JSON entities,\nrelations and exact quotations."),
            (7, 2, 1900, "Validate model output", "Zod schema + exact passage IDs, names,\nrelation endpoints and quotations;\none correction attempt for malformed output."),
            (8, 4, 2130, "Persist the index", "R2: original file. D1: documents, chunks,\nvectors, entities, mentions and edges.\nD1 batch is atomic; R2 uses compensation."),
            (9, 0, 2570, "Ask and choose a mode", "Write the question and choose lexical,\nvector, graph or hybrid. You later judge\nwhether the evidence answers the question."),
            (10, 2, 2800, "Guard the question API", "/api/ask: Sites identity, origin check,\nZod 3-2,000 characters and 12 questions\nper minute for each owner."),
            (11, 2, 3030, "Start LangGraph", "@langchain/langgraph 1.4: explicit state;\nSTART -> retrieve -> generate\n-> validate -> END."),
            (12, 3, 3260, "Embed the question", "Nemotron 3 Embed 1B; input_type=query.\nOnly vector and hybrid modes call it.\nModel mismatch forces re-indexing."),
            (13, 2, 3490, "Retrieve candidates", "Custom lib/core.ts: BM25 k1=1.2 b=.75;\ncosine > .30; graph up to 8 seeds\nand 2 hops. No prebuilt retriever."),
            (14, 2, 3720, "Fuse and bound evidence", "RRF = sum 1/(60+rank); at most\n6 passages and 3 per document.\nCode assigns source IDs S1, S2, ..."),
            (15, 3, 3950, "Generate grounded claims", "Nemotron 3 Super; evidence-only prompt;\nJSON with at most 6 claims, source IDs\nand one exact quote for each citation."),
            (16, 2, 4180, "Validate or abstain", "validateClaims checks known source IDs and\nexact quote presence. Invalid claims are\nremoved; no valid claim means abstention."),
            (17, 4, 4410, "Save the result", "D1 queries table stores the complete answer,\nmode and time for the authenticated owner."),
            (18, 1, 4640, "Show inspectable evidence", "React workspace displays answer, passages,\ngraph paths, warnings and steps.\nYou open citations and judge usefulness."),
            (19, 0, 5080, "Choose a lifecycle action", "Inspect a source, download the original,\nexport the graph, clear history or delete\na document."),
            (20, 2, 5310, "Enforce ownership and cleanup", "Owner-filtered API routes; coherent deletion\nremoves derived records, orphan entities\nand saved history that could become stale."),
            (21, 4, 5540, "Apply the data operation", "R2 serves/deletes originals. D1 reads/deletes\nstructured evidence. Neo4j 5.26 is only an\noptional local export mirror."),
        ],
        "footer": "NOT USED: model training or fine-tuning  •  Neo4j in the hosted query path  •  the full Microsoft community-summary GraphRAG pipeline",
    },
    "fr": {
        "out": "xrag-actor-pipeline-fr.png",
        "title": "Pipeline XRAG : qui fait chaque etape ?",
        "subtitle": "Les passages exacts entre vous, les outils navigateur, le code XRAG, les modeles NVIDIA et l'infrastructure",
        "lanes": [
            ("VOUS", "Intention et jugement"),
            ("OUTILS NAVIGATEUR", "Interface et lecture des fichiers"),
            ("CODE XRAG", "Regles et orchestration"),
            ("MODELES NVIDIA", "Operations apprises sur le langage"),
            ("DONNEES & INFRA", "Persistance et hebergement"),
        ],
        "phases": [(390, "A", "INDEXATION DES DOCUMENTS"), (2440, "B", "REPONSE AUX QUESTIONS"), (4950, "C", "INSPECTION ET CYCLE DE VIE")],
        "steps": [
            (1, 0, 520, "Choisir la source", "Choisir fichier, titre et option OCR.\nVous decidez ce qui peut etre indexe."),
            (2, 1, 750, "Lire le fichier", "Interface React + PDF.js 6.3,\nMammoth 1.12, File.text();\nTesseract.js 7 pour l'OCR anglais."),
            (3, 2, 980, "Authentifier et valider", "Identite Sites, controle d'origine, schema Zod,\nlimites fichier/type et 5 imports/minute.\nRoute documents."),
            (4, 2, 1210, "Nettoyer et decouper", "lib/core.ts : espaces normalises;\n~1 100 caracteres, ~140 de chevauchement;\n64 passages maximum par document."),
            (5, 3, 1440, "Creer les embeddings", "nvidia/nemotron-3-embed-1b;\ninput_type=passage; 2 048 dimensions;\nlots de 16."),
            (6, 3, 1670, "Proposer les faits du graphe", "nvidia/nemotron-3-super-120b-a12b;\n4 passages par lot; JSON avec entites,\nrelations et citations exactes."),
            (7, 2, 1900, "Valider la sortie du modele", "Schema Zod + IDs, noms, extremites et\ncitations exactes; une correction maximum\npour une sortie mal formee."),
            (8, 4, 2130, "Persister l'index", "R2 : fichier original. D1 : documents, passages,\nvecteurs, entites, mentions et relations.\nLot D1 atomique; compensation pour R2."),
            (9, 0, 2570, "Poser la question", "Ecrire la question et choisir lexical, vectoriel,\ngraphe ou hybride. Vous jugez ensuite\nsi la preuve repond reellement."),
            (10, 2, 2800, "Proteger l'API question", "/api/ask : identite Sites, origine, Zod\n3-2 000 caracteres et 12 questions/minute\npar proprietaire."),
            (11, 2, 3030, "Demarrer LangGraph", "@langchain/langgraph 1.4 : etat explicite;\nSTART -> retrieve -> generate\n-> validate -> END."),
            (12, 3, 3260, "Embedder la question", "Nemotron 3 Embed 1B; input_type=query.\nSeulement pour vectoriel et hybride.\nUn changement de modele impose reindexation."),
            (13, 2, 3490, "Retrouver les candidats", "lib/core.ts personnalise : BM25 k1=1.2 b=.75;\ncosinus > .30; graphe avec 8 graines\net 2 sauts max. Aucun retriever preconstruit."),
            (14, 2, 3720, "Fusionner et limiter", "RRF = somme 1/(60+rang); au plus\n6 passages et 3 par document.\nLe code attribue S1, S2, ..."),
            (15, 3, 3950, "Generer les affirmations", "Nemotron 3 Super; prompt limite aux preuves;\nJSON de 6 affirmations max., IDs de source\net une citation exacte par reference."),
            (16, 2, 4180, "Valider ou s'abstenir", "validateClaims controle les IDs connus et les\ncitations presentes. Les affirmations invalides\nsont retirees; aucune valide = abstention."),
            (17, 4, 4410, "Sauvegarder le resultat", "La table D1 queries stocke reponse complete,\nmode et date pour le proprietaire."),
            (18, 1, 4640, "Afficher les preuves", "L'interface React montre reponse, passages,\nchemins, avertissements et etapes.\nVous ouvrez les citations et jugez."),
            (19, 0, 5080, "Choisir une action", "Inspecter, telecharger, exporter le graphe,\neffacer l'historique ou supprimer\nun document."),
            (20, 2, 5310, "Controler et nettoyer", "Routes filtrees par proprietaire; la suppression\nretire derives, entites orphelines et historique\nqui pourrait devenir obsolete."),
            (21, 4, 5540, "Appliquer l'operation", "R2 sert/supprime les originaux. D1 lit/supprime\nles preuves structurees. Neo4j 5.26 reste\nun miroir local optionnel."),
        ],
        "footer": "NON UTILISE : entrainement ou fine-tuning  •  Neo4j dans le chemin heberge  •  pipeline Microsoft GraphRAG complet avec resumes de communautes",
    },
}


def make(language):
    copy = COPY[language]
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    def wrap(text, font, max_width):
        lines = []
        for source_line in text.splitlines():
            words, current = source_line.split(), ""
            for word in words:
                candidate = f"{current} {word}".strip()
                if not current or d.textlength(candidate, font=font) <= max_width:
                    current = candidate
                else:
                    lines.append(current); current = word
            lines.append(current)
        return lines

    d.text((105, 62), copy["title"], font=title_font, fill=INK)
    d.text((105, 157), copy["subtitle"], font=subtitle_font, fill=MUTED)
    d.rounded_rectangle((3160, 57, 3495, 137), radius=18, fill=ACCENT)
    d.text((3235, 78), "XRAG", font=lane_font, fill=WHITE)

    for i, ((name, role), color, x) in enumerate(zip(copy["lanes"], LANE_COLORS, LANE_X)):
        d.rounded_rectangle((x, 245, x + LANE_W, H - 185), radius=25, fill="#FFFFFF", outline=LINE, width=2)
        d.rounded_rectangle((x, 245, x + LANE_W, 350), radius=25, fill=color)
        d.rectangle((x, 315, x + LANE_W, 350), fill=color)
        d.text((x + 24, 267), name, font=lane_font, fill=WHITE)
        d.text((x + 24, 312), role, font=small_font, fill=WHITE)

    for y, letter, label in copy["phases"]:
        d.rounded_rectangle((105, y, 165, y + 52), radius=12, fill=ACCENT)
        d.text((123, y + 10), letter, font=lane_font, fill=WHITE)
        d.text((190, y + 7), label, font=phase_font, fill=INK)
        d.line((190, y + 57, W - 105, y + 57), fill=LINE, width=3)

    boxes = {}
    for number, lane, y, title, body in copy["steps"]:
        x = LANE_X[lane] + 22
        width, height = LANE_W - 44, 188
        color = LANE_COLORS[lane]
        d.rounded_rectangle((x, y, x + width, y + height), radius=20, fill="#F8F6F0", outline=color, width=3)
        d.ellipse((x + 18, y + 18, x + 58, y + 58), fill=color)
        num = str(number)
        tw = d.textlength(num, font=number_font)
        d.text((x + 38 - tw / 2, y + 27), num, font=number_font, fill=WHITE)
        title_lines = wrap(title, step_title_font, width - 95)
        d.multiline_text((x + 75, y + 18), "\n".join(title_lines), font=step_title_font, fill=INK, spacing=4)
        body_y = y + 62 + max(0, len(title_lines) - 1) * 30
        d.multiline_text((x + 22, body_y), body, font=step_body_font, fill=MUTED, spacing=7)
        boxes[number] = (x, y, width, height)

    links = [(1,2),(2,3),(3,4),(4,5),(4,6),(5,7),(6,7),(7,8),(9,10),(10,11),(11,12),(12,13),(11,13),(13,14),(14,15),(15,16),(16,17),(17,18),(19,20),(20,21)]
    for start_num, end_num in links:
        a, b = boxes[start_num], boxes[end_num]
        ax, ay, aw, ah = a; bx, by, bw, bh = b
        start = (ax + aw / 2, ay + ah)
        end = (bx + bw / 2, by)
        mid = (start[1] + end[1]) / 2
        color = "#777873"
        d.line((start[0], start[1], start[0], mid, end[0], mid, end[0], end[1] - 14), fill=color, width=5, joint="curve")
        d.polygon([(end[0], end[1]), (end[0] - 13, end[1] - 21), (end[0] + 13, end[1] - 21)], fill=color)

    d.rounded_rectangle((105, H - 145, W - 105, H - 70), radius=16, fill="#EEEAE0", outline=LINE, width=2)
    footer_lines = wrap(copy["footer"], footer_font, W - 280)
    d.multiline_text((140, H - 126), "\n".join(footer_lines), font=footer_font, fill=INK, spacing=5)
    out = ROOT / "docs" / copy["out"]
    im.save(out, quality=95, dpi=(180, 180))
    print(out)


make("en")
make("fr")
