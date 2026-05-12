# Roadmap

<!-- Canonical positioning sentence — keep in sync with pyproject.toml project.description. -->
lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy — no hidden state machine.

---

## Current status — post-Sprint 14

Sprint 14 is complete. The project is past the old Sprint 8 / 0.4.0 planning
state; the core library is usable for professional evaluation while API
stability remains experimental until `1.0.0`.

The core library provides:

- `LifecycleComponentNode` and `LifecycleComponent` base classes
- `TopicComponent`, `LifecyclePublisherComponent`, `LifecycleSubscriberComponent` implementations
- `when_active` decorator for activation gating
- `get_or_create_callback_group` helper for node-owned, idempotent callback group creation
- `_is_active` protected by `_active_lock` — concurrency contract is GIL-independent
- In-flight callback policy documented ("drop at next gate")
- Concurrency safety via RLock and reentrant-call detection
- Strict lifecycle contract with error handling and rollback
- Health/status reporting and lightweight watchdog observation
- Lifecycle-aware parameter ownership and runtime mutability policies
- Comprehensive test coverage (unit, concurrency, integration)
- Complete documentation and examples

See [API Reference](docs/api.rst) and [Getting Started](docs/getting_started.rst) to begin.

---

## Adoption and hardening

Before pursuing new features, the project is focused on making the library adoptable at scale:

- Clear positioning and ergonomic APIs
- Bulletproof concurrency model
- Strict lifecycle semantics with actionable diagnostics
- Rich test coverage for confidence
- Strategic design notes for future extensions

**See [Adoption & Hardening Roadmap](docs/planning/adoption_hardening.rst)** for the nine-concern roadmap.

Current status: adoption hardening is complete through Sprint 13, and Sprint 14
closed the planning-alignment pass. The next work
does not automatically have to extend the core package; companion examples,
documentation, architecture RFCs, DX, and tooling can outrank core features when
they reduce risk or improve adoption.

---

## Strategic direction

The project is positioned as an **inside-the-node** discipline layer: below launch files, lifecycle managers, and system orchestrators; above raw `rclpy` lifecycle primitives.

It is not a launcher, not a Nav2-style lifecycle manager, and not a replacement for ROS 2 lifecycle semantics. The message to validate with users is:

> Build predictable ROS 2 nodes.

**See [Strategic Cap](docs/planning/strategy.rst)** for the working product thesis, boundaries, adoption sequence, and publication gate.

The core should remain a small, explicit, ROS-native lifecycle runtime and
component composition helper. Event buses, ECS ideas, state stores, codegen,
DSLs, plugin systems, and advanced tooling may become separate modules or
companion work; they should not be absorbed into `lifecore_ros2` by default.

The future distributed typed state model should be developed as a separate
`lifecore_state` track. This keeps lifecycle orchestration separate from state as
source of truth and prevents the lifecycle core from becoming a monolithic
runtime framework.

---

## Planning tracks

A sprint may target core, companion, docs, architecture, tooling, DX, external
modules, or research. Priority is based on risk reduction, adoption leverage,
architectural clarification, and strategic sequencing, not package location.

- **Track A — Core lifecore_ros2:** maintain, harden, document, fix, and improve ergonomics without broad scope expansion.
- **Track B — Companion / Adoption:** comparative examples, tutorials, demonstrations, onboarding, and user-facing docs.
- **Track C — State Architecture:** prepare a separate `lifecore_state` model without polluting the lifecycle core.
- **Track D — DX / Testing / Diagnostics:** fixtures, fake components, activation helpers, diagnostics, and lightweight developer support.
- **Track E — Tooling / Codegen:** scripts, templates, scaffolding, and CLI work after conventions stabilize.
- **Track F — Research / RFC:** decision documents, disposable prototypes, architectural framing, and risk analysis.

Priority model:

- **P0:** Project coherence and roadmap debt
- **P1:** Usage proof and adoption
- **P2:** Separate future architecture
- **P3:** API hardening, tests, and diagnostics
- **P4:** New core abstractions
- **P5:** Advanced tooling, generation, and automation

## Next planning window

Sprint 14 completed the planning-alignment pass. The recommended sequence after
Sprint 14 is:

- **Sprint 15 — Companion Adoption Examples** (Companion / Adoption, P1): strengthen concrete comparison examples and runtime proof.
- **Sprint 16 — Test Ergonomics and Diagnostics Polish** (Core + DX, P1/P3): make lifecycle tests easier and failures clearer without large abstractions.
- **Sprint 17 — lifecore_state Architecture RFC** (State Architecture / Research, P2): decide boundaries, naming, concepts, and go/no-go before coding.
- **Sprint 18 — lifecore_state_msgs ABI Prototype** (State Architecture / ROS ABI, P2 conditional): prototype minimal ROS messages only if Sprint 17 validates the direction.
- **Sprint 19 — Minimal Factory and Registry** (Core Extension, P4 conditional): launch only after repeated real pain proves manual instantiation is insufficient.
- **Sprint 20+ — Tooling and Generated Nodes** (Tooling / Codegen, P5 conditional): generate only after examples, conventions, API, and state boundaries stabilize.

The historical Sprint 14 and Sprint 15 cards are now deferred/conditional. They
are no longer the default next steps.

**See [Sprint Planning](docs/planning/sprints/README.rst)** for the execution plan.

---

## Backlog

The backlog separates near-term strategic work, medium-term candidates, and
ideas that remain deliberately deferred until there is a concrete user need.

**See [Planning Backlog](docs/planning/backlog.rst)** for:

- Lifecycle policies (ordering, full-activation semantics)
- Internal component cascade and broader dependency policy questions
- Error handling contract (propagation rules, rollback policy)
- Component state and health (introspection, diagnostics)
- Execution and timing (callback gating, duration tracking)
- Testing utilities (fixtures, fake components)
- Observability (structured logging, tracing)
- Parameters and runtime configuration
- Config and specs (application-level configuration, deferred)
- Factory and registry (dynamic component loading, conditional Sprint 19+)
- Tooling and generated nodes (conditional Sprint 20+)
- ~~Callback group management (per-component groups, concurrency utilities)~~ **Shipped Sprint 8**
- Additional components (`ActionComponent`, parameter components)
- Binding layer (if component hierarchy becomes overloaded)
- Release status metadata (`Development Status :: 4 - Beta` promotion gate)
- README badges (once on PyPI)

Each item includes a rationale for deferral and placement notes for future implementation.

---

## Companion examples repository

**See [Examples Repository Plan](docs/planning/examples_repo.rst)** for the full planning.

**Status**: repository exists and already hosts the applied sensor watchdog comparison used as the first companion proof point. After Sprint 14, companion adoption work is a high-priority track: strengthening that proof can be more valuable than a new internal feature.

Start with the [sensor watchdog lifecycle comparison](https://github.com/apajon/lifecore_ros2_examples/blob/main/examples/lifecycle_comparison/README.md) in the companion repository.

---

## Do not do now

- no full `AppSpec` system now
- no generated nodes now
- no plugin framework now
- no ECS framework in core
- no general EventBus in core
- no StateStore in core
- no complex recovery automation now
- no factory until repeated pain is proven

---

## Design decisions and architecture

See [Architecture](docs/architecture.rst) for the lifecycle model, component contracts, concurrency guarantees, and strict transition rules.

See [Naming Conventions](.github/instructions/naming-conventions.instructions.md) for stable naming rules.

See **Design Notes** under [docs/design_notes/](docs/design_notes/) for detailed decisions on:

- Runtime introspection
- Dynamic components
- Observability
- Error handling (pending implementation)
- Lifecycle policies (pending implementation)
- Callback groups (pending implementation)

---

## Versioning strategy

The project uses [Conventional Commits](https://www.conventionalcommits.org/) and [python-semantic-release](https://python-semantic-release.readthedocs.io/).

**Current status:** version is in the `0.x` series and package metadata uses `Development Status :: 3 - Alpha`. This signals that the public API is not yet considered stable. Experimental adoption is welcome; breaking changes may still occur on minor bumps.

**Rules in effect:**

- `allow_zero_version = true` — semantic-release stays in `0.x` and does not force a `1.0.0` bump automatically
- `major_on_zero = false` — breaking changes (BREAKING CHANGE commits) increment the minor version while in `0.x`, not the major
- `tag_format = "v{version}"` — tags are prefixed with `v`

**Promotion to `1.0.0`:** will happen only when the public API is considered stable enough to defend. This requires completion of adoption hardening (concurrency safety, strict contract, test coverage) and is a deliberate decision — not automatic.
