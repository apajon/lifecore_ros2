#!/bin/bash
# MEMPALACE COPILOT PRECOMPACT HOOK — Emergency save before compaction
#
# GitHub Copilot "PreCompact" hook. Adapté du hook Claude Code
# PreCompact (mempal_precompact_hook.sh) pour le contrat Copilot.
#
# Comportement :
#   1. Parse le payload PreCompact de Copilot.
#   2. Lance un mine MemPalace synchrone (bloquant) — la compaction
#      efface du contexte, c'est le dernier moment pour sauver.
#   3. Retourne {"continue": true}.
#
# Différences vs Claude Code :
#   * Même sémantique « sauver avant compaction ».
#   * Utilise lib/common.sh pour le kill-switch et le logging.
#   * Le mine est synchrone (foreground) — on veut garantir la
#     sauvegarde avant que le contexte ne soit perdu.
#   * Sortie Copilot : {"continue": true} au lieu de {}.
#
# === INSTALL ===
#
# Le hook est déclaré dans mempalace-wake-copilot.json. Copilot le
# découvre automatiquement.

_mempal_self="${BASH_SOURCE[0]:-$0}"
_mempal_dir="$(cd "$(dirname "$_mempal_self")" 2>/dev/null && pwd)"
# shellcheck source=lib/common.sh
. "$_mempal_dir/lib/common.sh"

if mempal_is_disabled; then
    printf '{"continue": true}\n'
    exit 0
fi

INPUT="$(cat)"

# ── Parse Copilot PreCompact payload ───────────────────────────────
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

mempal_log "PreCompact" "${MEMPAL_CONV_ID:-unknown}" \
    "transcript=${TRANSCRIPT_PATH:-none}"

# ── Validation ─────────────────────────────────────────────────────
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

# ── Mine synchrone (foreground) ────────────────────────────────────
#
# Contrairement au hook Stop (asynchrone), le PreCompact mine en
# foreground : la compaction va supprimer du contexte, donc on veut
# être sûr que la sauvegarde est terminée avant de continuer.
if is_valid_transcript_path "$TRANSCRIPT_PATH" && [ -f "$TRANSCRIPT_PATH" ]; then
    mempalace mine "$(dirname "$TRANSCRIPT_PATH")" --mode convos \
        >> "$MEMPAL_CURSOR_LOG" 2>&1
elif [ -n "$TRANSCRIPT_PATH" ]; then
    mempal_log "PreCompact" "${MEMPAL_CONV_ID:-unknown}" \
        "skipping invalid transcript: $TRANSCRIPT_PATH"
fi

# Ne jamais bloquer la compaction — le mine est best-effort
printf '{"continue": true}\n'
