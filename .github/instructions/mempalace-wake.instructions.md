---
name: "MemPalace Session Wake-Up"
description: "Ordonne à Copilot d'interroger MemPalace (search + diary_read) avant de répondre sur ce projet. Fallback à base d'instructions ; le hook .github/hooks/mempalace-wake-copilot.json est le mécanisme préféré (inférence dynamique du wing)."
applyTo: "**"
---

# MemPalace Session Wake-Up

Ce fichier est le **fallback instructions** du hook Copilot `SessionStart`
(`.github/hooks/mempalace-wake-copilot.json` + `mempal_wake_hook_copilot.sh`).
Le hook est le mécanisme préféré car il infère dynamiquement le wing ;
cette instruction est un filet de sécurité avec le wing hardcodé
`lifecore_ros2`.

## Règle

Avant de répondre à toute question touchant au code, aux décisions
d'architecture, aux conventions ou à l'historique de ce projet,
exécute ces deux appels MemPalace :

1. `mempalace_search` avec `wing=lifecore_ros2`, `query=<mots-clés pertinents>`
2. `mempalace_diary_read` avec `agent_name=copilot`, `wing=lifecore_ros2`, `last_n=10`

Utilise les résultats tels quels s'ils répondent à la question.
Ne résume jamais les mots de l'utilisateur stockés dans MemPalace.

## Adaptation pour d'autres projets

Pour un autre projet utilisant MemPalace, copie ce fichier dans
`.github/instructions/` et remplace `lifecore_ros2` par le wing
correspondant (le `basename` du dossier racine du projet).
