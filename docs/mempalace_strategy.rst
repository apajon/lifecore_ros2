Mempalace Strategy
==================

This document defines how mempalace is used as a shared knowledge system across ROS 2 projects.

Why a Single Global Mempalace
-----------------------------

Mempalace is a **single global knowledge base** with multiple wings.
Each project does not get its own mempalace instance.
Knowledge is organized by scope, not by workspace.

Wing Naming Convention
----------------------

All wing names use **lowercase with underscores**. No uppercase, no camelCase.

================================  =========  ==========================================
Wing                              Scope      Content
================================  =========  ==========================================
``ros2``                          Shared     General ROS 2 knowledge (lifecycle, QoS,
                                             tf2, nav2, MoveIt, ros-control, etc.)
``<project_name>``                Project    Project-specific architecture, contracts,
                                             decisions (e.g., ``lifecore_ros2``)
================================  =========  ==========================================

Standard Room Categories
------------------------

Each wing can use these room slugs (hyphenated lowercase).
Create rooms only when content exists.

====================  ======================================================
Room                  Purpose
====================  ======================================================
architecture          High-level design decisions, layer definitions
lifecycle             Lifecycle state machine, transitions, hooks
components            Component contracts, interfaces, extension points
managers              Orchestrators, controller managers, lifecycle managers
communication         Topics, services, actions patterns
debugging             Debug patterns and diagnostic commands/tooling tips
observability         Logging, metrics, tracing, and runtime signals
configuration         URDF, SRDF, xacro, YAML, parameters
contracts             Inter-component agreements, API guarantees
anti-patterns         Confirmed mistakes to avoid
incident-log          Production/integration incidents: diagnosis, root cause,
                      fix applied, and prevention rule
failure-modes         Known failure modes with trigger conditions and recovery
validation            Testing rules, CI gates, quality checks
migration-notes       Breaking changes, version upgrades, deprecations
conventions           Naming, style, tooling conventions
====================  ======================================================

Entry Classification
--------------------

Every entry stored in mempalace should be classifiable as one of these types.
When the type is not obvious, tag it: ``[type: architecture-rule]``.

====================  ====================================================  ===========
Type                  Description                                           Typical wing
====================  ====================================================  ===========
architecture-rule     Structural constraint on the system                   project/ros2
code-convention       Repeatable coding pattern or style rule               project/ros2
component-contract    Interface agreement between components                project
reusable-pattern      General pattern applicable across projects            ros2
anti-pattern          Confirmed mistake to never repeat                     project/ros2
project-decision      Context-specific choice with rationale                project
transverse-knowledge  General ROS 2 fact reusable everywhere                ros2
migration-note        Breaking change or upgrade path                       project/ros2
====================  ====================================================  ===========

Scope Rules
-----------

- Native ROS 2 knowledge (lifecycle spec, QoS, tf2, etc.) → wing ``ros2``
- Project-specific contracts (LifecycleComponent hooks, etc.) → project wing
- If a project rule specializes a transverse rule, **reference** it: ``[see: ros2/lifecycle]``
- **Do not duplicate** transverse knowledge in project wings

Deduplication Policy
--------------------

Before writing to mempalace:

1. Search the target wing + room for semantically similar content.
2. If an existing entry covers **80%+** of the same information, **enrich** it instead of creating a new drawer.
3. If the new entry supersedes an older one, mark or delete the old entry.
4. Never create two drawers with the same core rule in different phrasings.

Freshness Metadata
------------------

Use this header in drawer content when the entry may evolve::

    STATUS: active | obsolete | review-needed
    CREATED: YYYY-MM-DD
    REVISED: YYYY-MM-DD (optional)
    VERSION: N (optional)

Cross-References
----------------

When a project rule depends on a transverse rule, store a lightweight reference::

    [see: ros2/lifecycle] for the native state machine this component extends

This avoids duplicating general knowledge and keeps the dependency explicit.

What to Persist
---------------

**Do persist:**

- Durable architecture decisions
- Repeatable conventions
- Important inter-component contracts
- Confirmed anti-patterns
- Rules that prevent future regressions

**Do not persist:**

- Trivial fixes or one-time details
- Temporary session results
- Debugging steps
- Information already in source code docstrings

Read Strategy
-------------

When an agent gathers context from mempalace:

1. Query the **project wing** first (e.g., ``lifecore_ros2``).
2. Then query the **transverse wing** (``ros2``).
3. Merge results. Project rules take precedence only if explicitly documented as a local override.
4. If nothing from mempalace, **fallback silently** to local docs (``architecture.rst``, ``README.md``, then workspace search).

Fallback Behavior
-----------------

- If mempalace tools are unavailable, **never fail or block**.
- Continue silently with local documentation sources.
- The fallback chain is defined in ``.github/instructions/ros2-architecture-context.instructions.md``.
