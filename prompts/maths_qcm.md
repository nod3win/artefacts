# Matière : Mathématiques — QCM type concours

## Fiche
**Fiche : [XX]** (remplacer par le numéro, de **01 à 08**).

## Rôle
Agis comme un concepteur de sujets du concours de médecine. Tu produis **10 QCM niveau concours difficile** pour la fiche, au format JSON avec LaTeX validé, destinés à une application web de révision. Le concours réel : QCM à **4 propositions, une seule correcte**.

---

# Règle de périmètre (OBLIGATOIRE)
Tu travailles exclusivement sur `RAW_DATA/Mathématiques/Fiche-[XX]_.../`.
Tu ne dois **jamais** créer, modifier, déplacer ou supprimer de fichiers en dehors de ce dossier. Interdiction absolue de toucher au dossier `CARNET_D_ENTRAINEMENT/` existant.
Seules exceptions, en **lecture seule** : `RAW_DATA/Mathématiques/Mathématiques.pdf` (annales) et `RAW_DATA/Mathématiques/_qcm/` (outillage : `_preambule.tex`, `valider_qcm.py`).
Tout autre chemin consulté = erreur, arrête-toi immédiatement.

---

# Sources autorisées
1. Le cours de la fiche : `Fiche-[XX]_....tex` (source principale).
2. L'extrait de livre : `LIVRE_Fiche-[XX]_....pdf`.
3. Les annales : `RAW_DATA/Mathématiques/Mathématiques.pdf` — **uniquement les questions liées à cette fiche**, pour calibrer le style et la difficulté réelle du concours. Ne recopie aucune annale : inspire-toi du style, crée des questions originales.

**Lecture des PDF : OCR natif exclusivement.** Charge chaque page comme une image et lis-la visuellement (graphes, courbes, tableaux compris). Jamais Tesseract, pytesseract ou extraction externe.

---

# Les 10 questions
* **Exactement 10 questions**, toutes calibrées **niveau concours difficile** (pas de gradation).
* Couvre les mécaniques importantes de la fiche ; le champ `theme` indique la mécanique visée par chaque question.
* Une question = **une seule réponse correcte** parmi 4 propositions.
* Questions calculatoires ET conceptuelles ; graphes de fonctions ou figures TikZ/pgfplots auto-contenues autorisés dans l'énoncé ; aucune image externe.
* Notations : `\qty{...}{...}` et `\ang{...}` pour les grandeurs, `\R`, `\N`, `\Z`, `\Q`, `\C` pour les ensembles, `\vv{...}` pour les vecteurs.

---

# ⭐ Qualité des distracteurs (le cœur du travail)

**Méthode imposée — génération à rebours :** pour chaque question, tu identifies D'ABORD 3 erreurs typiques d'étudiant, PUIS tu calcules le résultat exact de chaque erreur : ce résultat devient le distracteur. **Aucune option inventée au hasard.**

Taxonomie d'erreurs mathématiques (pioche dedans, adapte à la fiche) :
* erreur de signe en dérivant ou en intégrant (chaîne, $e^{-x}$, $\cos\to-\sin$) ;
* règle du produit ou du quotient incomplète (un terme oublié) ;
* règle de la chaîne oubliée ou appliquée deux fois ;
* oubli de la constante d'intégration ou des bornes inversées ;
* domaine de définition ignoré (racine, log, dénominateur nul) ;
* inversion d'une inégalité en multipliant par un négatif ;
* confusion radian ↔ degré ; valeurs remarquables trigonométriques permutées ($\sin\leftrightarrow\cos$, $\pi/3\leftrightarrow\pi/6$) ;
* erreur sur les identités ($(a+b)^2$ sans double produit, $\ln(a+b)\ne\ln a+\ln b$) ;
* limite : forme indéterminée tranchée trop vite, croissances comparées inversées ;
* vecteurs : produit scalaire ↔ norme, colinéarité ↔ orthogonalité ;
* statistiques : variance ↔ écart-type, effectifs ↔ fréquences, médiane ↔ moyenne.

Règles dures :
* Les 4 options sont **homogènes** : même format, même forme d'écriture (fraction/décimal), longueurs comparables.
* **Interdit** : « toutes/aucune des réponses », options synonymes ou équivalentes après simplification, valeur absurde d'un ordre de grandeur farfelu.
* La position de la bonne réponse **varie** sur les 10 questions (~équirépartie entre A/B/C/D).
* **Passe d'auto-critique finale** : pour chaque question, demande-toi « un bon étudiant peut-il éliminer 2 options sans calculer ? ». Si oui, remplace l'option faible par un vrai piège. Vérifie aussi qu'aucune paire d'options n'est mathématiquement égale.

---

# Format JSON (schéma figé)
Le livrable est `questions.json` : un **tableau de 10 objets**, chacun exactement :

```json
{
  "id": "MATH-F[XX]-Q01",
  "matiere": "Mathématiques",
  "fiche": "[XX]",
  "theme": "nom de la mécanique visée",
  "difficulte": "concours",
  "enonce": "énoncé en LaTeX (backslashes échappés : \\frac{...}{...}, \\qty{...}{...})",
  "options": ["option A", "option B", "option C", "option D"],
  "reponse_index": 2,
  "explication": "justification complète de la bonne réponse, en LaTeX",
  "pieges": [
    "A: erreur dont découle l'option A",
    "B: erreur dont découle l'option B",
    "D: erreur dont découle l'option D"
  ]
}
```

* `reponse_index` : **0-based** (A=0, B=1, C=2, D=3).
* `pieges` : exactement 3 entrées — les 3 distracteurs, chacun avec la lettre et l'erreur d'étudiant dont il découle.
* Dans le JSON, chaque backslash LaTeX est **doublé** (`\\frac`, `\\lim`) et les guillemets échappés.

---

# Workflow de validation (OBLIGATOIRE, dans cet ordre)

Crée le dossier `QCM_CONCOURS/` dans le dossier de la fiche. Puis :

1. **Rédige `controle.tex`** : les 10 questions complètes (énoncé, options A-D, bonne réponse, explication, pièges), en utilisant VERBATIM le préambule `RAW_DATA/Mathématiques/_qcm/_preambule.tex`. C'est ici que vit le LaTeX de référence (simple backslash).
2. **Compile `controle.tex`** en PDF. Tant que ça ne compile pas, corrige. Ne passe à l'étape suivante qu'avec un `controle.pdf` propre.
3. **Sérialise en `questions.json`** depuis le `.tex` validé (transformation mécanique : doubler les backslashes, échapper les guillemets, `\n` pour les sauts de ligne).
4. **Exécute le validateur** :
   `python3 RAW_DATA/Mathématiques/_qcm/valider_qcm.py QCM_CONCOURS/questions.json RAW_DATA/Mathématiques/_qcm/_preambule.tex`
   Ce script vérifie la structure (10 questions, 4 options, index 0-3, 3 pièges) **et recompile tout le LaTeX extrait du JSON**. Corrige et relance jusqu'à obtenir `✅ VALIDATION OK`. Un `⚠️` sur la répartition des réponses doit aussi être corrigé.
5. **Nettoie** : supprime tous les auxiliaires (`.aux`, `.log`, `.out`, etc.). Le dossier final contient **exactement trois fichiers** : `controle.tex`, `controle.pdf`, `questions.json`.

---

# Livrable attendu
`RAW_DATA/Mathématiques/Fiche-[XX]_.../QCM_CONCOURS/` contenant `questions.json` (10 questions validées ✅), `controle.tex` et `controle.pdf` (relecture humaine), rien d'autre, sans aucune modification hors du dossier de la fiche.
