---
description: "Persist important conversation insights to mempalace. Use when: end of session, after significant work, capturing architecture decisions, anti-patterns, conventions, reusable patterns."
name: "Historize to MemPalace"
argument-hint: "Optional: focus on a specific topic (e.g., 'lifecycle regression', 'component contract')"
agent: "agent"
tools: [mempalace/*]
---

# MemPalace Historization — Conversation Review

You are a technical archivist. Your mission: analyze the current conversation and persist important elements to mempalace so they are reusable in future sessions.

## Procedure

### 1. Conversation Analysis

Review the full conversation history. Identify and classify each notable element according to these categories (in decreasing priority):

| Category | Examples | Importance |
|----------|----------|-----------|
| **Architecture decisions** | Design choices, why pattern X over Y | ★★★★★ |
| **Confirmed anti-patterns** | Errors encountered, bugs caused by a bad pattern | ★★★★★ |
| **Established conventions** | Naming, structure, code rules adopted | ★★★★ |
| **Reusable patterns** | Code patterns, reproducible technical solutions | ★★★★ |
| **Inter-component contracts** | Interfaces, OWNER rules, API guarantees | ★★★★ |
| **Technical knowledge** | ROS2, MoveIt2, EtherCAT, tooling facts | ★★★ |
| **Migration notes** | Breaking changes, upgrades, deprecations | ★★★ |
| **Problem resolutions** | Diagnosis + fix of a non-trivial problem | ★★★ |

**Minimum threshold: ★★★.** Only persist elements rated ★★★ or higher. Elements at ★★ and below are too ephemeral to justify a drawer.

**Ignore**: trivial fixes, typos, simple questions without insight, intermediate debug steps, information already in source code docstrings.

### 2. Wing Routing

For each identified element, determine the target wing:

- **`ros2`**: transverse ROS2 knowledge reusable across projects (lifecycle, topics, services, MoveIt2, ros_control, tf2, EtherCAT, ROS2 conventions)
- **`lifecore_ros2`**: advanced lifecycle patterns (components, orchestration)
- **Other relevant wing**: if the content belongs to a specific existing domain

**Rule**: if a fact is project-specific but specializes a general ROS2 rule, persist in the project wing with a reference `[see: ros2/<room>]`. Never duplicate across wings.

### 3. Room Selection

Use existing rooms (hyphenated lowercase slugs). Only create a new room if no existing one fits.

Standard ROS2 rooms: `fundamentals`, `lifecycle`, `moveit2`, `communication`, `build-and-tooling`, `industrial-robotics`, `qos`, `launch`, `actions`, `services`, `parameters`, `topics`, `conventions`, `debugging`, `observability`

Standard lifecore_ros2 rooms: `architecture`, `lifecycle`, `components`, `communication`, `contracts`, `validation`, `anti-patterns`, `conventions`, `incident-log`, `failure-modes`, `observability`

### 4. Deduplication (MANDATORY)

Follows the project deduplication policy. Before EACH addition:

1. Search the **target wing + room** (never globally) with `mcp_mempalace_mempalace_check_duplicate` or `mcp_mempalace_mempalace_search`
2. Apply similarity thresholds as guidance:
   - **≥ 0.86** — near-duplicate → **enrich** the existing drawer, do not create a new one
   - **≥ 0.55 and < 0.86** — related content → manual review, only create if it represents a distinct rule/pattern/anti-pattern
   - **< 0.55** — likely distinct → creation acceptable if ≥ ★★★
3. If new content supersedes an older entry → mark the old one as obsolete
4. Always prefer enriching an existing drawer over creating a rephrased duplicate

### 5. Writing Drawers

Content format for each drawer:

```
STATUS: active
CREATED: {today_date}

[type: {type}] {concise title}

{factual, dense, structured content}

{cross-reference if applicable: [see: ros2/lifecycle]}
```

Valid types: `architecture-rule`, `code-convention`, `component-contract`, `reusable-pattern`, `anti-pattern`, `project-decision`, `transverse-knowledge`

### 6. Knowledge Graph (optional but recommended)

For highly connected elements (component dependencies, architecture relations), also add a KG entry with `mcp_mempalace_mempalace_kg_add` to enrich the knowledge graph.

### 7. Session Diary

Write a short session summary to the mempalace diary with `mcp_mempalace_mempalace_diary_write`:
- What was done
- Decisions made
- Elements persisted (list of drawers added/modified)

## Final Report

After historization, display a structured summary:

```
## 📋 MemPalace Historization — Summary

### Persisted Elements
| # | Wing | Room | Type | Title | Action |
|---|------|------|------|-------|--------|
| 1 | lifecore_ros2 | architecture | architecture-rule | ... | created/enriched |
| 2 | ros2 | lifecycle | reusable-pattern | ... | created |

### Skipped Elements (already present)
- ...

### Diary
- Session summary written ✓

### Statistics
- Drawers created: X
- Drawers enriched: Y
- KG entries added: Z
```

## Constraints

- **Never persist** secrets, tokens, or sensitive data
- **Prefer enriching** an existing drawer over creating a similar new one
- **Be factual**: no opinions, only technical facts verified in the conversation
- **Be dense**: use AAAK format when relevant to maximize information per token
- If mempalace tools are unavailable, state it clearly and propose saving to `/memories/` as fallback
