---
description: Réexpliquer une notion sous un autre angle (ajout au cours si validé)
argument-hint: <id-notion ou terme>
---

Réexplique **$ARGUMENTS**, en suivant `CLAUDE.md`.

1. **Repère la notion** dans le contenu (`content/`). Accepte un identifiant ou un terme approchant. Relis le cours et la fiche du chapitre pour ne pas répéter le même découpage ni le même exemple. Si la notion n'existe pas encore, dis-le, puis explique-la brièvement en indiquant le chapitre du livre où elle sera traitée (d'après `content/livre.json`, sans inventer de page).
2. **Autre angle.** Choisis un autre découpage logique, par exemple :
   - partir du résultat et remonter ;
   - comparer avec la notion voisine ;
   - passer par le cas limite.

   L'ordre reste : question résolue → mécanique → détail.
3. **Autre exemple chiffré.** Calcule-le en Python. Il ne doit pas figurer déjà dans le cours. Si tu utilises une valeur actuelle, donne sa source et sa date.
4. **Liens.** Rappelle en une ligne chaque dépendance qui aide vraiment à comprendre.
5. **Vérification.** Termine par une seule question courte.
6. **Fin.** Demande si l'explication doit être ajoutée au cours. Si Marine dit oui, ajoute-la, lance la validation, fais un commit `explique: <notion>`, puis un push. Sinon, ne modifie aucun fichier.

Sortie : 25 lignes maximum.
