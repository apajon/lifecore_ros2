# TODO — Adoption & Hardening

Actionable checklist for `ROADMAP_adoption_hardening.md`. Each item is small,
reviewable, and traceable to one of the nine concerns in the roadmap.

Rule: no item on this list justifies violating the guardrails in `TODO.md §3`
(no parallel state machine, no vague manager abstraction, stay lifecycle-native).

---

## 1. Positioning

- [x] Add a "Why `lifecore_ros2` exists" section to `README.md` (audience,
      problem framing, non-goals)
- [x] Add one architecture diagram: `Node ↔ Components ↔ Lifecycle` (ASCII or
      Mermaid; keep it under 20 lines)
- [x] Align `pyproject.toml` `project.description` with the canonical
      positioning sentence (already in `ROADMAP.md`) — verify no drift

## 2. API ergonomics — friction audit

- [x] Count steps required to implement a minimal `LifecyclePublisherComponent`
      from scratch; record in an audit note
- [x] Count steps for a minimal `LifecycleSubscriberComponent`
- [x] Count steps to compose two components under a `LifecycleComponentNode`
- [x] For any step that exists only for framework bookkeeping, open an issue
      proposing removal or defaulting
      → Issue #1: consider making `msg_type` optional (Python type-erasure
        limitation; investigation deferred); no other bookkeeping-only step found
- [x] Promote one example as the canonical "shortest path" and snapshot its line
      count as a regression target
      → `examples/minimal_subscriber.py`; component + node definition: 24 lines
      → Audit note: `docs/api_friction_audit.rst`

## 3. Naming — lock-in

- [x] Promote `.github/instructions/naming-conventions.instructions.md` content
      into a user-facing `docs/` section (architecture or contributing)
- [x] Add explicit rule: no `Abstract` prefix; prefer `Base` or no prefix
- [x] Add explicit rule: no `*Manager`, `*Handler`, `*Core` synonyms without
      review justification
- [x] Add a review checklist item in `CONTRIBUTING.md` covering naming

## 4. Ownership & threading

- [x] Audit `LifecycleComponentNode.add_component` for thread safety; document
      current guarantees
      → Thread-safe via `threading.RLock`; documented in `docs/architecture.rst §Concurrency Contract`
- [x] Audit lifecycle transition dispatch for reentrancy from callbacks
      → Documented: hooks are synchronous; reentrant calls raise `ConcurrentTransitionError`
- [x] Audit component destruction relative to active callbacks
      → Documented in §Concurrency Contract; no framework management beyond lifecycle transitions
- [x] Write an Architecture Decision Record: single-threaded model vs
      mutex-protected model (pick one, justify)
      → Decision: single-threaded executor + RLock for registration; see `docs/architecture.rst §ADR`
- [x] Document forbidden concurrent transitions and their enforcement
      → Documented in §Concurrency Contract; enforced by `_in_transition` flag
- [x] Add an assertion or typed exception for forbidden concurrent cases
      → `ConcurrentTransitionError(LifecoreError, RuntimeError)` added; raised by `_begin_transition`
- [x] Add a concurrency section to `docs/architecture.rst`
      → `Concurrency Contract` section added (ADR, thread-safety table, forbidden transitions, reentrancy, destruction)

## 5. Strict lifecycle contract

- [x] Enumerate invalid transition sequences in a single table
      (double activate, deactivate-without-activate, cleanup-while-active, etc.)
      → `docs/architecture.rst §Strict direct-call contract`
- [x] For each invalid case, decide: rely on native rclpy rejection, or raise a
      typed `LifecoreError` subclass
      → Node path: native `rclpy` rejection with framework logging; direct component path:
        `InvalidLifecycleTransitionError`
- [x] Ensure every rejection path emits an actionable log line (component name,
      current state, attempted transition)
      → Direct and node-driven rejection logging added in core lifecycle boundaries
- [x] Guarantee state coherence on failure: no half-configured components left
      visible to the node
      → Failed node-driven `configure` now rolls back component resources before returning

## 6. Test coverage

### Unit
- [ ] Full lifecycle walk (configure → activate → deactivate → cleanup → shutdown)
- [ ] Double `activate` (expect rejection or idempotence — per §5 decision)
- [ ] `deactivate` without prior `activate`
- [ ] `add_component` before and after first transition (registration closed)
- [ ] Remove component (if supported) during each lifecycle state

### Concurrency
- [ ] Multi-thread `add_component` (per §4 decision: either proves safety, or
      proves the documented single-thread rule by failing loudly)
- [ ] Transition triggered during `add_component`
- [ ] Component destruction during `spin`

### Integration
- [ ] Node with three heterogeneous components transitioning together
- [ ] Inter-component interaction through pub/sub
- [ ] Failure in one component's `_on_configure` does not leave siblings in an
      inconsistent state

### Regression discipline
- [ ] Rule: any bug fix from now on ships with a regression test in the same PR

## 7. Differentiators — design notes only, no code yet

- [ ] Write a design note for runtime introspection (read-only API: list
      components, lifecycle state, attached resources)
- [ ] Write a design note for dynamic components (add/remove at runtime) —
      explicitly gated on §4 concurrency decision being done
- [ ] Write a design note for observability (structured logging, lifecycle
      tracing) — explicitly gated on §5 strict contract being done
- [ ] Do **not** start implementation until §4, §5, §6 are green

## 8. README

- [ ] Add a 30-second quickstart (clone → install → run one example)
- [ ] Link to one complete example already in `examples/` instead of duplicating
- [ ] Embed the architecture diagram from §1
- [ ] Link to design rules rather than restating them
- [ ] Verify every command in the README works from a clean clone

## 9. Long-term vision

- [ ] Document the `1.0.0` promotion gate explicitly: §4, §5, §6 complete
- [ ] Restate non-goals in `ROADMAP.md` if any new feedback contradicts them
- [ ] Keep this file and `ROADMAP_adoption_hardening.md` in sync as items ship

---

## Sequencing reminder

Follow the order in `ROADMAP_adoption_hardening.md §Sequencing`:
1 & 8 → 3 → 4 & 5 → 6 → 2 → 7.

Do not pull items from §7 forward without the gates being green.
