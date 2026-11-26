---
description: Réexpliquer une notion sous un autre angle
argument-hint: <id-notion ou terme>
---

Réexplique **$ARGUMENTS**, en suivant `CLAUDE.md`.

1. Retrouve la notion dans `data/notions.json`. Accepte un identifiant ou un terme approchant. Relis sa fiche `fiches/NN.md` pour **ne pas répéter** le même découpage ni le même exemple. Si la notion n'existe pas encore, dis-le, puis explique-la quand même brièvement, en précisant le chapitre du livre où elle sera traitée (d'après `data/livre.json`, sans inventer de page).
2. **Autre angle.** Prends un autre découpage logique que la fiche : par exemple partir du résultat attendu et remonter, comparer avec la notion voisine, ou passer par le cas limite. Ordre à suivre : question résolue → mécanique → détail.
3. **Autre exemple chiffré.** Calcule-le en Python. Il ne doit pas être dans la fiche. Si tu utilises une valeur actuelle, donne sa source et sa date.
4. **Liens.** Rappelle en une ligne chaque dépendance (`depend_de`) qui aide vraiment à comprendre.
5. **Vérification.** Termine par une seule question courte de vérification. Si Marine y répond, corrige sa réponse. N'enregistre rien dans l'historique, car ce n'est pas une question de la banque.

Pas de fichier modifié, sauf si Marine demande d'ajouter cette explication à la fiche. Sortie : 25 lignes au maximum.
