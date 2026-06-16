#!/bin/bash
# RSM WAKE HOOK — Repo Semantic Memory context injection
#
# GitHub Copilot "SessionStart" + "UserPromptSubmit" hook.
# Injecte une instruction de rappel RSM après MemPalace dans la
# chaîne de hooks.
#
# Comportement :
#   1. Parse le payload Copilot (workspace, event).
#   2. Infère le workspace root.
#   3. Retourne {"continue": true, "systemMessage": "..."} avec
#      l'instruction d'utilisation de RSM.
#
# Événements supportés :
#   * SessionStart — rappel général d'utiliser RSM
#   * UserPromptSubmit — rappel ciblé avec la requête utilisateur
#
# === INSTALL ===
#
# Déclaré dans mempalace-wake-copilot.json (après les hooks MemPalace
# pour garantir l'ordre : MemPal d'abord, RSM ensuite).
#
# === ORCHESTRATION ===
#
# Les hooks Copilot pour un même événement s'exécutent dans l'ordre
# du tableau JSON. L'ordre est :
#   1. mempal_wake_hook_copilot.sh  (MemPalace — rappel mémoire)
#   2. rsm_wake_hook_copilot.sh     (RSM — contexte sémantique)

_rsm_self="${BASH_SOURCE[0]:-$0}"
_rsm_dir="$(cd "$(dirname "$_rsm_self")" 2>/dev/null && pwd)"
# shellcheck source=lib/common.sh
. "$_rsm_dir/lib/common.sh"

# Le kill-switch MemPalace contrôle aussi RSM (même mécanisme)
if mempal_is_disabled; then
    printf '{"continue": true}\n'
    exit 0
fi

INPUT="$(cat)"

# ── Détection de l'événement ───────────────────────────────────────
#
# On extrait hookEventName pour adapter le message : SessionStart →
# rappel général, UserPromptSubmit → rappel ciblé.

EVENT="$(
    printf '%s' "$INPUT" | "$MEMPAL_PYTHON_BIN" -c '
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get("hookEventName", ""))
except Exception:
    print("")
' 2>/dev/null
)"

# ── Inférence du workspace ─────────────────────────────────────────
mempal_parse_stdin "$INPUT"

WS_ROOT=""
if [ "$MEMPAL_PARSE_OK" = "1" ] && [ -n "$MEMPAL_WORKSPACE" ]; then
    WS_ROOT="$MEMPAL_WORKSPACE"
else
    WS_ROOT="$(
        printf '%s' "$INPUT" | "$MEMPAL_PYTHON_BIN" -c '
import json, sys, os, re
def safe_str(v):
    return re.sub(r"[^a-zA-Z0-9_/.\-~]", "", str(v or ""))
try:
    data = json.load(sys.stdin)
except Exception:
    print("")
    sys.exit(0)
if not isinstance(data, dict):
    print("")
    sys.exit(0)
roots = data.get("workspace_roots") or data.get("workspace") or []
if isinstance(roots, list) and roots:
    print(safe_str(roots[0]))
elif isinstance(roots, str) and roots:
    print(safe_str(roots))
else:
    print(safe_str(data.get("cwd", os.getcwd())))
' 2>/dev/null
    )"
fi

if [ -z "$WS_ROOT" ]; then
    WS_ROOT="$PWD"
fi

mempal_log "RSM_${EVENT:-SessionStart}" "${MEMPAL_CONV_ID:-unknown}" \
    "workspace=$WS_ROOT"

# ── Émission du systemMessage ──────────────────────────────────────
#
# Message adapté selon l'événement :
#   * SessionStart — instruction générale
#   * UserPromptSubmit — instruction ciblée (la requête est dans le
#     contexte de l'agent, pas besoin de la répéter)

if [ "$EVENT" = "UserPromptSubmit" ]; then
    "$MEMPAL_PYTHON_BIN" -c '
import json, sys
ws = sys.argv[1] if len(sys.argv) > 1 else "."
msg = (
    "RSM semantic memory is available for this workspace. "
    "The user just submitted a prompt. Before answering, consider "
    "calling these RSM tools to pull relevant code context:\n"
    "1. rsm_store_list_indexes — see which repos are indexed\n"
    "2. rsm_store_select_index — activate the relevant index\n"
    "3. rsm_search (query=<keywords>) — broad code discovery\n"
    "4. rsm_prepare_context (task=<description>) — focused context pack\n"
    "If the repo is already indexed at " + ws + ", "
    "use rsm_search or rsm_prepare_context to pull the most "
    "relevant files, symbols, and relations before answering. "
    "Prefer RSM over manual grep/read for structural questions."
)
print(json.dumps({"continue": True, "systemMessage": msg}))
' "$WS_ROOT"
else
    # SessionStart — rappel général
    "$MEMPAL_PYTHON_BIN" -c '
import json, sys
ws = sys.argv[1] if len(sys.argv) > 1 else "."
msg = (
    "RSM (repo-semantic-memory) is available. This workspace at " + ws + " "
    "may have pre-built semantic indexes. When answering questions "
    "about code structure, dependencies, or architecture, use RSM tools:\n"
    "- rsm_store_list_indexes — list available indexes\n"
    "- rsm_store_select_index — activate the workspace index\n"
    "- rsm_search (query=<keywords>) — find relevant code\n"
    "- rsm_find_related (source_path=<file>) — explore connections\n"
    "- rsm_prepare_context (task=<description>) — build a context pack\n"
    "Use RSM for structural/architectural questions instead of grep/read."
)
print(json.dumps({"continue": True, "systemMessage": msg}))
' "$WS_ROOT"
fi
