Sprint 20+ - Tooling and generated nodes (conditional)
======================================================

Status:
  Deferred / Conditional

Reason:
  Deferred after Sprint 13 because tooling and code generation should follow
  stabilized conventions, not define them prematurely.

Launch condition:
  Only start after examples, conventions, core API boundaries, and
  ``lifecore_state`` boundaries are stable.

**Historical status.** This card used to be Sprint 15. It is now deferred and
conditional. It is not the default next sprint after Sprint 13.

**Track.** Tooling / Codegen.

**Priority.** P5 conditional - advanced tooling, generation, and automation.

**Condition.** Start only after examples, conventions, the core API, the
``lifecore_state`` boundary, and real generation needs are stable.

**Objective.** Explore scaffolding once the core patterns are stable enough to
generate safely.

**Deliverable.** A documented tooling direction for generating or reviewing
``lifecore_ros2`` node skeletons.

---

Decisions already made
----------------------

- Tooling waits until the runtime conventions are stable enough to generate.
- Codegen follows mature conventions; it does not discover the architecture.
- Generated code must follow naming, cleanup, lifecycle, and gating
  conventions.
- MCP remains outside the runtime library.

Candidate tooling directions:

- Copilot skill or prompt workflow that generates a lifecycle component node
- template for subscriber / publisher / timer / service composition
- checks that generated code follows naming, cleanup, and gating conventions
- companion-repo examples that generated code can point to

To decide during sprint planning
--------------------------------

- Whether the first deliverable is a prompt, a Copilot skill, or a repository
  script.
- Whether generation starts with core-style minimal skeletons or
  companion-repo concrete scenario scaffolds.
- Which conventions are stable enough to enforce automatically.

---

Prerequisites
-------------

Do not start this sprint until these are stable:

- adoption examples and documentation
- lifecycle conventions
- core API
- ``lifecore_state`` boundary
- real generation needs

---

Scope boundaries
----------------

In scope:

- developer tooling
- scaffolding
- documentation of generated-code expectations

Out of scope:

- runtime AI behavior
- direct MCP integration in the core library
- config-driven application platform
- plugin loading
- magic runtime behavior
- hard dependency on an immature spec format

---

Success signal
--------------

- [ ] Generated skeletons look like code a maintainer would accept.
- [ ] Generated code remains readable and testable.
- [ ] Tooling reduces setup friction without expanding runtime scope.
- [ ] Tooling is optional; the framework remains usable without it.
