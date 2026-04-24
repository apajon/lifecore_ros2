# Roadmap — Adoption & Hardening

<!-- Companion to ROADMAP.md. Focuses on making lifecore_ros2 adoptable beyond the
     author: positioning, API friction, concurrency safety, strict lifecycle contract,
     test coverage, differentiation, onboarding quality. -->

This roadmap addresses the structural feedback received on the `0.x` baseline:
the core release is shipped, but scaling adoption requires verrouiller positionnement,
ergonomie API, sécurité concurrente, rigueur du contrat lifecycle, et qualité
d'onboarding.

It is organised by the nine concerns raised in review. Each concern declares
**intent**, **in-scope**, **out-of-scope**, and **success signal**. Concrete
actionable items live in `TODO_adoption_hardening.md`.

---

## Guiding principle

> A developer must be able to create a working `LifecycleComponent` in under
> 2 minutes without reading the full documentation.

Every item below is validated against this principle. If a proposed change
increases friction without proportional value, it is rejected.

---

## 1. Positioning — frame the repo as a framework

**Intent.** Stop presenting `lifecore_ros2` as "a ROS 2 project" and state clearly
that it is a minimal composition framework for lifecycle-managed ROS 2 components.

**In-scope.**
- Explicit "Why `lifecore_ros2` exists" section in `README.md`
- Target audience statement: modular robotics, complex embedded systems, runtime
  orchestration of lifecycle components
- One architecture diagram: `Node ↔ Components ↔ Lifecycle`

**Out-of-scope.**
- Marketing copy, logos, branding assets
- Comparison matrix against unrelated frameworks

**Success signal.** A reader who lands on the repo understands in < 30 s what the
library is for and who it targets.

---

## 2. API ergonomics — fight over-abstraction

**Intent.** Verify empirically that the current API does not force a developer
through ten steps to produce a useful component.

**In-scope.**
- Friction audit: count steps required to (a) create a publisher component,
  (b) create a subscriber component, (c) compose them under a node
- Identify verbose hooks or mandatory overrides that could be optional
- Document a canonical "shortest path" example and track it as a regression

**Out-of-scope.**
- Introducing new abstractions to hide complexity (the answer to verbosity is
  removal, not layering)
- Config-driven component creation (deferred — see `TODO.md` post-1.0 backlog)

**Success signal.** The shortest-path publisher example fits on one screen and
does not require the reader to know every `_on_*` hook.

---

## 3. Naming convention — lock it in

**Intent.** Stabilise naming now that `LifecycleComponent` / `LifecycleComponentNode`
have converged. Prevent drift into `Core`, `Manager`, `Handler` synonyms.

**In-scope.**
- Repository-wide naming rules (already partially documented in
  `.github/instructions/naming-conventions.instructions.md`): promote to an
  authoritative doc section
- Explicit rule: no `Abstract` prefix; use `Base` or no prefix
- Explicit rule: behavioural interfaces use `Interface` suffix only if truly needed
- Enforcement: lint or review checklist item

**Out-of-scope.**
- Renaming any currently-exported public symbol
- Retrofitting historical decisions already shipped in `0.x`

**Success signal.** No PR introduces `*Manager`, `*Handler`, `*Core`, or `Abstract*`
classes without being flagged in review.

---

## 4. Ownership & threading — make the concurrency model explicit

**Intent.** Decide and document the threading contract of `LifecycleComponentNode`
and `LifecycleComponent`. Either protect shared state or declare a single-thread
model. No implicit assumptions.

**In-scope.**
- Audit of `add_component`, lifecycle transitions, callback dispatch, and
  component destruction for data races
- Decision record: single-threaded model vs mutex-protected model (likely
  single-threaded per ROS 2 executor, with explicit constraints documented)
- Explicit rule: forbidden concurrent transitions and their enforcement
- Atomic or guarded lifecycle state reads

**Out-of-scope.**
- Introducing a custom executor or threading primitives beyond rclpy
- Supporting arbitrary multi-executor topologies (deferred)

**Success signal.** A reader can answer "can I call `add_component` from a
callback?" by reading one paragraph in the docs.

---

## 5. Strict lifecycle contract

**Intent.** Treat the lifecycle as a contract, not a suggestion. Reject invalid
transitions loudly instead of silently accepting them.

**In-scope.**
- Double `activate`, `deactivate` without prior `activate`, and other invalid
  sequences → raise a typed exception or return a documented failure
- Explicit, actionable log messages at every transition boundary
- State always coherent: no partial transitions leaking visible state

**Out-of-scope.**
- Replacing native ROS 2 lifecycle semantics with a parallel state machine
  (explicit guardrail already in `TODO.md §3`)

**Success signal.** A test suite covers every invalid transition and asserts the
framework rejects it deterministically.

---

## 6. Test coverage — close the critical gap

**Intent.** Raise test coverage from "nominal paths work" to "framework is
trustworthy under stress". This is the single biggest blocker to adoption.

**In-scope.**
- Unit: full lifecycle walk, double activate/deactivate, add/remove component
- Concurrency: multi-thread `add_component`, activation during add, destruction
  during `spin`
- Integration: node with multiple components, inter-component interactions
- Regression: one test per fixed bug going forward

**Out-of-scope.**
- End-to-end system tests requiring a full ROS 2 graph and real hardware
- Performance benchmarks (tracked separately if ever needed)

**Success signal.** CI fails deterministically on any regression in lifecycle
semantics, ownership, or activation gating.

---

## 7. Differentiators — what makes `lifecore_ros2` worth adopting

**Intent.** Identify the three features that move the library from "correct" to
"compelling" for professional teams. Plan them, but do not ship prematurely.

**In-scope (future, gated on 1–6 being solid).**
- Runtime introspection: list components, read lifecycle state, debug helpers
- Dynamic components: clean add/remove at runtime (hot reload)
- Observability: structured logging, lifecycle tracing

**Out-of-scope for now.**
- Any of the above before concurrency (4), strict contract (5), and tests (6)
  are done. Differentiators on a shaky base are liabilities, not assets.

**Success signal.** Each differentiator has a written design note and an explicit
gate referencing prerequisites from sections 4–6.

---

## 8. README — onboarding quality

**Intent.** The README must get a new reader productive fast. Currently it is
insufficient for external adoption.

**In-scope.**
- 30-second quickstart (copy-paste runnable)
- One complete, realistic example
- Architecture diagram (reuse from §1)
- Design rules and guardrails (link, do not duplicate)

**Out-of-scope.**
- Full tutorial content (lives in Sphinx docs under `docs/`)

**Success signal.** A reader unfamiliar with the project can run a working
lifecycle component within five minutes of cloning.

---

## 9. Long-term vision

**Intent.** State the trajectory explicitly so contributors and users can
self-select.

**Trajectory.**
- Stable public API (promote to `1.0.0` only when sections 4, 5, 6 are green)
- Solid docs (Sphinx + README + examples in sync)
- Bulletproof tests (see §6)
- Becomes: (a) a base for modular robots, (b) an internal team framework,
  (c) a recognised ROS 2 package

**Explicit non-goals.**
- Full application framework with service orchestration or task scheduling
  (already excluded in `ROADMAP.md`)
- Domain components, plugin system, or config-driven runtime (deferred)

---

## Sequencing

The nine sections are not independent. Recommended order:

1. **Positioning (§1)** and **README (§8)** — cheap, unlock adoption feedback
2. **Naming lock-in (§3)** — prevents churn in later work
3. **Concurrency contract (§4)** and **strict lifecycle (§5)** — foundational
4. **Test coverage (§6)** — validates §4 and §5
5. **API ergonomics audit (§2)** — performed against a stable, tested base
6. **Differentiators (§7)** — only after 1–6 are green

Promotion to `1.0.0` is gated on §4, §5, §6 being complete and §1, §2, §8 being
materially improved.

---

## Related documents

- `ROADMAP.md` — 0.x release scope and out-of-scope items
- `TODO.md` — release flow and post-1.0 backlog
- `TODO_adoption_hardening.md` — actionable checklist for this roadmap
- `.github/instructions/naming-conventions.instructions.md` — naming rules
