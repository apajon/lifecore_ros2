---
description: "Analyze the current conversation and git diff to propose a sequence of logical commits in Conventional Commits format (smart-release compatible). Use when: preparing a commit, splitting work into atomic units, ensuring semantic versioning compatibility."
name: "Logical Commits (smart-release)"
argument-hint: "Optional: scope or context hint (e.g., 'component cleanup', 'lifecycle fix')"
agent: "agent"
tools: [read, edit, search, 'mempalace/*', 'github/*', 'gitkraken/*']
---

# Logical Commits — Conventional Commits Format

Analyze the current conversation and the git diff, then **stage and commit** the changes in a sequence of well-scoped, atomic commits in **Conventional Commits** format, compatible with semantic-release and release-please.

> **Default behavior: commit.** Execute the commits unless a blocking ambiguity requires clarification. If clarification is needed, ask the single most important question, wait for the answer, then proceed.

## Step 0 — Extract touched files from the conversation

Review the full conversation history. Collect every file path that was **created, edited, or deleted** during this session. Build an explicit list:

```
Conversation-touched files:
- <path/to/file1>
- <path/to/file2>
...
```

This list is the **scope filter**: only changes to these files are eligible for the commits produced by this prompt. Any file present in the diff but absent from this list must be flagged separately (see Step 5).

## Step 1 — Collect the diff

Run the following in the terminal:

```bash
git diff --cached --stat && git diff --cached
```

If the output is empty (nothing staged), fall back to:

```bash
git diff --stat && git diff
```

Use the first non-empty result.

**Apply the scope filter**: retain only hunks belonging to files identified in Step 0. Discard the rest for now — they will be surfaced in Step 5.

## Step 2 — Identify logical units of work

Group the changed files and hunks by **intent**, not by file. Each group should represent one coherent, independently deployable change. Ask: "What problem does this group solve?"

Typical groups:

| Intent | Conventional type |
|--------|------------------|
| New behavior or capability | `feat` |
| Bug fix | `fix` |
| Internal restructuring, no behavior change | `refactor` |
| Performance improvement | `perf` |
| Documentation (code or docs/) | `docs` |
| Tests only | `test` |
| Build, packaging, CI | `build` / `ci` |
| Tooling, config, chores | `chore` |
| Reverting a previous change | `revert` |

**Breaking change**: add `!` after the type (`feat!:`) or add `BREAKING CHANGE: <description>` in the footer.

## Step 3 — Write Conventional Commit messages

For each logical group, produce a commit block in this format:

```
<type>[(<scope>)][!]: <subject>

[<body — why this change, not what>]

[BREAKING CHANGE: <description>]
[Closes #<issue>]
```

Rules:
- Subject: imperative mood, lowercase, ≤ 72 chars, no trailing period.
- Scope: the component, module, or subsystem affected (optional but recommended).
- Body: explain the *why* only if the subject alone is not self-explanatory.
- Footer: include `BREAKING CHANGE` if the public API changes incompatibly.

## Step 4 — Stage and commit

For each logical group, in recommended order (foundational first), run:

```bash
git add <file1> <file2> ...
git commit -m "<type>(<scope>): <subject>" -m "<body>" -m "<footer>"
```

Omit `-m "<body>"` and `-m "<footer>"` when empty.

After each commit, print a one-line confirmation:

```
✅ Commit N/total — <type>(<scope>): <subject>
   Files: <list>
```

If a blocking ambiguity prevents grouping a file correctly (e.g., cannot determine whether a change is `fix` or `feat`), **stop before that commit**, ask the single most important clarifying question, and resume once answered.

## Step 5 — Post-commit summary

Once all commits are done, print a summary table:

| # | Commit message | Files | Version impact |
|---|----------------|-------|----------------|
| 1 | `type(scope): subject` | `file.py` | patch / minor / major / none |

Then verify:
- Every file from the **scope filter** was committed.
- No single commit mixed orthogonal concerns.
- Version impact column is correct: `feat` → minor, `fix`/`perf`/`refactor` → patch, `!` → major, `docs`/`ci`/`chore`/`build`/`style`/`test` → **none**.

If a file was missed, commit it now with the correct type before declaring done.

**Out-of-scope files**: if the diff contains files not touched during this conversation, list them explicitly at the end under a `⚠️ Out-of-scope changes` section. **Do not stage or include them in any commit.** Only process them if the user explicitly asks to include them.
