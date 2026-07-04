#!/usr/bin/env python3
# ============================================================
# valider_qcm.py — validation d'un questions.json (QCM concours)
#
# Vérifie :
#   1. que le JSON parse (échappement correct des \ et ")
#   2. la structure : 10 questions, champs obligatoires, 4 options,
#      reponse_index dans [0..3], 3 entrées dans "pieges"
#   3. la répartition des bonnes réponses (avertissement si biaisée)
#   4. que TOUT le LaTeX contenu dans le JSON recompile réellement
#      (round-trip : JSON -> .tex -> pdflatex)
#
# Usage :
#   python3 valider_qcm.py questions.json _preambule.tex
#
# Sortie : "✅ VALIDATION OK" et code 0, sinon message ❌ et code 1.
# ============================================================
import json, sys, subprocess, tempfile, os, pathlib, collections

def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)

if len(sys.argv) != 3:
    fail("Usage: python3 valider_qcm.py questions.json _preambule.tex")

json_path, pre_path = sys.argv[1], sys.argv[2]

# ---------- 1. Parsing JSON ----------
try:
    raw = pathlib.Path(json_path).read_text(encoding="utf-8")
    data = json.loads(raw)
except FileNotFoundError:
    fail(f"Fichier introuvable : {json_path}")
except json.JSONDecodeError as e:
    fail(f"JSON invalide (échappement des \\ ou \" ?) : {e}")

try:
    preambule = pathlib.Path(pre_path).read_text(encoding="utf-8")
except FileNotFoundError:
    fail(f"Préambule introuvable : {pre_path}")

# ---------- 2. Structure ----------
if not isinstance(data, list):
    fail("La racine du JSON doit être un tableau de questions.")
if len(data) != 10:
    fail(f"Attendu exactement 10 questions, trouvé {len(data)}.")

CHAMPS = {"id", "matiere", "fiche", "theme", "difficulte",
          "enonce", "options", "reponse_index", "explication", "pieges"}

for i, q in enumerate(data, 1):
    if not isinstance(q, dict):
        fail(f"Q{i} : n'est pas un objet JSON.")
    manquants = CHAMPS - q.keys()
    if manquants:
        fail(f"Q{i} ({q.get('id','?')}) : champs manquants {sorted(manquants)}")
    if not isinstance(q["options"], list) or len(q["options"]) != 4:
        fail(f"Q{i} ({q['id']}) : il faut exactement 4 options.")
    if any(not isinstance(o, str) or not o.strip() for o in q["options"]):
        fail(f"Q{i} ({q['id']}) : option vide ou non textuelle.")
    if not isinstance(q["reponse_index"], int) or not (0 <= q["reponse_index"] <= 3):
        fail(f"Q{i} ({q['id']}) : reponse_index doit être un entier 0..3.")
    if not isinstance(q["pieges"], list) or len(q["pieges"]) != 3:
        fail(f"Q{i} ({q['id']}) : 'pieges' doit lister exactement les 3 distracteurs.")
    if not q["enonce"].strip() or not q["explication"].strip():
        fail(f"Q{i} ({q['id']}) : énoncé ou explication vide.")

# ---------- 3. Répartition des bonnes réponses ----------
repartition = collections.Counter(q["reponse_index"] for q in data)
lettres = {0: "A", 1: "B", 2: "C", 3: "D"}
if max(repartition.values()) >= 6:
    lettre = lettres[repartition.most_common(1)[0][0]]
    print(f"⚠️  Avertissement : {repartition.most_common(1)[0][1]}/10 bonnes réponses "
          f"en position {lettre}. Rééquilibre la position de la bonne réponse.")

# ---------- 4. Round-trip LaTeX ----------
blocs = []
for q in data:
    opts = "\n".join(rf"\item {o}" for o in q["options"])
    pieges = "\n".join(rf"\item {p}" for p in q["pieges"])
    blocs.append(rf"""\noindent\textbf{{{q['id']} --- {q['theme']}}}\par
{q['enonce']}
\begin{{enumerate}}[label=\Alph*)]
{opts}
\end{{enumerate}}
\textit{{Bonne réponse : {lettres[q['reponse_index']]}}}\par
{q['explication']}\par
\textit{{Pièges :}}
\begin{{itemize}}
{pieges}
\end{{itemize}}
\vspace{{8pt}}\hrule\vspace{{8pt}}""")

corps = preambule
corps = corps.replace(r"% ... contenu ...", "\n".join(blocs))

with tempfile.TemporaryDirectory() as d:
    tex = os.path.join(d, "chk.tex")
    pathlib.Path(tex).write_text(corps, encoding="utf-8")
    r = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
         "-output-directory", d, tex],
        capture_output=True, text=True)
    if r.returncode != 0:
        erreurs = [l for l in r.stdout.splitlines() if l.startswith("!")]
        fail("Le LaTeX contenu dans le JSON ne compile pas :\n  "
             + "\n  ".join(erreurs[:6]))

print("✅ VALIDATION OK : 10 questions, 4 options, index et pièges corrects, "
      "LaTeX du JSON recompilé sans erreur.")
