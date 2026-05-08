# Roadmap

<!-- Canonical positioning sentence — keep in sync with pyproject.toml project.description. -->
lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy — no hidden state machine.

---

## Current status — 0.4.0 + Sprint 8

The first public release is shipped. The core library provides:

- `LifecycleComponentNode` and `LifecycleComponent` base classes
- `TopicComponent`, `LifecyclePublisherComponent`, `LifecycleSubscriberComponent` implementations
- `when_active` decorator for activation gating
- `get_or_create_callback_group` helper for node-owned, idempotent callback group creation
- `_is_active` protected by `_active_lock` — concurrency contract is GIL-independent
- In-flight callback policy documented ("drop at next gate")
- Concurrency safety via RLock and reentrant-call detection
- Strict lifecycle contract with error handling and rollback
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

Current status: ✓ all adoption items complete (v0.4.0). The core library is usable and documented for professional evaluation, while API stability remains experimental until `1.0.0`.

---

## Strategic direction

The project is positioned as an **inside-the-node** discipline layer: below launch files, lifecycle managers, and system orchestrators; above raw `rclpy` lifecycle primitives.

It is not a launcher, not a Nav2-style lifecycle manager, and not a replacement for ROS 2 lifecycle semantics. The message to validate with users is:

> Build predictable ROS 2 nodes.

**See [Strategic Cap](docs/planning/strategy.rst)** for the working product thesis, boundaries, adoption sequence, and publication gate.

---

## Next planning window

The recommended sequence after the current foundation is tracked by sprint
number. Sprint numbers encode priority order:

1. **Lifecycle comparison example** — implement the same sensor watchdog node as plain ROS 2, classic ROS 2 lifecycle, and `lifecore_ros2`.
2. **Internal component cascade** — move deterministic intra-node ordering directly after the comparison because it is the main differentiator.
3. **Runtime hardening** — callback gating, cleanup ownership, concurrency, and observability before recovery-facing APIs.
4. **Health and watchdog** — expose health before adding watchdog behavior.
5. **Advanced surfaces** — lifecycle policies, parameters, factory/registry, then tooling/generation.

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
- Config and specs (application-level configuration)
- Factory and registry (dynamic component loading)
- ~~Callback group management (per-component groups, concurrency utilities)~~ **Shipped Sprint 8**
- Additional components (`ActionComponent`, parameter components)
- Binding layer (if component hierarchy becomes overloaded)
- Release status metadata (`Development Status :: 4 - Beta` promotion gate)
- README badges (once on PyPI)

Each item includes a rationale for deferral and placement notes for future implementation.

---

## Companion examples repository

**See [Examples Repository Plan](docs/planning/examples_repo.rst)** for the full planning.

**Status**: repository exists and should host applied, domain-flavored, or multi-node examples that fall outside the core library's scope. The strategic lifecycle comparison example should be proven in the core repo first, then extended in the companion repo only if it needs applied scenarios or extra dependencies.

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
