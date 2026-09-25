# Pipeline de responsabilite XRAG

Ce document repond a trois questions pour chaque etape : qui agit, quelle technologie a vraiment ete utilisee et quel resultat est produit. "Outil" designe le logiciel deterministe du projet. "Modele" designe un modele NVIDIA appris dont la sortie doit etre validee. L'utilisateur reste responsable des droits sur les sources, de la question et du jugement final.

## A. Indexation des documents

1. **Vous choisissez la source.** Vous selectionnez le fichier, le titre et l'option OCR anglais. Vous etes responsable de l'autorisation de traiter le document.
2. **Les outils navigateur lisent le fichier.** React appelle PDF.js 6.3 pour PDF, Mammoth 1.12 pour DOCX, `File.text()` pour TXT/MD/CSV/JSON et Tesseract.js 7 pour l'OCR anglais. Le code se trouve dans `lib/parse-file.ts`.
3. **Le code XRAG authentifie et valide.** La route documents lit l'identite Sites, controle l'origine, applique Zod, limite les extensions, la taille, les pages et le texte, puis applique cinq imports par minute et par proprietaire.
4. **Le code XRAG nettoie et decoupe.** `lib/core.ts` normalise le texte et produit des passages d'environ 1 100 caracteres avec environ 140 de chevauchement, sans traverser une page, pour 64 passages maximum par document.
5. **Le modele d'embedding cree les vecteurs.** `nvidia/nemotron-3-embed-1b` recoit `input_type=passage`. Les vecteurs verifies ont 2 048 valeurs et les requetes utilisent des lots de 16.
6. **Le modele generatif propose les faits.** `nvidia/nemotron-3-super-120b-a12b` recoit quatre passages par lot et renvoie un JSON d'entites, relations typees et citations exactes.
7. **Le code XRAG valide la proposition.** Zod controle le schema. Le code controle les IDs, les entites source et cible, la presence des noms, les extremites et les citations. Une sortie structuree incorrecte obtient une seule tentative de correction.
8. **D1 et R2 persistent l'index.** R2 stocke les octets originaux. D1 stocke documents, passages, vecteurs JSON, entites, mentions et relations avec preuve. Le lot D1 est atomique. Une compensation R2 est tentee si D1 echoue.

## B. Reponse aux questions

9. **Vous posez la question et choisissez le mode.** Les choix sont lexical, vectoriel, graphe et hybride.
10. **Le code XRAG protege l'API.** `/api/ask` authentifie, controle l'origine, valide une question de 3 a 2 000 caracteres et limite a 12 questions par minute et par proprietaire.
11. **LangGraph demarre la machine a etats.** `@langchain/langgraph` 1.4 execute `START -> retrieve -> generate -> validate -> END` dans `lib/workflow.ts`.
12. **Le modele d'embedding represente la question.** Les modes vectoriel et hybride utilisent Nemotron 3 Embed 1B avec `input_type=query`. Un changement de modele exige la reindexation.
13. **Le code XRAG retrouve les candidats.** `lib/core.ts` execute BM25 avec `k1=1.2`, `b=0.75`, le cosinus au-dessus de `0.30` et un parcours de huit graines et deux sauts maximum. Aucun retriever LangChain preconstruit n'est utilise.
14. **Le code XRAG fusionne et limite.** RRF additionne `1/(60+rang)`. Le contexte final contient six passages maximum et trois par document. Le code attribue les IDs `S1`, `S2`, etc.
15. **Le modele generatif propose les affirmations.** Nemotron 3 Super recoit la question et les passages. Le prompt autorise six affirmations JSON maximum et exige les IDs plus une citation exacte par reference.
16. **Le code XRAG valide ou s'abstient.** `validateClaims` rejette les IDs inconnus et les citations absentes. Si aucune affirmation valide ne reste, XRAG renvoie une abstention pour preuve insuffisante.
17. **D1 sauvegarde le resultat.** La table `queries` stocke la reponse complete, le mode, le proprietaire et la date.
18. **Les outils navigateur affichent les preuves.** React montre la reponse, les passages, chemins, avertissements, duree et etapes. Vous ouvrez les citations et jugez si la preuve soutient la reponse.

## C. Inspection et cycle de vie

19. **Vous choisissez l'action.** Inspection, telechargement, export, suppression de l'historique ou suppression du document.
20. **Le code XRAG applique les droits et le nettoyage.** Chaque route filtre par proprietaire. La suppression retire les donnees dependantes, les entites orphelines et l'historique qui pourrait citer une preuve supprimee.
21. **L'infrastructure applique l'operation.** R2 sert ou supprime les fichiers. D1 lit ou supprime les preuves structurees. Neo4j 5.26 Community reste un miroir local optionnel et ne repond pas aux questions du site deploye.

## Regle de responsabilite

- **Vous :** documents autorises, question, mode, inspection et jugement final.
- **Outils navigateur :** lecture des fichiers et presentation des resultats.
- **Code XRAG :** authentification, validation, classement, fusion, stockage, suppression et controle du modele.
- **Modeles NVIDIA :** embeddings et propositions de structures ou affirmations. Ils ne valident pas leur propre sortie.
- **D1, R2, Workers et Sites :** persistance et hebergement. Le stockage ne raisonne pas.

XRAG n'entraine et ne fine-tune aucun modele. Neo4j n'est pas dans le chemin de requete heberge. Le projet n'implemente pas le pipeline Microsoft GraphRAG complet avec resumes de communautes.
