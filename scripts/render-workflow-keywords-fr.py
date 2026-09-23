from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "xrag-workflow-keywords-fr.png"
W, H = 2400, 3900
BG, INK, MUTED = "#F8F6F0", "#272725", "#62645F"
ACCENT, SAGE, LINE, WHITE = "#A94F36", "#4A6653", "#C8C4B8", "#FFFFFF"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
title_font = ImageFont.truetype(BOLD, 74)
subtitle_font = ImageFont.truetype(FONT, 29)
card_title_font = ImageFont.truetype(BOLD, 30)
term_font = ImageFont.truetype(BOLD, 24)
body_font = ImageFont.truetype(FONT, 23)
footer_font = ImageFont.truetype(FONT, 20)

CATEGORIES = [
    ("01  SYSTEME ET ACCES", [
        ("XRAG", "La plateforme : RAG enrichi par un graphe de connaissances."),
        ("RAG", "Retrouve des passages avant que le LLM redige."),
        ("GraphRAG", "Ajoute relations d'entites et chemins a la recherche."),
        ("Interface authentifiee", "Espace prive pour imports, questions et inspection."),
        ("Corpus proprietaire", "Documents et derives d'un utilisateur authentifie."),
        ("Route API", "Point d'entree serveur qui valide et execute."),
        ("Limite de debit", "Borne les requetes par proprietaire et periode."),
    ]),
    ("02  INGESTION DOCUMENTAIRE", [
        ("PDF.js", "Extrait le texte des pages PDF dans le navigateur."),
        ("Mammoth", "Extrait le contenu lisible des fichiers DOCX."),
        ("OCR", "Transforme le texte d'un scan en caracteres."),
        ("SHA-256", "Produit une empreinte stable pour les doublons."),
        ("Deduplication", "Rejette un contenu repete dans le meme espace."),
        ("Nettoyage", "Normalise le texte avant l'indexation."),
        ("Chunk / passage", "Segment consultable d'environ 1 100 caracteres."),
        ("Chevauchement", "Repete environ 140 caracteres entre passages."),
    ]),
    ("03  MODELES ET EXTRACTION", [
        ("LLM", "Modele de langage pour extraction et generation."),
        ("NVIDIA NIM", "API de modeles appelee cote serveur."),
        ("Nemotron 3 Embed 1B", "Cree des vecteurs de 2 048 dimensions."),
        ("Embedding", "Representation numerique du sens d'un texte."),
        ("Nemotron 3 Super", "Extrait les faits et genere les affirmations."),
        ("Entite", "Noeud : personne, organisation, concept ou projet."),
        ("Relation", "Arete typee reliant deux entites."),
        ("Mention", "Lien entre une entite et son passage de preuve."),
        ("Citation justificative", "Texte exact soutenant un fait ou une affirmation."),
        ("Validation schema / extremites", "Controle forme et entites reliees."),
    ]),
    ("04  STOCKAGE ET PROVENANCE", [
        ("Provenance", "Trace d'une reponse ou relation vers sa source."),
        ("D1", "SQL heberge pour passages, vecteurs et graphe."),
        ("Metadonnees", "Identifiants, proprietaire, hash, statut et dates."),
        ("Graphe de proprietes", "Connaissance sous forme de noeuds et aretes attribues."),
        ("R2", "Stockage des fichiers originaux."),
        ("Stockage d'objets", "Conserve les fichiers par cle, pas par lignes SQL."),
        ("Miroir Neo4j", "Copie locale optionnelle; hors du chemin heberge."),
        ("Export", "Copie unidirectionnelle, pas une synchronisation."),
    ]),
    ("05  LANGGRAPH ET RECHERCHE", [
        ("LangGraph", "Execute rechercher, generer et valider."),
        ("Recherche lexicale", "Compare les mots de la question et des passages."),
        ("BM25", "Classe par frequence, rarete et longueur."),
        ("Recherche vectorielle", "Compare la question aux passages par le sens."),
        ("Similarite cosinus", "Mesure la direction relative de deux vecteurs."),
        ("Seuil", "Score vectoriel minimum accepte : > 0.30."),
        ("Parcours du graphe", "Suit les relations vers des preuves."),
        ("Graine", "Entite de depart; huit maximum."),
        ("Saut", "Une relation traversee; deux maximum."),
        ("Recherche hybride", "Combine lexical, vectoriel et graphe."),
    ]),
    ("06  FUSION ET PREUVES", [
        ("RRF", "Fusion des rangs : somme de 1 / (60 + rang)."),
        ("Rang", "Position d'un element dans une liste de resultats."),
        ("Preuves limitees", "Six passages, avec trois par document maximum."),
        ("Affirmation", "Phrase factuelle liee aux preuves fournies."),
        ("ID de source", "Identifiant d'un passage disponible au modele."),
        ("Citation exacte", "Texte qui doit apparaitre dans le passage."),
        ("Validation", "Rejette IDs inconnus et citations absentes."),
    ]),
    ("07  SORTIE ET EXPLICABILITE", [
        ("Reponse fondee", "Reponse liee aux passages et chemins."),
        ("Chemin du graphe", "Suite ordonnee d'entites et de relations."),
        ("Avertissement", "Signale une limite recuperable."),
        ("Abstention", "Refuse quand la preuve valide est insuffisante."),
        ("Inspection", "Ouvre citations et documents originaux."),
        ("Exploration", "Affiche directement entites et relations."),
        ("Expert candidat", "Personne liee a un domaine par une preuve."),
        ("Recommandation", "Document ou projet propose par les liens."),
    ]),
    ("08  CYCLE DE VIE ET PORTEE", [
        ("Suppression coherente", "Retire originaux et donnees derivees."),
        ("Entite orpheline", "Entite sans mention apres suppression."),
        ("Historique obsolete", "Reponse qui pourrait citer une preuve supprimee."),
        ("Pilote academique prive", "PFE teste pour evaluation privee."),
        ("Limite de 500 passages", "Borne stockage, latence et cout."),
    ]),
]

im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)


def wrap(text, font, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or d.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current); current = word
    if current:
        lines.append(current)
    return lines


def card_height(items, width):
    height = 86
    for _, definition in items:
        height += 35 + len(wrap(definition, body_font, width - 58)) * 31 + 16
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


d.text((100, 76), "Carte des mots-cles du workflow XRAG", font=title_font, fill=INK)
d.text((100, 170), "Definitions simples de tous les termes techniques du workflow", font=subtitle_font, fill=MUTED)
d.rounded_rectangle((1880, 72, 2295, 150), radius=18, fill=ACCENT)
d.text((1975, 91), "XRAG", font=card_title_font, fill=WHITE)
d.line((100, 235, W - 100, 235), fill=LINE, width=3)

column_x, column_y = [100, 1220], [285, 285]
for index, (title, items) in enumerate(CATEGORIES):
    column = min(range(2), key=lambda i: column_y[i])
    height = draw_card(column_x[column], column_y[column], 1080, title, items, [ACCENT, SAGE][index % 2])
    column_y[column] += height + 34

assert max(column_y) < H - 140, "Les cartes depassent le canevas"
d.line((100, H - 125, W - 100, H - 125), fill=LINE, width=3)
d.text((100, H - 88), "Explications : docs/xrag-workflow-keywords-fr.md  |  Workflow : docs/xrag-workflow-fr.png", font=footer_font, fill=MUTED)
d.text((100, H - 52), "Les valeurs indiquees sont les limites configurees du pilote XRAG.", font=footer_font, fill=MUTED)

OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, quality=95, dpi=(180, 180))
print(OUT)
