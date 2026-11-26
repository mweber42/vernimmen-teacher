---
description: Préparer un chapitre avant lecture (fiche + questions)
argument-hint: <numéro de chapitre> [photo de la table détaillée]
---

Prépare le chapitre **$ARGUMENTS** du Vernimmen, en suivant `CLAUDE.md`.

1. **Plan.** Lance `python3 outils/prof.py chapitre <N>`. Si le chapitre n'existe pas, arrête-toi et dis-le. Si `data/questions/NN.json` ou `fiches/NN.md` existe déjà, demande avant d'écraser.
2. **Sections.**
   - Si une photo de la table détaillée est jointe, suis ses sections.
   - Sinon, déduis-les du titre et de la place du chapitre. Retiens-les pour la sortie terminal.
3. **Vérifications.** Contrôle ce qui a pu changer depuis 2016 sur ce sujet (liste de `CLAUDE.md`), sur des sources autorisées uniquement. Si tu utilises des chiffres actuels (taux, primes, fiscalité), donne-les avec leur source et la date. Si la recherche web est indisponible, marque `À vérifier` et dis-le.
4. **Calculs.** Écris `calculs/NN.py`. Il produit tous les chiffres de l'exemple et des questions de calcul. Exécute-le et reprends les résultats tels quels.
5. **Fiche.** Écris `fiches/NN.md` selon `modeles/fiche.md`, en 1 à 2 pages. Dépendances : rappel en une ligne des notions déjà vues (`notions_existantes`).
6. **Notions.** Ajoute les notions du chapitre dans `data/notions.json` (format décrit dans `README.md`), avec `niveau: "decouverte"`. Mets dans `depend_de` les seules dépendances réelles.
7. **Glossaire.** Ajoute les termes dans `data/glossaire.json` : FR, EN, définition courte, chapitre et notion. Pas de doublon d'un terme existant.
8. **Questions.** Écris `data/questions/NN.json` selon `modeles/questions.json` : 12 à 16 questions. Chaque lot contient au moins :
   - 3 `qcm`,
   - 2 `vrai-faux`,
   - 2 `calcul`,
   - 1 `ouverte`,
   - 1 `liaison` (vers un chapitre déjà vu, s'il y en a),
   - 1 `cas`,
   - 2 `carte`.

   Les distracteurs sont plausibles. Les questions portent sur l'état actuel. Une `explication` pour chaque question.
9. **Contrôle.** Lance `python3 outils/prof.py valider` et corrige jusqu'à obtenir `OK`.
10. **Suivi.**
    - Lance `python3 outils/prof.py statut <N> prepare`. Ajoute `--table-detaillee` si la photo a été fournie.
    - Ajoute une ligne à `PROGRESSION.md`.
    - Fais un commit `prepare: chapitre N`, puis un push.

**Sortie terminal : 5 lignes maximum.**
- Ligne 1 : `Ch. N prêt : fiches/NN.md · X questions`.
- Si les sections ont été supposées : une ligne qui commence par `Sections supposées :`.
- Puis ce qu'il faut surveiller pendant la lecture.
- Signale tout écart d'étape, push compris.
