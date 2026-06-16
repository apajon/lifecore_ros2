#!/bin/bash
# MEMPALACE COPILOT WAKE HOOK — Session-start memory recall
#
# GitHub Copilot "SessionStart" hook. Equivalent du hook Cursor
# sessionStart, adapté au contrat de hooks de Copilot.
#
# Comportement :
#   1. Parse le payload SessionStart de Copilot (workspace, session_id).
#   2. Infère le wing à partir du nom du workspace.
#   3. Retourne {"continue": true, "systemMessage": "..."} avec
#      l'instruction de rappel MemPalace.
#
# === INSTALL ===
#
# Placer le fichier JSON compagnon (mempalace-wake-copilot.json) dans
# .github/hooks/ — Copilot le découvre automatiquement.
#
# === DIFFÉRENCES VS CURSOR ===
#
#   * Copilot utilise SessionStart (PascalCase), Cursor sessionStart.
#   * Sortie : {"continue": true, "systemMessage": "..."} au lieu de
#     {"additionalContext": "..."}.
#   * agent_name pour diary_read : "copilot" au lieu de "cursor-ide".
#   * Mêmes helpers lib/common.sh pour le kill-switch et le logging.

_mempal_self="${BASH_SOURCE[0]:-$0}"
_mempal_dir="$(cd "$(dirname "$_mempal_self")" 2>/dev/null && pwd)"
# shellcheck source=lib/common.sh
. "$_mempal_dir/lib/common.sh"

if mempal_is_disabled; then
    printf '{"continue": true}\n'
    exit 0
fi

INPUT="$(cat)"

# ── Parse Copilot SessionStart payload ─────────────────────────────
#
# Copilot envoie un JSON sur stdin. On extrait ce qu'on peut avec un
# parser Python minimal, similaire à mempal_parse_stdin mais adapté
# au schéma Copilot (qui peut différer de Cursor).
#
# On utilise le parser existant de common.sh en fallback : s'il
# arrive à extraire un workspace, on l'utilise. Sinon, on tente une
# extraction directe du champ "workspace" ou "cwd" du payload.

mempal_parse_stdin "$INPUT"

WING=""
if [ "$MEMPAL_PARSE_OK" = "1" ] && [ -n "$MEMPAL_WORKSPACE" ]; then
    WING="$(mempal_infer_wing "$MEMPAL_WORKSPACE")"
else
    # Fallback : extraction directe du workspace depuis le JSON Copilot
    WING="$(
        printf '%s' "$INPUT" | "$MEMPAL_PYTHON_BIN" -c '
import json, sys, os, re

def safe_str(value):
    return re.sub(r"[^a-zA-Z0-9_/.\-~]", "", str(value or ""))

try:
    data = json.load(sys.stdin)
except Exception:
    print("")
    sys.exit(0)

if not isinstance(data, dict):
    print("")
    sys.exit(0)

# Copilot peut fournir workspace, workspace_roots, ou cwd
ws = ""
roots = data.get("workspace_roots") or data.get("workspace") or []
if isinstance(roots, list) and roots:
    ws = safe_str(roots[0])
elif isinstance(roots, str) and roots:
    ws = safe_str(roots)
if not ws:
    ws = safe_str(data.get("cwd", ""))

if ws:
    print(os.path.basename(ws.rstrip("/")) or ws)
' 2>/dev/null
    )"
fi

# Fallback ultime : utiliser le nom du dossier courant
if [ -z "$WING" ]; then
    WING="$(basename "$PWD")"
fi

mempal_log "SessionStart" "${MEMPAL_CONV_ID:-unknown}" \
    "workspace=${MEMPAL_WORKSPACE:-$PWD} wing=$WING"

# ── Émission du systemMessage ──────────────────────────────────────
#
# Copilot attend {"continue": true, "systemMessage": "..."}.
# On injecte l'instruction de rappel MemPalace, avec le wing inféré.
# Les noms d'outils MCP sont vérifiés contre le serveur MemPalace :
# mempalace_search et mempalace_diary_read existent et acceptent
# le paramètre wing.

"$MEMPAL_PYTHON_BIN" -c '
import json, sys
wing = sys.argv[1] if len(sys.argv) > 1 else "unknown"
msg = (
    "MemPalace wake-up. Ce workspace correspond à wing=" + wing + ". "
    "Avant de répondre à toute question touchant au code, aux décisions "
    "d'\''architecture, aux conventions ou à l'\''historique de ce projet, "
    "appelle mempalace_search (wing=" + wing + ", "
    "query=<mots-clés pertinents>) et mempalace_diary_read "
    "(agent_name=copilot, wing=" + wing + ", last_n=10). "
    "Utilise les résultats tels quels s'\''ils répondent à la question ; "
    "ne résume jamais les mots de l'\''utilisateur stockés dans MemPalace."
)
print(json.dumps({"continue": True, "systemMessage": msg}))
' "$WING"
