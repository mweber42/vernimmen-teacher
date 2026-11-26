---
description: Quiz après lecture (8 à 12 questions, correction immédiate)
argument-hint: <numéro de chapitre | mix>
---

Fais passer un quiz sur **$ARGUMENTS**, en suivant `CLAUDE.md`.

1. **Réponses en attente.**
   - Lis `data/a-corriger.json`.
   - S'il contient des réponses, corrige-les d'abord (juste / partiel / faux, avec ce qui manque).
   - Enregistre chacune avec `python3 outils/prof.py enregistrer`.
2. **Tirage.**
   - Session : `quiz-<cible>-<AAAAMMJJ-HHMM>`.
   - Lance `python3 outils/prof.py tirer <cible> --n 10`, avec `--n` entre 8 et 12.
   - Pour `mix`, le tirage mélange tous les chapitres préparés.
   - Les réponses ne sont pas affichées par la commande : lis-les dans `data/questions/NN.json` seulement au moment de corriger.
3. **Une question à la fois.**
   - Affiche : `[3/10 · qcm · ch.12]`, puis l'énoncé.
   - Pour un QCM, numérote les choix dans un ordre mélangé.
   - Attends la réponse de Marine. Ne pose jamais la question suivante dans le même message que la précédente.
4. **Correction immédiate**, en 2 à 4 lignes : verdict, puis pourquoi.
   - Calcul : refais le calcul en Python.
   - Ouverte, liaison ou cas : compare aux `criteres` et à la `reponse_modele`. Sois exigeant.
   - Si la question semble ambiguë ou fausse, dis-le. Elle sera retirée des révisions avec `/signaler` en phase 2. En attendant, note-la dans le bilan.
5. **Enregistrement.** Après chaque réponse : `python3 outils/prof.py enregistrer <id> <juste|partiel|faux> --reponse "<réponse résumée>" --session <id-session>`.
   - Si Marine dit « je ne sais pas », enregistre `faux`.
   - Si elle dit « stop », arrête et passe au bilan.
6. **Bilan**, en 4 lignes maximum :
   - score (juste = 1, partiel = 0,5) ;
   - notions ratées ;
   - une suggestion (`/explique <notion>` ou relecture de pages précises).
7. **Suivi.**
   - Si c'est le premier quiz de ce chapitre, lance `python3 outils/prof.py statut <N> quiz-fait`.
   - Ajoute une ligne à `PROGRESSION.md`.
   - Lance `python3 outils/prof.py valider`.
   - Fais un commit `session: chapitre N, quiz X/Y`, puis un push.
