#!/bin/bash
# MEMPALACE COPILOT SAVE HOOK — Auto-save at session end
#
# GitHub Copilot "Stop" hook. Adapté du hook Claude Code Stop
# (mempal_save_hook.sh) pour le contrat de hooks Copilot.
#
# Comportement :
#   1. Parse le payload Stop de Copilot (transcript_path si dispo).
#   2. Lance un mine MemPalace sur la transcription (async).
#   3. Retourne {"continue": true} — ne bloque jamais l'arrêt.
#
# Différences vs Claude Code :
#   * Copilot n'a pas de stop_hook_active → pas de boucle infinie.
#   * Pas de blocage (decision: block) → toujours continue: true.
#   * Le mine est asynchrone (background) pour ne pas bloquer.
#   * Réutilise lib/common.sh pour kill-switch et logging.
#
# === INSTALL ===
#
# Le hook est déclaré dans mempalace-wake-copilot.json (avec SessionStart
# et PreCompact). Copilot le découvre automatiquement.

_mempal_self="${BASH_SOURCE[0]:-$0}"
_mempal_dir="$(cd "$(dirname "$_mempal_self")" 2>/dev/null && pwd)"
# shellcheck source=lib/common.sh
. "$_mempal_dir/lib/common.sh"

if mempal_is_disabled; then
    printf '{"continue": true}\n'
    exit 0
fi

INPUT="$(cat)"

# ── Parse Copilot Stop payload ─────────────────────────────────────
#
# Copilot Stop peut contenir transcript_path. On tente l'extraction.
# Si absent, on log et on passe — le mine automatique n'est pas
# critique pour le fonctionnement du hook.

TRANSCRIPT_PATH="$(
    printf '%s' "$INPUT" | "$MEMPAL_PYTHON_BIN" -c '
import json, sys, re
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
tp = safe_str(data.get("transcript_path", ""))
print(tp)
' 2>/dev/null
)"

TRANSCRIPT_PATH="${TRANSCRIPT_PATH/#\~/$HOME}"

mempal_log "Stop" "${MEMPAL_CONV_ID:-unknown}" \
    "transcript=${TRANSCRIPT_PATH:-none}"

# ── Validation du chemin ───────────────────────────────────────────
is_valid_transcript_path() {
    local path="$1"
    [ -n "$path" ] || return 1
    case "$path" in
        *.json|*.jsonl) ;;
        *) return 1 ;;
    esac
    case "/$path/" in
        */../*) return 1 ;;
    esac
    return 0
}

# ── Mine asynchrone ────────────────────────────────────────────────
if is_valid_transcript_path "$TRANSCRIPT_PATH" && [ -f "$TRANSCRIPT_PATH" ]; then
    mempalace mine "$(dirname "$TRANSCRIPT_PATH")" --mode convos \
        >> "$MEMPAL_CURSOR_LOG" 2>&1 &
elif [ -n "$TRANSCRIPT_PATH" ]; then
    mempal_log "Stop" "${MEMPAL_CONV_ID:-unknown}" \
        "skipping invalid transcript: $TRANSCRIPT_PATH"
fi

# Ne jamais bloquer l'arrêt — le mine est best-effort
printf '{"continue": true}\n'
