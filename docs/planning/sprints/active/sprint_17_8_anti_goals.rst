Sprint 17.8 — Write Anti-Goals and Anti-Patterns
=================================================

**Status.** Active.

**Track.** Architecture / Research.

**Type.** Documentation.

**Objective.** Explicitly reject unsafe architectural directions for
``lifecore_state`` before any implementation sprint begins.

**Parent sprint.** :doc:`sprint_17_lifecore_state_rfc`.

Feature goal
------------

Write ``lifecore_state/anti_goals.rst`` so Sprint 17 documents what
``lifecore_state`` must not become. The document acts as a defensive guard
against architectural scope creep and design mistakes, providing reviewers with
explicit justification to reject overreaching proposals.

Lifecycle behavior contract
---------------------------

Sprint 17.8 is documentation-only. It must not change configure, activate,
deactivate, cleanup, shutdown, or error behavior for any existing
``lifecore_ros2`` node or component.

The document must keep these non-impact rules explicit:

- **configure:** no runtime resource creation changes.
- **activate:** no activation gate changes.
- **deactivate:** no deactivation behavior changes.
- **cleanup:** no cleanup behavior changes.
- **shutdown:** no shutdown behavior changes.
- **error:** no error recovery changes.

Context
-------

Sprint 17.7 documented message semantics. Sprint 17.8 now documents what the
architecture must explicitly reject. The term ``state`` is broad and invites
mission creep. Anti-goals protect against hidden complexity, over-engineering,
and pattern mistakes imported from other systems.

Impacted modules
----------------

``lifecore_state/anti_goals.rst``
  Primary deliverable for Sprint 17.8.

``docs/planning/sprints/active/``
  Hosts this active planning card and the main Sprint 17 coordinator.

``src/``, ``tests/``, and ``examples/``
  Not impacted. Sprint 17.8 must not change runtime behavior, tests, or public
  APIs.

Document location
-----------------

**File:** ``lifecore_state/anti_goals.rst``

Required sections
-----------------

1. **Purpose**
   Explain why anti-goals matter and how reviewers should use this document.

2. **Why anti-goals matter**
   Cover that ``state`` is a broad term that risks mission creep, that
   anti-goals anchor the architecture against worse alternatives, and that
   they enable reviewers to reject bad proposals with explicit justification.

3. **Not a robotics operating system**
   Reject global orchestration, mission planning, replacement for ROS 2, and
   global middleware.

4. **Not a global orchestration runtime**
   Reject workflows, planning engines, global decision engines, and anything
   beyond local, explicit, per-node scope.

5. **Not a hidden synchronization framework**
   Require that all synchronization be explicit: topics visible, registries
   visible, policies visible, versions trackable, sequences detectable.

6. **Not a giant ECS platform**
   Acknowledge that ECS ideas may inspire design, but reject an ECS runtime
   with entity-wide queries, system scheduling, and framework overhead.

7. **Not an EventBus**
   Acknowledge that events may be useful later for diagnostics, but reject
   publish-on-set, magic observable properties, and implicit listeners for
   state mutations.

8. **Not a plugin framework**
   Reject dynamic behavior loading, shared library plugins, plugin registries,
   and convention-over-configuration magic.

9. **Not a factory or spec system**
   Reject central factories, global specs that create the application,
   declarative instantiation, and anything that removes imperative explicit
   code as the primary construction path.

10. **Not codegen-first**
    Acknowledge that codegen may be useful later, but reject it before message
    and concept stability and before the human review cycle matures.

11. **No giant StateManager class**
    Explicitly reject a single class that combines registry management,
    publishers, subscribers, lifecycle, callbacks, stale monitoring, command
    handling, validation, logging, and orchestration. Require separate classes
    with clear, single responsibilities.

12. **No magical StateField**
    Reject automatic publish-on-set, complex callbacks hidden in field
    accessors, lifecycle awareness in core, registry awareness in core,
    descriptor awareness in core, and global registry knowledge.

13. **No automatic publish-on-set in core**
    Require explicit ``set()``, mark-dirty, and flush-delta patterns. Keep core
    and publishing separated.

14. **No auto-register unknown fields by default**
    Reject automatic registration because it breaks API contracts, enables
    typos, defeats static schemas, creates implicit coupling, and makes
    debugging harder.

15. **No command-as-truth**
    Restate that ``StateCommand`` is intent and not reality, that
    ``StateUpdate`` is truth, that commands require feedback, and that an
    accepted command must become visible in later state.

16. **No lifecycle contamination in core**
    Require that ``lifecore_state_core`` remain pure Python with no ``rclpy``
    imports, no ROS 2 awareness, and no lifecycle imports.

17. **Safe future directions**
    Distinguish patterns that are not anti-goals but are deferred: diagnostics
    events for observability, CLI and visualization tools, codegen after
    stabilization, compact message optimization, and command-line inspection.

18. **Decision summary**
    Summarize the rejected directions and state the architectural principle
    they share.

Acceptance criteria
-------------------

- [ ] All major anti-patterns explicitly rejected
- [ ] Rationale for each rejection clear
- [ ] ``No giant manager`` pattern documented
- [ ] ``No magic`` principle stated
- [ ] Lifecycle/core separation enforced
- [ ] Safe future directions listed
- [ ] Mandatory review phrase included

Content quality checklist
-------------------------

- [ ] Anti-goals are specific, not vague
- [ ] Each rejection has justification
- [ ] Patterns are tied to real risks
- [ ] Language is direct but not hostile
- [ ] Document is usable as PR review reference

Success criteria
----------------

Reviewers can cite this document to:

- Reject architectural overreach
- Require simpler alternatives
- Enforce separation of concerns
- Prevent hidden complexity

Review requirement
------------------

Mandatory phrase:
"ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17."
