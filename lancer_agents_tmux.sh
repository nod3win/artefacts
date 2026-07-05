#!/usr/bin/env bash
# ============================================================
# lancer_agents_tmux.sh — ouvre des sessions Claude Code
# INTERACTIVES (usage abonnement, pas le crédit Agent SDK),
# une fenêtre tmux par fiche. Zéro terminal à ouvrir à la main.
#
# Usage (depuis la racine qui contient RAW_DATA/) :
#   ./lancer_agents_tmux.sh <MATIERE> <PROMPT_TEMPLATE> [FICHES...]
#
# Exemples :
#   ./lancer_agents_tmux.sh Chimie prompts/chimie_qcm.md          # toutes les fiches
#   ./lancer_agents_tmux.sh Physique prompts/physique_qcm.md 03 07
#
# Navigation ensuite :
#   tmux attach -t agents        # voir les fenêtres
#   Ctrl+B n / p                 # fenêtre suivante / précédente
#   Ctrl+B w                     # liste des fenêtres (une par fiche)
#   Ctrl+B d                     # détacher (tout continue de tourner)
# ============================================================
set -u

MATIERE="${1:?Usage: ./lancer_agents_tmux.sh <MATIERE> <PROMPT_TEMPLATE> [FICHES...]}"
TEMPLATE="${2:?Il manque le fichier de prompt template.}"
shift 2

SESSION="${SESSION:-agents}"
ROOT="$(pwd)"

command -v tmux  >/dev/null || { echo "❌ tmux n'est pas installé (apt install tmux)."; exit 1; }
command -v claude >/dev/null || { echo "❌ claude introuvable dans le PATH."; exit 1; }
[ -f "$TEMPLATE" ] || { echo "❌ Template introuvable : $TEMPLATE"; exit 1; }
[ -d "RAW_DATA/$MATIERE" ] || { echo "❌ RAW_DATA/$MATIERE introuvable (lance depuis la racine)."; exit 1; }

# --- Liste des fiches : arguments, sinon auto-détection ---
if [ "$#" -gt 0 ]; then
  FICHES=("$@")
else
  FICHES=()
  for d in "RAW_DATA/$MATIERE"/Fiche-*_*/; do
    b=$(basename "$d"); n=${b#Fiche-}; FICHES+=("${n%%_*}")
  done
fi

# --- Session tmux (créée si absente, réutilisée sinon) ---
tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION" -c "$ROOT"

echo "▶ $MATIERE — ${#FICHES[@]} fiche(s) : ${FICHES[*]} — session tmux : $SESSION"

for XX in "${FICHES[@]}"; do
  WIN="${MATIERE:0:4}-${XX}"                       # ex. Chim-03, Phys-07
  PROMPT_FILE=$(mktemp "/tmp/prompt-${MATIERE}-${XX}-XXXX.md")
  sed "s/\[XX\]/${XX}/g" "$TEMPLATE" > "$PROMPT_FILE"

  # Fenêtre interactive : claude démarre avec le prompt initial.
  # Session INTERACTIVE => consomme l'abonnement, pas le crédit Agent SDK.
  tmux new-window -t "$SESSION" -n "$WIN" -c "$ROOT" \
    "claude \"\$(cat '$PROMPT_FILE')\" --dangerously-skip-permissions ; echo ; echo '=== Fiche ${XX} : session terminée (fenêtre conservée) ===' ; exec bash"

  echo "  ↳ fenêtre $WIN ouverte (prompt: $PROMPT_FILE)"
  sleep 4   # étale les démarrages
done

echo
echo "🏁 ${#FICHES[@]} sessions interactives lancées dans tmux."
echo "   tmux attach -t $SESSION    # pour voir / intervenir"
echo "   Ctrl+B w                   # naviguer entre les fiches"
echo "   Ctrl+B d                   # détacher, tout continue"
