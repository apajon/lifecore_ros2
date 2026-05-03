Sprint 15 - Tooling and generated nodes
=======================================

**Objective.** Explore scaffolding once the core patterns are stable enough to
generate safely.

**Deliverable.** A documented tooling direction for generating or reviewing
``lifecore_ros2`` node skeletons.

---

Decisions already made
----------------------

- Tooling waits until the runtime conventions are stable enough to generate.
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

- lifecycle comparison example
- internal cascade contract
- cleanup ownership contract
- health/status API
- watchdog scope

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
- config-driven application framework
- plugin loading

---

Success signal
--------------

- [ ] Generated skeletons look like code a maintainer would accept.
- [ ] Tooling reduces setup friction without expanding runtime scope.
