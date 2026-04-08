# Copilot Assets

This directory contains versioned internal Copilot assets used by the engineering team.

## Purpose

These files are internal engineering assets, not runtime package code.
They support day-to-day development workflows across:

- feature delivery orchestration
- code and architecture review workflows
- regression investigation and recovery
- documentation planning and synchronization

## Structure

- `agents/`: specialist agent definitions.
- `orchestrators/`: orchestration agents that coordinate specialist agents.
- `prompts/`: reusable prompt templates.
- `skills/`: skill assets and domain playbooks.
- `hooks/`: hook-related assets, including frontmatter validation helpers.
- `instructions/`: additional internal instruction material when needed.

## Notes

- Keep `.github/` minimal and reserved for GitHub/Copilot-required files.
- Required GitHub instruction files remain under `.github/copilot-instructions.md` and `.github/instructions/`.
- Use readable kebab-case file names for consistency.
