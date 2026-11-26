# vernimmen-teacher

Compagnon d'apprentissage pour « Finance d'entreprise » de Pierre Vernimmen (Dalloz, édition 2016). Il produit des fiches par chapitre, des quiz et un suivi de progression. Il fonctionne avec Claude Code : le professeur, c'est Claude, avec les règles de `CLAUDE.md`.

## Utilisation (phase 1)

| Commande | Quand | Effet |
|---|---|---|
| `/prepare 12` (+ photo de la table détaillée, si disponible) | avant la lecture | crée `fiches/12.md`, les questions, les notions et le glossaire ; affiche 5 lignes à surveiller |
| `/quiz 12` ou `/quiz mix` | après la lecture | 8 à 12 questions, corrigées une par une ; met à jour la progression |
| `/explique bfr` | en cas de blocage | réexplique la notion sous un autre angle, avec un autre exemple |

Outil en ligne de commande (Python 3, bibliothèque standard uniquement) :

```bash
python3 outils/prof.py chapitre 12
```

```bash
python3 outils/prof.py valider
```

```bash
python3 outils/prof.py etat
```

Les autres sous-commandes (`tirer`, `enregistrer`, `attente`, `statut`) sont appelées par les commandes Claude. Voir `python3 outils/prof.py -h`.

## Structure des données

Tous les identifiants de notion sont en kebab-case, sans accents.

| Fichier | Contenu |
|---|---|
| `data/livre.json` | Plan du livre de 2016 : `parties[]` (avec `titres[]`), `chapitres[]` (`numero`, `titre`, `partie`, `titre_partie`, `page_debut`, `page_fin`, `nb_pages`, `statut`, `table_detaillee_fournie`), `liminaires`, `fin_ouvrage`, `alertes`. Les pages de fin sont **déduites**. |
| `data/notions.json` | `{"notions": {"<id>": {nom, nom_en, chapitre, definition, depend_de[], niveau, fragile, nb_reponses}}}`. Le niveau est recalculé depuis l'historique. |
| `data/glossaire.json` | `{"termes": [{fr, en, definition, chapitre, notion}]}`. L'export CSV `terme FR, terme EN, définition courte, chapitre` arrive en phase 2. |
| `data/questions/NN.json` | `{"chapitre", "questions": [...]}`. Voir `modeles/questions.json`. Champs : `id` (`NN-qXX`), `notions[]`, `type` (`qcm`, `vrai-faux`, `ouverte`, `calcul`, `cas`, `liaison`, `carte`), `correction` (`auto`, `auto-evaluee`, `claude`), `enonce`, `choix`, `reponse`, `tolerance`, `unite`, `reponse_modele`, `criteres`, `explication`, `difficulte`, `signalee`. |
| `data/historique.jsonl` | Une ligne par réponse : `date`, `question_id`, `chapitre`, `type`, `notions`, `resultat` (`juste`, `partiel`, `faux`), `score` (1 / 0,5 / 0), `session`, `reponse`, `confiance` (optionnelle). |
| `data/a-corriger.json` | `{"en_attente": [{date, question_id, reponse, origine}]}` : les réponses ouvertes à faire corriger par Claude. |
| `data/revisions.json` | État de la répétition espacée par question (phase 2). |
| `data/etat.json` | Synthèse compacte recalculée par `prof.py etat` : chapitre en cours, prochain chapitre, cartes dues, notions fragiles, dernière activité, rythme. |
| `fiches/NN.md` | Fiche du chapitre (modèle : `modeles/fiche.md`). |
| `calculs/NN.py` | Script qui produit tous les chiffres de la fiche et des questions. |
| `PROGRESSION.md` | Journal lisible : une ligne par session. |

Niveaux de maîtrise : `decouverte` → `comprise` → `appliquee` → `consolidee`. Les règles exactes sont dans `CLAUDE.md`.

## Feuille de route

- [x] **Phase 1** : plan du livre, `/prepare`, `/quiz`, `/explique`, fiches, structure des données.
- [ ] **Phase 2** : répétition espacée, `/revision`, `/exercice`, `/signaler`, `/bilan`, `/coach-du-jour` (et le prompt de la tâche planifiée ici), export CSV du glossaire, tests.
- [ ] **Phase 3** (sur demande) : application mobile, sans API d'IA.
