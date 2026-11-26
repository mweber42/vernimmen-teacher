---
description: Générer tout le contenu d'un chapitre (cours, fiche, questions, notions, glossaire, depuis 2016)
argument-hint: <numéro de chapitre> [photo de la table détaillée]
---

Prépare le contenu du chapitre **$ARGUMENTS**, en suivant `CLAUDE.md`.

**Prérequis.** Le format des fichiers de contenu et le schéma de validation doivent avoir été validés par Marine (fin de phase 0 et phase 1). Sinon, arrête-toi et dis-le en une ligne.

1. **Plan.** Lis le chapitre dans `content/livre.json` : titre, partie, titre de partie, pages. S'il n'existe pas, arrête-toi. Si du contenu existe déjà pour ce chapitre, demande avant d'écraser.
2. **Sections.** Suis la photo de la table détaillée si elle est jointe. Sinon, déduis les sections du titre et de la place du chapitre, et retiens-les pour les signaler.
3. **Vérifications.** Contrôle ce qui a changé depuis 2016 (liste de `CLAUDE.md`), sur des sources autorisées uniquement, avec la date de consultation. Si la recherche est impossible, marque `À vérifier` et dis-le.
4. **Calculs.** Écris le script Python du chapitre, qui produit tous les chiffres du cours et des questions. Exécute-le et reprends ses résultats tels quels.
5. **Contenu.** Rédige :
   - le cours ;
   - la fiche, une page maximum ;
   - 10 à 20 questions, avec au moins une de chaque type : QCM, vrai/faux, calcul, ouverte, mini-cas, liaison ;
   - les notions et leurs dépendances (uniquement les dépendances réelles) ;
   - les termes du glossaire (sans doublons) ;
   - la rubrique « Ce qui a changé depuis 2016 ».
6. **Validation.** Lance la vérification du schéma et corrige jusqu'à ce qu'elle passe.
7. **Git.** Fais un commit `prepare: chapitre N`, puis un push.

**Sortie : 5 lignes maximum.**
- Ligne 1 : `Ch. N prêt : X questions, Y notions`.
- Si les sections ont été supposées : une ligne `Sections supposées : …`.
- Puis ce qu'il faut surveiller pendant la lecture.
- Signale tout écart d'étape.
