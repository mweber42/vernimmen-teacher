#!/usr/bin/env python3
"""Outil en ligne de commande du « Prof Vernimmen ».

Bibliothèque standard uniquement (aucune dépendance, aucune API).
Lancer depuis la racine du dépôt :

    python3 outils/prof.py chapitre 12        # infos d'un chapitre + chapitres déjà vus
    python3 outils/prof.py valider            # cohérence de toutes les données
    python3 outils/prof.py tirer 12 --n 10    # questions pour un quiz (ou « mix »)
    python3 outils/prof.py enregistrer 12-q03 juste [--reponse "..."] [--session ID]
    python3 outils/prof.py attente 12-q05 "ma réponse"   # met une réponse ouverte en file
    python3 outils/prof.py etat               # recalcule niveaux + data/etat.json
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import date, datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"
QUESTIONS = DATA / "questions"

TYPES_QUESTION = {"qcm", "vrai-faux", "ouverte", "calcul", "cas", "liaison", "carte"}
CORRECTIONS = {"auto", "auto-evaluee", "claude"}
RESULTATS = {"juste": 1.0, "partiel": 0.5, "faux": 0.0}
NIVEAUX = ["decouverte", "comprise", "appliquee", "consolidee"]
STATUTS_CHAPITRE = {"a-preparer", "prepare", "lu", "quiz-fait"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEUIL_REUSSITE = 0.8  # score >= 0.8 : réponse comptée comme réussie


# ---------- lecture / écriture ----------

def lire(nom: str, defaut=None):
    chemin = DATA / nom
    if not chemin.exists():
        return defaut
    return json.loads(chemin.read_text(encoding="utf-8"))


def ecrire(nom: str, contenu) -> None:
    chemin = DATA / nom
    tmp = chemin.with_suffix(chemin.suffix + ".tmp")
    tmp.write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(chemin)


def historique() -> list[dict]:
    chemin = DATA / "historique.jsonl"
    if not chemin.exists():
        return []
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def toutes_questions() -> dict[str, dict]:
    res = {}
    for f in sorted(QUESTIONS.glob("*.json")):
        for q in json.loads(f.read_text(encoding="utf-8"))["questions"]:
            res[q["id"]] = q
    return res


def ecrire_question(q: dict) -> None:
    f = QUESTIONS / f"{q['chapitre']:02d}.json"
    contenu = json.loads(f.read_text(encoding="utf-8"))
    contenu["questions"] = [q if x["id"] == q["id"] else x for x in contenu["questions"]]
    tmp = f.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(f)


# ---------- niveaux de maîtrise ----------

def niveau_notion(reponses: list[dict]) -> tuple[str, bool]:
    """Calcule (niveau, fragile) à partir des réponses portant sur une notion.

    Règles (déterministes, recalculées à chaque fois depuis l'historique) :
    - decouverte : aucune réponse réussie.
    - comprise   : >= 1 réussite et taux de réussite >= 60 % sur les 5 dernières
                   (taux appliqué dès 3 réponses ; avant, l'indicateur fragile suffit).
    - appliquee  : comprise + >= 1 réussite sur un calcul, un cas ou une liaison.
    - consolidee : appliquee + réussites sur >= 3 jours distincts étalés sur >= 7 jours,
                   dont >= 1 question ouverte, calcul ou cas, et dernière réponse réussie.
    - fragile    : dernière réponse ratée, ou taux < 60 % sur les 5 dernières.
    """
    if not reponses:
        return "decouverte", False
    reponses = sorted(reponses, key=lambda r: r["date"])
    reussies = [r for r in reponses if r["score"] >= SEUIL_REUSSITE]
    dernieres = reponses[-5:]
    taux = sum(r["score"] for r in dernieres) / len(dernieres)
    fragile = reponses[-1]["score"] < SEUIL_REUSSITE or taux < 0.6
    niveau = "decouverte"
    if reussies and (len(dernieres) < 3 or taux >= 0.6):
        niveau = "comprise"
        if any(r["type"] in {"calcul", "cas", "liaison"} for r in reussies):
            niveau = "appliquee"
            jours = sorted({r["date"][:10] for r in reussies})
            etalement = (date.fromisoformat(jours[-1]) - date.fromisoformat(jours[0])).days
            if (len(jours) >= 3 and etalement >= 7
                    and any(r["type"] in {"ouverte", "calcul", "cas"} for r in reussies)
                    and reponses[-1]["score"] >= SEUIL_REUSSITE):
                niveau = "consolidee"
    return niveau, fragile


def recalculer_etat() -> dict:
    notions = lire("notions.json", {"notions": {}})
    hist = historique()
    par_notion: dict[str, list[dict]] = {}
    for r in hist:
        for n in r.get("notions", []):
            par_notion.setdefault(n, []).append(r)
    fragiles = []
    for nid, n in notions["notions"].items():
        niv, frag = niveau_notion(par_notion.get(nid, []))
        n["niveau"] = niv
        n["fragile"] = frag
        n["nb_reponses"] = len(par_notion.get(nid, []))
        if frag:
            fragiles.append(nid)
    ecrire("notions.json", notions)

    livre = lire("livre.json")
    etat = lire("etat.json", {})
    chapitres = livre["chapitres"]
    en_cours = [c for c in chapitres if c["statut"] in {"prepare", "lu"}]
    a_preparer = [c for c in chapitres if c["statut"] == "a-preparer"]
    attente = lire("a-corriger.json", {"en_attente": []})["en_attente"]
    revisions = lire("revisions.json", {"cartes": {}})
    aujourdhui = date.today().isoformat()
    dues = sum(1 for c in revisions.get("cartes", {}).values()
               if c.get("echeance", "9999") <= aujourdhui and not c.get("suspendue"))
    derniere = max((r["date"] for r in hist), default=etat.get("derniere_activite"))
    etat.update({
        "maj": datetime.now().isoformat(timespec="seconds"),
        "chapitre_en_cours": en_cours[0]["numero"] if en_cours else None,
        "prochain_chapitre_a_preparer": a_preparer[0]["numero"] if a_preparer else None,
        "chapitres_faits": [c["numero"] for c in chapitres if c["statut"] == "quiz-fait"],
        "cartes_dues": dues,
        "reponses_a_corriger": len(attente),
        "notions_fragiles": fragiles[:10],
        "nb_reponses_total": len(hist),
        "derniere_activite": derniere[:10] if derniere else None,
    })
    etat.setdefault("rythme", {"chapitres_par_semaine": 3})
    ecrire("etat.json", etat)
    return etat


# ---------- commandes ----------

def cmd_chapitre(args) -> int:
    livre = lire("livre.json")
    ch = next((c for c in livre["chapitres"] if c["numero"] == args.numero), None)
    if ch is None:
        print(f"Chapitre {args.numero} absent de livre.json (chapitres 1 à 55).")
        return 1
    partie = next((p for p in livre["parties"] if p["numero"] == ch["partie"]), None)
    titre = None
    if partie and ch["titre_partie"]:
        titre = next(t for t in partie["titres"] if t["numero"] == ch["titre_partie"])
    print(json.dumps({
        "chapitre": ch,
        "partie": partie and {"numero": partie["numero"], "titre": partie["titre"]},
        "titre_partie": titre and {"numero": titre["numero"], "titre": titre["titre"]},
        "chapitres_precedents_prepares": [
            {"numero": c["numero"], "titre": c["titre"]} for c in livre["chapitres"]
            if c["statut"] != "a-preparer" and c["numero"] != ch["numero"]],
        "notions_existantes": sorted(lire("notions.json", {"notions": {}})["notions"]),
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_valider(args) -> int:
    erreurs: list[str] = []
    livre = lire("livre.json")
    nums = {c["numero"] for c in livre["chapitres"]}
    for c in livre["chapitres"]:
        if c["statut"] not in STATUTS_CHAPITRE:
            erreurs.append(f"livre.json ch.{c['numero']} : statut inconnu {c['statut']!r}")

    notions = lire("notions.json", {"notions": {}})["notions"]
    for nid, n in notions.items():
        if not KEBAB.match(nid):
            erreurs.append(f"notion {nid!r} : identifiant non kebab-case / avec accents")
        if n.get("chapitre") not in nums:
            erreurs.append(f"notion {nid} : chapitre {n.get('chapitre')} inconnu")
        for d in n.get("depend_de", []):
            if d not in notions:
                erreurs.append(f"notion {nid} : dépendance inconnue {d!r}")
        if n.get("niveau") not in NIVEAUX:
            erreurs.append(f"notion {nid} : niveau inconnu {n.get('niveau')!r}")
    # cycles de dépendances
    def cycle(nid, pile):
        if nid in pile:
            return pile[pile.index(nid):] + [nid]
        for d in notions.get(nid, {}).get("depend_de", []):
            c = cycle(d, pile + [nid])
            if c:
                return c
        return None
    for nid in notions:
        c = cycle(nid, [])
        if c:
            erreurs.append("cycle de dépendances : " + " -> ".join(c))
            break

    vus = set()
    for f in sorted(QUESTIONS.glob("*.json")):
        try:
            contenu = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            erreurs.append(f"{f.name} : JSON invalide ({e})")
            continue
        for q in contenu.get("questions", []):
            qid = q.get("id", "?")
            if qid in vus:
                erreurs.append(f"question {qid} : identifiant en double")
            vus.add(qid)
            if not re.match(r"^\d{2}-q\d{2,3}$", qid):
                erreurs.append(f"question {qid} : format d'id attendu NN-qXX")
            if q.get("chapitre") not in nums or f.stem != f"{q.get('chapitre', 0):02d}":
                erreurs.append(f"question {qid} : chapitre incohérent avec {f.name}")
            if q.get("type") not in TYPES_QUESTION:
                erreurs.append(f"question {qid} : type inconnu {q.get('type')!r}")
            if q.get("correction") not in CORRECTIONS:
                erreurs.append(f"question {qid} : correction inconnue {q.get('correction')!r}")
            for n in q.get("notions", []):
                if n not in notions:
                    erreurs.append(f"question {qid} : notion inconnue {n!r}")
            if not q.get("notions"):
                erreurs.append(f"question {qid} : aucune notion")
            t = q.get("type")
            if t == "qcm" and not (isinstance(q.get("choix"), list) and q.get("reponse") in q["choix"]):
                erreurs.append(f"question {qid} : QCM sans choix ou réponse hors choix")
            if t == "vrai-faux" and not isinstance(q.get("reponse"), bool):
                erreurs.append(f"question {qid} : vrai-faux sans réponse booléenne")
            if t == "calcul" and not isinstance(q.get("reponse"), (int, float)):
                erreurs.append(f"question {qid} : calcul sans réponse numérique")
            if t in {"ouverte", "cas", "liaison", "carte"} and not q.get("reponse_modele"):
                erreurs.append(f"question {qid} : réponse modèle manquante")
            if not q.get("explication"):
                erreurs.append(f"question {qid} : explication manquante")

    for g in lire("glossaire.json", {"termes": []})["termes"]:
        if not (g.get("fr") and g.get("en") and g.get("definition")):
            erreurs.append(f"glossaire : terme incomplet {g}")
        if g.get("chapitre") not in nums:
            erreurs.append(f"glossaire {g.get('fr')} : chapitre inconnu")

    toutes = vus
    for r in historique():
        if r["question_id"] not in toutes:
            erreurs.append(f"historique : question inconnue {r['question_id']}")
    for a in lire("a-corriger.json", {"en_attente": []})["en_attente"]:
        if a["question_id"] not in toutes:
            erreurs.append(f"a-corriger : question inconnue {a['question_id']}")

    for f in sorted((RACINE / "fiches").glob("*.md")):
        texte = f.read_text(encoding="utf-8")
        if "Ce qui a changé depuis 2016" not in texte:
            erreurs.append(f"fiches/{f.name} : rubrique « Ce qui a changé depuis 2016 » absente")

    if erreurs:
        print(f"{len(erreurs)} erreur(s) :")
        for e in erreurs:
            print(" -", e)
        return 1
    print(f"OK : {len(notions)} notions, {len(vus)} questions, données cohérentes.")
    return 0


def cmd_tirer(args) -> int:
    qs = [q for q in toutes_questions().values() if not q.get("signalee")]
    if args.cible != "mix":
        qs = [q for q in qs if q["chapitre"] == int(args.cible)]
    if not qs:
        print("Aucune question disponible pour cette cible.")
        return 1
    hist = historique()
    notions = lire("notions.json", {"notions": {}})["notions"]
    vues: dict[str, list[float]] = {}
    for r in hist:
        vues.setdefault(r["question_id"], []).append(r["score"])
    rang = {n: i for i, n in enumerate(NIVEAUX)}
    rnd = random.Random(args.graine)

    def priorite(q):
        scores = vues.get(q["id"], [])
        niv = min((rang.get(notions.get(n, {}).get("niveau", "decouverte"), 0) for n in q["notions"]), default=0)
        fragile = any(notions.get(n, {}).get("fragile") for n in q["notions"])
        derniere_ratee = bool(scores) and scores[-1] < SEUIL_REUSSITE
        # petite valeur = plus prioritaire
        return (not (derniere_ratee or fragile), len(scores), niv, rnd.random())

    qs.sort(key=priorite)
    choix = qs[: args.n]
    rnd.shuffle(choix)
    for q in choix:
        print(json.dumps({k: q[k] for k in q if k not in {"explication", "reponse", "reponse_modele"}},
                         ensure_ascii=False))
    print(f"# {len(choix)} question(s) tirée(s) sur {len(qs)} disponibles", file=sys.stderr)
    return 0


def cmd_enregistrer(args) -> int:
    qs = toutes_questions()
    q = qs.get(args.question)
    if q is None:
        print(f"Question inconnue : {args.question}")
        return 1
    ligne = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "question_id": q["id"],
        "chapitre": q["chapitre"],
        "type": q["type"],
        "notions": q["notions"],
        "resultat": args.resultat,
        "score": RESULTATS[args.resultat],
        "session": args.session,
    }
    if args.reponse:
        ligne["reponse"] = args.reponse
    if args.confiance is not None:
        ligne["confiance"] = args.confiance
    with (DATA / "historique.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    # retirer de la file d'attente si elle y était
    attente = lire("a-corriger.json", {"en_attente": []})
    avant = len(attente["en_attente"])
    attente["en_attente"] = [a for a in attente["en_attente"] if a["question_id"] != q["id"]]
    if len(attente["en_attente"]) != avant:
        ecrire("a-corriger.json", attente)
    recalculer_etat()
    print(f"Enregistré : {q['id']} → {args.resultat}")
    return 0


def cmd_attente(args) -> int:
    q = toutes_questions().get(args.question)
    if q is None:
        print(f"Question inconnue : {args.question}")
        return 1
    attente = lire("a-corriger.json", {"en_attente": []})
    attente["en_attente"].append({
        "date": datetime.now().isoformat(timespec="seconds"),
        "question_id": q["id"],
        "reponse": args.reponse,
        "origine": args.origine,
    })
    ecrire("a-corriger.json", attente)
    recalculer_etat()
    print(f"En attente de correction : {q['id']}")
    return 0


def cmd_statut(args) -> int:
    livre = lire("livre.json")
    if args.statut not in STATUTS_CHAPITRE:
        print(f"Statut inconnu. Possibles : {sorted(STATUTS_CHAPITRE)}")
        return 1
    for c in livre["chapitres"]:
        if c["numero"] == args.numero:
            c["statut"] = args.statut
            if args.table_detaillee:
                c["table_detaillee_fournie"] = True
    ecrire("livre.json", livre)
    recalculer_etat()
    print(f"Chapitre {args.numero} → {args.statut}")
    return 0


def cmd_etat(args) -> int:
    print(json.dumps(recalculer_etat(), ensure_ascii=False, indent=2))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("chapitre"); a.add_argument("numero", type=int); a.set_defaults(f=cmd_chapitre)
    a = sp.add_parser("valider"); a.set_defaults(f=cmd_valider)
    a = sp.add_parser("tirer"); a.add_argument("cible"); a.add_argument("--n", type=int, default=10)
    a.add_argument("--graine", type=int, default=None); a.set_defaults(f=cmd_tirer)
    a = sp.add_parser("enregistrer"); a.add_argument("question"); a.add_argument("resultat", choices=RESULTATS)
    a.add_argument("--reponse"); a.add_argument("--session"); a.add_argument("--confiance", type=int, choices=[1, 2, 3])
    a.set_defaults(f=cmd_enregistrer)
    a = sp.add_parser("attente"); a.add_argument("question"); a.add_argument("reponse")
    a.add_argument("--origine", default="terminal"); a.set_defaults(f=cmd_attente)
    a = sp.add_parser("statut"); a.add_argument("numero", type=int); a.add_argument("statut")
    a.add_argument("--table-detaillee", action="store_true"); a.set_defaults(f=cmd_statut)
    a = sp.add_parser("etat"); a.set_defaults(f=cmd_etat)
    args = p.parse_args(argv)
    return args.f(args)


if __name__ == "__main__":
    sys.exit(main())
