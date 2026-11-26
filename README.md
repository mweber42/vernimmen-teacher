# Vernimmen Teacher

Application web pour apprendre le Vernimmen « Finance d'entreprise » : cours et fiches par chapitre, révisions espacées et suivi de progression.

L'application accompagne la lecture de l'édition 2016 (Dalloz, papier). Elle doit permettre :
- **Lire** le cours et la fiche de révision de chaque chapitre, enseignés selon les règles **actuelles**, avec ce qui a changé depuis 2016.
- **Réviser** avec des questions variées (QCM, vrai/faux, calcul, question ouverte, mini-cas, liaison entre notions), planifiées par répétition espacée.
- **Suivre** sa progression : chapitres, notions maîtrisées, points faibles, régularité.

Elle s'utilise sur téléphone et sur ordinateur. Elle est installable sur l'écran d'accueil et ne dépend d'aucune API d'IA. Le contenu pédagogique est généré par Claude Code dans ce dépôt, puis intégré à l'application à chaque déploiement.

## État du projet

**Phase 0 : cadrage produit et interface, en cours.** L'application n'a pas encore de code.

| Phase | Objectif | État |
|---|---|---|
| 0. Cadrage | Parcours utilisateur, écrans, maquettes HTML, architecture et modèle de données | en cours |
| 1. POC | Boucle lire → réviser → voir sa progression, sur téléphone, avec les chapitres 1 et 2 | à venir |
| 2. V1 | Toutes les fonctionnalités, synchronisation entre appareils, signalements, coach quotidien | à venir |
| 3. Contenu | Chapitres au rythme de lecture, examens de fin de partie | à venir |

## Contenu du dépôt

| Chemin | Rôle |
|---|---|
| `content/livre.json` | Plan du livre de 2016 : 5 parties, titres, 55 chapitres, pages. Les pages de fin sont déduites ; les incohérences sont listées dans `alertes`. |
| `modeles/` | Propositions de format pour la fiche et les questions, à valider en phase 0. |
| `.claude/commands/` | Commandes Claude Code pour produire le contenu : `/prepare <chapitre>` et `/explique <notion>`. Ensuite (V1) : `/signalements` et `/coach-du-jour`. |
| `CLAUDE.md` | Règles du professeur et conventions du projet. |

## Architecture pressentie (à valider en phase 0)

- **Application :** PWA React + TypeScript (Vite), mobile-first, mode sombre.
- **Contenu :** fichiers versionnés dans `content/`, validés par un schéma (Zod) au build. Un contenu invalide bloque le déploiement au lieu de casser l'application.
- **Progression :** stockée sur l'appareil (IndexedDB) avec export et import dans le POC, puis synchronisée entre appareils (par exemple Supabase) en V1.
- **Révisions :** algorithme FSRS, via une bibliothèque open source éprouvée.
- **Hébergement :** déploiement automatique depuis GitHub (Vercel ou Netlify) à chaque push.
