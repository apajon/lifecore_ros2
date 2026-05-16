---
description: "Use when: creating clean, atomic Git commits from changes made during the current conversation, splitting work into logical units, excluding unrelated diffs, or generating Conventional Commits for semantic release workflows."
name: "Smart Commits Session"
argument-hint: "Optional: format=conventional|free, granularity=fine|medium|large, prefix, scope, lang=english|french"
agent: "agent"
tools: [vscode/toolSearch, execute, read, 'github/*', 'mempalace/*', edit, search, 'gitkraken/*']
---

# Smart Commits - Current Session

Your mission: create clean, atomic, readable commits using **only** the changes made during the current conversation.

Default behavior: execute the commits once the grouping is clear. Stop and ask only when a real ambiguity or ownership doubt requires clarification.

## User Parameters

Use these preferences if provided in **$ARGUMENTS**.

Recommended defaults when omitted:
- `lang=english`
- `format=conventional`
- `granularity=fine`

## Mandatory Rules

1. Never include pre-existing changes or changes unrelated to the current conversation.
2. If ownership of a file or hunk is ambiguous, ask for explicit confirmation before committing it.
3. Never make a catch-all commit.
4. Group changes by functional intent first: `fix`, `refactor`, `test`, `docs`, `chore`, `feat`, `perf`, `build`, `ci`.
5. Never use broad staging such as `git add .`; stage files or hunks selectively.
6. Never use destructive Git actions.
7. Default commit language is English unless `lang=french` is explicitly requested.

## Procedure

### Step 0 - Extract the session scope

Review the full conversation history and build an explicit list of files that were created, edited, or deleted during this session.

Output this exact block first:

```text
Conversation-touched files:
- <path/to/file1>
- <path/to/file2>
```

Treat that list as the strict scope filter for all later Git operations.

### Step 1 - Inspect the Git state

Inspect modified, staged, and unstaged changes. Prefer staged diffs if they are already meaningful; otherwise inspect unstaged diffs too.

Apply the session scope filter strictly:
- Retain only files and hunks attributable to the current conversation.
- Exclude everything else from proposed commits.
- Keep excluded items for the out-of-scope report.

### Step 2 - Build logical commit groups

Group changes by intent, not by file. Each group must be independently understandable and as small as safely possible according to `granularity`.

If two changes are tightly coupled and would be misleading or broken when split, keep them together and explain why.

### Step 3 - Generate commit messages

Message strategy:
- If `format=conventional`, use Conventional Commits.
- Otherwise use clear intent-oriented commit messages in the requested language.
- If `prefix` is provided, prepend it consistently.
- If `scope` is provided, apply it consistently when appropriate.

For Conventional Commits, follow these rules:
- Subject in imperative mood, lowercase, no trailing period, ideally 72 characters or fewer.
- Use `!` or a `BREAKING CHANGE:` footer only for real incompatible API changes.
- Add a short body only when it clarifies why grouping or behavior matters.

### Step 4 - Show the execution plan

Before staging, show this table:

| Commit | Type | Proposed message | Files | Justification |
|---|---|---|---|---|
| 1 | fix/refactor/... | ... | ... | ... |

Then ask exactly:

"I will run these commits now unless you want to adjust the grouping."

Do not wait for confirmation by default. Continue directly to execution unless the user interrupts or a blocking ambiguity exists.

### Step 5 - Stage and commit selectively

After showing the plan:
- Stage only the files or hunks that belong to the current logical group.
- Commit groups in a stable order, usually foundational changes first.
- Avoid mixing formatting-only changes with behavioral changes unless inseparable.

After each commit, print a one-line confirmation in this format:

```text
✅ Commit N/total - <message>
   Files: <list>
```

If a blocking ambiguity appears at this stage, stop before committing that group, ask the single most important clarifying question, then resume.

### Step 6 - Final summary

When finished, print a summary table:

| # | Commit message | Files | Version impact |
|---|---|---|---|
| 1 | `type(scope): subject` | `file.py` | patch / minor / major / none |

Version impact rules:
- `feat` -> minor
- `fix`, `perf`, `refactor` -> patch
- `!` or `BREAKING CHANGE` -> major
- `docs`, `ci`, `chore`, `build`, `style`, `test` -> none

Then verify explicitly:
- Every file from the session scope was either committed or intentionally excluded.
- No commit mixes orthogonal concerns.
- The version impact assigned to each commit is correct.

If a session-scoped file was missed, commit it before declaring success.

## Out-of-Scope Changes

If the Git diff contains files or hunks that were not touched during the current conversation, list them under:

```text
⚠️ Out-of-scope changes
```

Do not stage or include them unless the user explicitly asks you to do so.

## Quality Constraints

- Prefer the smallest safe commit set over fewer broad commits.
- A commit should be locally coherent for its scope and should preserve validation expectations as much as possible.
- If scope attribution is uncertain, stop and ask instead of guessing.
