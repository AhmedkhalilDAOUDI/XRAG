# Glossaire du workflow XRAG

Ce glossaire explique en francais le vocabulaire technique du workflow XRAG. Il decrit le pilote academique implemente. Il ne pretend pas que chaque technologie citee sert directement le chemin de requete heberge.

## 1. Systeme et acces

**XRAG** est le nom de la plateforme. Elle combine la generation augmentee par la recherche et un graphe de connaissances pour utiliser a la fois les passages textuels et les relations entre concepts.

**RAG** retrouve des preuves dans une collection avant que le LLM redige une reponse. Les passages recuperes limitent la reponse et fournissent les citations.

**GraphRAG** ajoute des donnees de graphe a la recherche. XRAG peut suivre des chemins entite-relation en plus des mots et vecteurs. Le projet est un workflow borne de graphe de proprietes, pas l'implementation complete du pipeline Microsoft GraphRAG.

**Interface authentifiee** designe l'espace web prive dans lequel l'utilisateur charge des documents, pose des questions et inspecte les preuves.

**Espace ou corpus du proprietaire** regroupe les documents et donnees derivees d'une identite authentifiee. Les filtres proprietaire evitent les acces croises.

**Route API** designe un point d'entree serveur comme `/api/ask`. Elle valide la requete, applique les controles et renvoie des donnees structurees.

**Limite de debit** borne le nombre d'appels d'un proprietaire pendant une periode. Elle protege le service et le quota fournisseur.

## 2. Ingestion documentaire

**Document accepte** est un fichier PDF, DOCX, TXT, MD, CSV ou JSON que XRAG sait lire. CSV et JSON restent du texte dans cette version.

**PDF.js** extrait le texte des pages PDF dans le navigateur.

**Mammoth** extrait le contenu lisible des fichiers DOCX sans chercher a reproduire toute la mise en page Word.

**OCR** transforme le texte visible dans une image ou un scan en caracteres. XRAG utilise Tesseract anglais en solution de secours.

**Validation serveur** controle taille, type, proprietaire, limites et champs obligatoires avant la persistance.

**SHA-256** est une fonction de hachage cryptographique. Elle produit une empreinte stable des octets pour detecter un doublon.

**Deduplication** rejette un fichier dont l'empreinte existe deja dans le meme espace.

**Nettoyage** normalise le texte extrait et reduit les espaces ou caracteres inutilisables.

**Chunk ou passage** est un segment borne utilise pour la recherche et la citation. XRAG vise environ 1 100 caracteres.

**Chevauchement** repete environ 140 caracteres entre passages voisins pour proteger les faits proches d'une coupure.

## 3. Modeles et extraction

**LLM** est un grand modele de langage utilise pour l'extraction structuree et la generation de reponses.

**NVIDIA NIM** est l'API de modeles utilisee par XRAG. La cle reste cote serveur et ne doit jamais entrer dans Git ou le navigateur.

**Nemotron 3 Embed 1B** est le modele d'embedding configure. Il transforme passages et questions en vecteurs de 2 048 dimensions.

**Embedding** est une representation numerique du sens d'un texte. Des textes proches par le sens doivent produire des directions proches.

**Dimension vectorielle** est le nombre de coordonnees. XRAG enregistre 2 048 nombres par vecteur du modele configure.

**Nemotron 3 Super** est le modele generatif configure. Il extrait les faits du graphe et genere des affirmations a partir des preuves.

**Entite** est un noeud du graphe : personne, organisation, technologie, procedure, projet ou concept.

**Relation** est une connexion typee entre deux entites, par exemple `LEADS` ou `DEPENDS_ON`.

**Mention** relie une entite au passage ou elle apparait et maintient le chemin vers la preuve.

**Citation justificative** est le texte exact du passage qui soutient une relation ou une affirmation.

**Schema** definit la forme et les types obligatoires d'une sortie de modele.

**Validation des extremites** verifie que la source et la cible d'une relation correspondent a des entites connues.

## 4. Persistance et provenance

**Provenance** enregistre l'origine d'un fait ou d'une reponse. XRAG relie documents, passages, entites, relations, citations et reponses.

**D1** est la base SQL hebergee. Elle stocke metadonnees, passages, vecteurs, entites, mentions, relations et historique.

**Base durable** signifie que les enregistrements survivent aux requetes et aux redemarrages.

**Metadonnees** decrivent un objet : identifiant, titre, proprietaire, empreinte, statut et date.

**Graphe de proprietes** represente la connaissance par des noeuds et aretes portant des attributs. XRAG le stocke dans des tables D1.

**R2** est le stockage d'objets des fichiers originaux. D1 conserve les references et donnees derivees.

**Stockage d'objets** conserve des fichiers complets adresses par des cles, contrairement aux lignes SQL structurees.

**Neo4j** est une base de graphes utilisee comme miroir local optionnel. Elle ne sert pas le chemin de requete deploye.

**Miroir ou export** est une copie unidirectionnelle du graphe D1 vers Neo4j, pas une synchronisation automatique.

## 5. LangGraph et recherche

**LangGraph** orchestre la machine a etats de question-reponse. XRAG execute recherche, generation et validation.

**Mode de recherche** choisit lexical, vectoriel, graphe ou hybride.

**Recherche lexicale** compare les mots de la question et des passages. Elle est forte sur les noms et termes exacts.

**BM25** classe selon frequence, rarete et longueur. `k1 = 1.2` controle la saturation et `b = 0.75` normalise la longueur.

**Recherche vectorielle** embedde la question et compare son vecteur a ceux des passages.

**Similarite cosinus** mesure l'angle entre deux vecteurs. Une grande valeur indique des directions semantiques proches.

**Seuil de similarite** est le score vectoriel minimum accepte. Le workflow utilise une valeur superieure a `0.30`.

**Parcours du graphe** suit les relations depuis les entites correspondantes vers les noeuds et passages voisins.

**Graine** est une entite de depart. XRAG utilise huit graines au maximum.

**Saut** est une relation traversee. XRAG limite le parcours a deux sauts.

**Recherche hybride** combine les listes lexicale, vectorielle et graphe.

**RRF** fusionne les rangs avec `somme(1 / (60 + rang))`. Les scores bruts des branches n'ont pas besoin de partager une echelle.

**Selection limitee des preuves** restreint le contexte a six passages, avec trois passages maximum par document.

## 6. Generation, validation et sortie

**Affirmation** est une phrase factuelle produite pour la reponse. XRAG en demande six au maximum et exige une preuve.

**Identifiant de source** designe un passage recupere. La validation rejette un identifiant absent de l'ensemble fourni au modele.

**Citation exacte** est un fragment qui doit apparaitre mot pour mot dans le passage cite. Sa presence ne prouve pas a elle seule toute l'implication semantique.

**Reponse fondee sur les sources** est une reponse liee a des passages et chemins plutot qu'a la seule memoire du modele.

**Validation des citations** controle les identifiants et la presence des extraits.

**Chemin du graphe** est une suite ordonnee d'entites et de relations montrant une connexion.

**Avertissement** signale une limite recuperable, comme une branche vectorielle indisponible ou une citation rejetee.

**Abstention** signifie que XRAG ne possede pas assez de preuves valides pour repondre.

## 7. Inspection, decouverte et cycle de vie

**Inspection des preuves** permet d'ouvrir les passages et documents originaux derriere une reponse.

**Historique sauvegarde** conserve les questions et sorties du proprietaire authentifie.

**Exploration du graphe** affiche les entites et relations pour inspection directe.

**Expert candidat** est une personne associee a un domaine par une preuve documentaire. C'est un candidat documente, pas une certification independante.

**Recommandation** est un document, une procedure ou un projet propose a partir d'entites et relations partagees.

**Suppression coherente** retire le fichier original ainsi que passages, vecteurs, mentions et relations derives.

**Entite orpheline** est une entite sans mention restante apres suppression d'un document.

**Historique obsolete** est une reponse sauvegardee qui pourrait citer une preuve supprimee.

**Pilote academique prive** decrit la limite de la version : un PFE teste pour evaluation privee, pas un produit d'entreprise certifie.

**Limite de 500 passages** borne le stockage, le scan vectoriel en memoire, la latence et le cout. Un plus grand corpus demande index ANN, file d'ingestion, tests de charge, sauvegarde et droits propres a l'organisation.
