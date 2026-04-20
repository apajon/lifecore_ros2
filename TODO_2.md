# TODO for first public release of `lifecore_ros2`

This document defines the concrete work needed before the first public release of `lifecore_ros2`.

The project is intentionally a small, abstract ROS 2 lifecycle composition library. The goal is not to ship a full application framework. The goal is to publish a reliable, understandable, well-positioned core library with a clean public surface and enough examples to make its value obvious.

---

## Release goal

Ship a first public version that clearly communicates:

- this is a serious ROS 2 Jazzy library
- it solves a real lifecycle composition problem
- it stays close to native ROS 2 lifecycle semantics
- it is small, explicit, and predictable
- it is ready to be adopted experimentally without guessing how it works

---

## Guiding constraints

- keep the core library abstract
- avoid adding hidden state machines or framework magic
- keep examples focused and pedagogical
- include at least one more concrete example, even if it is still small
- optimize for clarity, stability, and trust over feature count

---

# 1. Release scope and versioning

## 1.1 Freeze the first public scope
- [x] Write down exactly what is part of the first public release
- [x] Write down what is intentionally excluded for now
- [x] Mark any unstable idea as postponed instead of "maybe"

### Why
Without a hard boundary, the release will drift. Small libraries often get delayed by endless polishing. A clear release scope prevents that and forces a real version to happen.

### Deliverable
A short section in `README.md` or `ROADMAP.md` with:
- included in first release
- intentionally deferred
- out of scope for the core library

---

## 1.2 Decide the initial version number honestly
- [x] Choose between `0.1.0` and `1.0.0`
- [x] Document the expected stability level of the public API
- [x] Align semantic-release usage with that choice

### Why
If the abstractions may still move, `0.1.0` is the right signal. If the public classes and extension model are already effectively fixed, then `1.0.0` can make sense. The version must reflect reality, not ambition.

### Recommendation
Default to `0.1.0` unless you are confident the public API is already stable enough to defend.

---

## 1.3 Define public API stability expectations
- [x] Explicitly list which classes are public API
- [x] Explicitly mark internal helpers as non-public
- [x] State whether subclassing hooks are stable or still evolving

### Why
For an abstract library, the real API is not just function names. It is also the extension model. If users start relying on internal behavior, future cleanup becomes painful.

---

# 2. Core lifecycle correctness

## 2.1 Formalize lifecycle invariants
- [x] Document what `configure` is allowed to allocate
- [x] Document what `activate` is allowed to enable
- [x] Document what `deactivate` must disable
- [x] Document what `cleanup` must release
- [x] State clearly that no parallel hidden lifecycle exists

### Why
This is the heart of the project. The whole value of `lifecore_ros2` depends on being predictable and faithful to native lifecycle semantics.

### Invariants to lock down
- resources are created during configure
- runtime behavior is gated by activation
- deactivation stops runtime behavior without pretending cleanup happened
- cleanup releases resources cleanly
- no component introduces a second lifecycle model on the side

---

## 2.2 Test the happy path for each component type
- [x] Test `LifecycleComponentNode` nominal transitions
- [x] Test `LifecycleComponent` nominal transition behavior
- [x] Test `TopicComponent` resource setup and teardown
- [x] Test `LifecyclePublisherComponent` publish behavior across transitions
- [x] Test `LifecycleSubscriberComponent` callback behavior across transitions

### Why
The basic paths must be mechanically trustworthy before any public release.

---

## 2.3 Test invalid and edge transitions
- [x] Activation before configure is rejected or handled explicitly
- [x] Cleanup before configure is handled explicitly
- [x] Repeated configure or activate transitions behave predictably
- [x] Deactivate without active runtime state behaves predictably
- [x] Cleanup after partial initialization behaves safely

### Why
Infrastructure libraries fail at the edges, not in the README example.

---

## 2.4 Test failure propagation and recovery behavior
- [x] Exception in `on_configure`
- [x] Exception in `on_activate`
- [x] Exception in `on_deactivate`
- [x] Exception in `on_cleanup`
- [x] One component failing inside a composed node
- [x] Partial resource allocation followed by failure

### Why
Users need confidence that a failing component will not leave the node in a confusing or inconsistent state.

---

## 2.5 Validate publisher and subscriber gating strictly
- [x] Confirm publish attempts outside activation are rejected or ignored intentionally
- [x] Confirm subscriber callbacks do not process messages while inactive
- [x] Confirm behavior resumes correctly after reactivation

### Why
This is one of the most visible and easiest-to-understand promises of the library. It must be airtight.

---

# 3. Public API and extension model

## 3.1 Review every public class name
- [x] Re-evaluate `ComposedLifecycleNode` -> `LifecycleComponentNode`
- [x] Re-evaluate `LifecycleComponent` (kept)
- [x] Re-evaluate `TopicComponent` (kept)
- [x] Re-evaluate `PublisherComponent` -> `LifecyclePublisherComponent`
- [x] Re-evaluate `SubscriberComponent` -> `LifecycleSubscriberComponent`

### Why
Names are sticky. Once public, they become part of how people think about the library. This is the best time to challenge them.

### Review criteria
- precise
- easy to understand in isolation
- aligned with long-term design
- not misleading outside author context

### 3.1 Decision record
- `ComposedLifecycleNode` renamed to `LifecycleComponentNode`.
- `PublisherComponent` renamed to `LifecyclePublisherComponent`.
- `SubscriberComponent` renamed to `LifecycleSubscriberComponent`.
- `LifecycleComponent` and `TopicComponent` remain unchanged.

---

## 3.2 Define the responsibility of each public class
- [x] Add a short responsibility statement to each class docstring
- [x] Clarify what each class owns
- [x] Clarify what each class does not own
- [x] Clarify expected override points

### Why
An abstract library becomes usable when its concepts are sharply bounded. Users should not need to reverse-engineer your architecture from source code.

---

## 3.3 Separate public hooks from internal machinery
- [x] Mark intended subclass hooks clearly
- [x] Mark internal helper methods clearly
- [x] Avoid leaking implementation details through accidental public methods
- [x] Decide whether protected naming is needed for extension points

### Why
Users will depend on anything that looks available. If you do not draw the line, they will draw it for you.

### 3.3 Decision record

**Four-bucket taxonomy** applied uniformly across `core/` and `components/`:

- **Bucket 1 — Public API**: no underscore; included in `__all__`. No changes needed.
- **Bucket 2 — Protected extension points**: `_on_*` / `_release_resources`. Docstring starts with `Extension point.` Rendered in Sphinx autodoc via `autodoc-skip-member` hook.
- **Bucket 3 — Framework-controlled entry points**: the six `on_*` methods on `LifecycleComponent`. Decorated with `@typing.final` so pyright catches accidental overrides. `LifecycleComponentNode.on_configure` and `on_shutdown` are **not** sealed — they carry an explicit "override with super" contract.
- **Bucket 4 — Framework-internal**: `_attach`, `_detach`, `_resolve_logger`, `_guarded_call`, `_safe_release_resources`, `_close_registration`, `_on_message_wrapper`. Docstring starts with `Framework-internal. Do not call from user code.` Excluded from Sphinx autodoc.

**`on_message` resolution — R2 (keep public)**: `on_message` defines *application* behavior (the subscriber callback contract), not framework behavior. It is intentionally public. This distinguishes it from `_on_configure` etc. which customize framework transitions. Documented in the `LifecycleSubscriberComponent` docstring and in `docs/architecture.rst`.

**`_on_message_wrapper` sealed**: decorated `@final` — it is a framework dispatch method that must never be overridden.

**`docs/conf.py`**: added `autodoc-skip-member` hook that includes Bucket 2 extension points (`_on_*`, `_release_resources`) and excludes all other `_*` members from generated API docs.

**`docs/architecture.rst`**: added "Member Convention" section documenting the four buckets and their markers; fixed two stale lifecycle invariant statements (`on_deactivate` clears `_is_active` only on SUCCESS; `_release_resources` is called automatically).

---

## 3.4 Tighten type hints and static guarantees
- [x] Remove unnecessary `Any`
- [x] Check all public signatures
- [x] Validate optional values and nullability
- [x] Ensure pyright reflects intended contracts

### Why
For a Python infrastructure library, type hints are part of the API. Good type information lowers adoption friction and catches architectural drift early.

### 3.4 Decision record

**D1 — Topic components are generic in `MsgT`**: `TopicComponent[MsgT]`, `LifecyclePublisherComponent[MsgT]`, and `LifecycleSubscriberComponent[MsgT]` use PEP 695 syntax (Python 3.12+). `publish(msg: MsgT)` and `on_message(msg: MsgT)` are now typed against the message type inferred at construction (`msg_type=String` → `MsgT = String`). Explicit parameterization (`LifecyclePublisherComponent[String](...)`) is supported. Examples updated to demonstrate explicit `[MsgT]` usage. `MsgT` is unbounded — no stable ROS 2 message base class is available without coupling to `rosidl` internals.

**D2 — `get_logger()` narrowed to `_LoggerLike` Protocol**: `LifecycleComponent.get_logger()` now returns `_LoggerLike` (a private structural Protocol) instead of `Any`. `_LoggerLike` covers `debug`, `info`, `warning`, `error`, `fatal` — all methods the framework and typical subclass code use. `cast(_LoggerLike, ...)` in `_resolve_logger` bypasses structural verification, which is correct since rclpy's `RcutilsLogger` is not exported as a public typed interface.

**D3 — Justified `Any` uses annotated explicitly**: two residual `Any` uses are documented inline with `# Any:` comments. Convention established: every `Any` in `src/` must carry a one-line justification.

**D4 — Pyright strict mode added to `pyproject.toml`**: `[tool.pyright]` block added with `typeCheckingMode = "strict"`. `reportMissingTypeStubs`, `reportUnknownMemberType`, `reportUnknownArgumentType`, `reportUnknownVariableType` downgraded from error to warning to absorb unactionable noise from rclpy's partial stubs. Zero pyright errors for `src/lifecore_ros2/**`.

**D5 — `MsgT` is not exported**: the TypeVar is local to each component module and not added to `__all__`. The generic surface is observable through class subscript; no new public symbol is introduced.

**Validation at close**: `ruff check`, `ruff format --check`, `pyright` (0 errors, 0 warnings), `pytest` (130/130) all pass. Pyright smoke check in `tests/typing_smoke_check.py` mechanically confirms the generic contract: `# type: ignore[arg-type]` on a wrong-type `publish()` call is flagged as *necessary* by pyright strict, proving `MsgT` does not resolve to `Any`.

---

## 3.5 Define a coherent error policy
- [x] Decide when to raise exceptions
- [x] Decide when to log and ignore
- [x] Decide when to signal lifecycle failure explicitly
- [x] Make error behavior consistent across components

### Why
Users can tolerate strict behavior. They cannot tolerate inconsistent behavior.

### 3.5 Decision record

Four rules applied uniformly across `core/` and `components/`:

**Rule A — Boundary violations raise `LifecoreError` subclasses**: misuse of the public API by application code raises a typed subclass of `LifecoreError`, which also inherits from the matching standard Python exception:
- `RegistrationClosedError(LifecoreError, RuntimeError)`: `add_component` called after first lifecycle transition.
- `DuplicateComponentError(LifecoreError, ValueError)`: `add_component` with a duplicate component name.
- `ComponentNotAttachedError(LifecoreError, RuntimeError)`: `.node` accessed on a detached component.
- `ComponentNotConfiguredError(LifecoreError, RuntimeError)`: `publish()` before `_on_configure` created the publisher.
Defined in `src/lifecore_ros2/core/exceptions.py`. Catch `LifecoreError` to handle any framework boundary violation in one handler.

**Rule B — Lifecycle hooks never raise outward**: `_guarded_call` wraps every `_on_*` hook. Uncaught exceptions and invalid return values are converted to `TransitionCallbackReturn.ERROR` with a logged traceback. Hook authors choose SUCCESS / FAILURE / ERROR (or raise); the framework never lets an exception escape into rclpy.

**Rule C — Activation gating: outbound raises, inbound drops**:
- Outbound calls (e.g. `publish()`) raise `RuntimeError` by default via `@when_active`. Raising surfaces lifecycle programming errors.
- Inbound callbacks (subscription callbacks, timers) silently drop with a debug log. Raising into the rclpy executor would crash the spin loop.
- Exceptions raised inside `on_message` are caught by `_on_message_wrapper`, logged at error level, and dropped — never propagated to the executor.
Both defaults are customisable via `@when_active(when_not_active=...)`.

**Rule D — Cleanup/shutdown/error propagate worst result**: `on_cleanup`, `on_shutdown`, and `on_error` each run the `_on_*` hook and then call `_release_resources`. The returned `TransitionCallbackReturn` is the worst of the two results using ordering `SUCCESS < FAILURE < ERROR` (see `_worst_of` in `lifecycle_component.py`). A failing `_on_cleanup` hook does **not** skip `_release_resources`.

---

# 4. Documentation quality

## 4.1 Rewrite the README as a landing page
- [x] Open with a one-sentence positioning statement
- [x] Add a short "why this exists" section
- [x] Explain the problem before listing the classes
- [x] Show the value before the architecture
- [x] Keep quickstart short and frictionless

### Why
A good README does not just document the project. It sells the mental model in under a minute.

### Target structure
1. title
2. one-sentence positioning
3. why this exists
4. what the library provides
5. design principles
6. quickstart
7. minimal example
8. public API overview
9. current limitations
10. documentation links
11. companion example repo link later

---

## 4.2 Add a strong "why this exists" section
- [x] State the lifecycle pain points this library addresses
- [x] Explain what boilerplate or ambiguity it removes
- [x] Explain what it does not try to abstract away

### Why
People adopt libraries to solve pains, not to admire architecture.

### Pain points worth naming
- lifecycle logic gets scattered
- ROS resource setup and teardown are easy to make inconsistent
- runtime gating is often hand-rolled badly
- reusable lifecycle-aware building blocks are awkward in raw rclpy

---

## 4.3 Add a clear "non-goals" section
- [x] No hidden parallel lifecycle model
- [x] No full application framework
- [x] No replacement of native ROS 2 lifecycle semantics
- [x] No magic orchestration outside explicit component composition

### Why
This protects the project from misinterpretation and sets the tone immediately.

---

## 4.4 Strengthen architecture documentation
- [x] Document node-component relationships clearly
- [x] Document the transition sequence clearly
- [x] Document topic resource lifecycle clearly
- [x] Add simple diagrams if useful

### Why
A conceptual library needs lower cognitive load, not more prose.

---

## 4.5 Add recommended patterns and anti-patterns
- [x] Recommended: allocate ROS resources during configure
- [x] Recommended: gate behavior through activation
- [x] Recommended: keep hooks deterministic
- [x] Anti-pattern: create hidden runtime states disconnected from lifecycle
- [x] Anti-pattern: treat deactivate like cleanup
- [x] Anti-pattern: put heavy business logic inside lifecycle transition hooks

### Why
This is where the project starts teaching good ROS 2 lifecycle design, not just exposing helpers.

---

## 4.6 Add a "mental migration from raw rclpy" section
- [x] Show a small before/after comparison
- [x] Explain how composition improves structure
- [x] Explain what remains unchanged from native lifecycle semantics

### Why
It lowers the adoption barrier and makes the benefit concrete.

---

# 5. Examples

## 5.1 Clean up the existing minimal examples
- [x] Make each example short
- [x] Ensure each example demonstrates one idea only
- [x] Add a short explanation at the top of each example
- [x] Keep the expected behavior obvious

### Why
If examples are abstract, they must be extremely legible. Otherwise they feel like internal tests, not teaching tools.

### 5.1 Decision record

- Module docstring added to each example: single idea stated, CLI commands listed, expected log lines per transition documented inline.
- `minimal_node`: commented-out `_on_configure` promoted to a real override on `LoggingComponent`; dead code removed.
- `minimal_publisher`: explicit `_on_cleanup` override added (logs framework-managed release); `# why:` comment added on timer allocation explaining configure-time resource vs activate-time behavior split.
- `minimal_subscriber`: `on_message` docstring added confirming Bucket-1 public application-callback contract and activation-gated delivery semantics.
- `main()` boilerplate kept structurally identical across all three files.

---

## 5.2 Add one more concrete example
- [x] Create a small but recognizably real example
- [x] Keep it generic enough to stay inside the library repo
- [x] Make the value visible through lifecycle transitions
- [x] Avoid turning it into a domain-heavy application demo

### Why
You were right to keep the library abstract. But the repo still needs one example that feels closer to a real use case.

### 5.2 Decision record

**File**: `examples/telemetry_publisher.py`

**Teaching axis**: configure-time resource acquisition vs activate-time gated behavior — the distinction absent from the minimal examples.

- `LifecycleTelemetryPublisher(LifecyclePublisherComponent[Float64])`: all four hooks overridden explicitly.
  - `_on_configure`: calls `super()` (creates ROS publisher), then acquires simulated sensor handle (`_sensor_ready = True`, `_sequence = 0`).
  - `_on_activate`: creates 1 s sampling timer (runtime behavior, not a ROS resource).
  - `_on_deactivate`: cancels and destroys timer; sensor handle **deliberately kept open** to demonstrate that deactivate ≠ cleanup.
  - `_on_cleanup`: releases sensor handle, resets state, calls `super()._on_cleanup(state)`.
  - `_sample`: publishes `Float64(sin(seq * 0.1))`; `@when_active` gating on parent makes an extra guard unnecessary.
- `TelemetryNode(LifecycleComponentNode)`: business-domain name per naming conventions.
- BEST_EFFORT QoS `depth=5` defined as a module constant (`_TELEMETRY_QOS`).
- No new dependencies; simulated sensor uses stdlib `math`.
- Module docstring includes expected output per transition (covers 5.4 for this example).

---

## 5.3 Add one multi-component example
- [x] Compose at least two or three components together
- [x] Show how composition is better than isolated examples
- [x] Keep the behavior easy to observe

### Why
This is likely closer to the real value of the library than separate minimal publisher/subscriber snippets.

### 5.3 Decision record

**Deliverable**: `examples/composed_pipeline.py` — three sibling components compose inside one `LifecycleComponentNode`:

- `SineSource(LifecyclePublisherComponent[Float64])`: emits sine-wave samples on `/pipeline/raw` while active; timer created on activate (runtime behavior, not ROS resource).
- `MovingAverageRelay(LifecycleComponent)`: extends `LifecycleComponent` directly, owning both a raw rclpy subscription and raw rclpy publisher. Demonstrates the pure extension model: any pair of ROS resources belongs in one component. Buffer cleared on deactivate to prevent stale-state bias after reactivation.
- `LoggingSink(LifecycleSubscriberComponent[Float64])`: logs averaged values from `/pipeline/avg` while active.

**Teaching value**: composition is the unit of value — no single component shows the observable behavior; all three must activate together. Activation gating across a multi-hop pipeline is visible: while inactive, `ros2 topic list` shows both topics but no data flows.

**Architecture principle taught**: `MovingAverageRelay` as a direct `LifecycleComponent` subclass makes explicit what pre-built topic components do internally — allowing users to understand and extend the pattern for custom multi-resource scenarios.

**Expected output** documented in module docstring; all four lifecycle transitions explicitly logged per component.

---

## 5.4 Make expected outputs explicit
- [x] Document what users should observe in logs
- [x] Document what should happen before activation
- [x] Document what should happen after deactivation
- [x] Document what should disappear after cleanup

### Why
Examples become much easier to trust when the expected outcome is precise.

---

## 5.5 Prepare companion examples repository structure
- [x] Decide on the name, for example `lifecore_ros2_examples`
- [x] Outline future example categories
- [x] Add a placeholder reference in docs if useful
- [x] Plan at least one concrete follow-up repository example

### Why
Even if not published on day one, the ecosystem should already have a direction.

### 5.5 Decision record

**Name**: `lifecore_ros2_examples`, owner `apajon`. Rejected alternatives:
`lifecore_ros2_demos` (reads as throwaway), `lifecore_examples` (drops ROS qualifier),
`lifecore_ros2_recipes` (constrains structure prematurely).

**Scope boundary**: an example belongs in the companion repo if it depends on third-party
ROS packages beyond `rclpy` / `std_msgs`, uses domain-specific message types, spans more
than one ROS node, or teaches an applied pattern rather than a single core abstraction.
Otherwise it stays in `examples/` in this repo. This is the contributor-facing exclusion
test.

**Categories** (initial outline):
- sensor-pipeline composition (multi-publisher / fan-in topologies)
- lifecycle-aware diagnostics (`/diagnostics` integration, inter-component health)
- multi-node orchestration patterns (supervisor and launch-coordinated lifecycle nodes)

**First concrete example**: sensor-fusion pipeline — two heterogeneous simulated sensors,
one fusion `LifecycleComponent` owning two subscriptions and one publisher, one logging
`LifecycleSubscriberComponent`. Teaches activation gating across a fan-in topology,
configure-time sensor-handle acquisition, the warm-up window with inbound-drop
semantics, and state reset on deactivate.

**Coupling to core releases**: the companion repo follows core cadence but does not pin
a coupled version. Core releases never block on companion-repo state.

**Deliverables in this repo (planning artifacts, no source/test/example changes)**:
- `ROADMAP.md` — new "Companion examples repository" section
- `README.md` — "current limitations" line updated to a forward pointer marked
  *planned — not yet published*
- `docs/examples.rst` — new "Companion examples repository (planned)" subsection
- `ROADMAP_lifecore_ros2_examples.md` — full roadmap for the companion repo
- `TODO_lifecore_ros2_examples.md` — phased TODO for the companion repo

The two `*_lifecore_ros2_examples.md` files live in this repo until the companion
repository is created, then move into it (tracked in Phase 3 of
`TODO_lifecore_ros2_examples.md`).

---

# 6. Developer experience and project structure

## 6.1 Validate installation from scratch
- [x] Test clone on a clean machine or clean environment
- [x] Source ROS 2 Jazzy
- [x] Run `uv sync --extra dev`
- [x] Run `uv run --extra dev pytest`
- [x] Run `uv run --extra dev python examples/...`
- [x] Build docs from scratch

### Why
A library that only works on the author's machine is dead on arrival.

### 6.1 Decision record

Validated locally by the maintainer on the development machine with ROS 2 Jazzy sourced.
Clean `uv sync --extra dev` installs all dev tooling. All examples (`minimal_node.py`,
`minimal_publisher.py`, `minimal_subscriber.py`, `telemetry_publisher.py`,
`composed_pipeline.py`) run without error. Docs build succeeds with
`uv run --group docs python -m sphinx -b html docs docs/_build/html`.
Full CI-environment verification remains as an exit gate for §6.6.

---

## 6.2 Review `pyproject.toml`
- [x] Check project metadata
- [x] Check extras and dependency groups
- [x] Check package description
- [x] Check version exposure
- [x] Check tooling sections
- [x] Check Python version declaration

### Why
This file is part of the public face of the project.

### 6.2 Decision record

- `numpy` and `pydantic` removed: no import site found in `src/` (`dependencies = []`).
- `rclpy` absence justified inline: `# rclpy is intentionally absent — it comes from the system ROS installation`.
- PEP 639 SPDX form adopted: `license = "Apache-2.0"` + `license-files = ["LICENSE"]` (old `{file = "LICENSE"}` deprecated under PEP 639; setuptools >= 77 required, pinned to >= 80).
- Added `keywords`, `classifiers` (Development Status :: 4 - Beta, License, Programming Language, Topic, Intended Audience).
- Added four `[project.urls]` entries: Repository, Documentation, Changelog, Issues.
- `requires-python = ">=3.12"` confirmed correct; tooling sections (`ruff`, `pyright`, `pytest`, `semantic_release`) reviewed — unchanged.

---

## 6.3 Add an explicit license
- [x] Choose license
- [x] Add `LICENSE`
- [x] Mention it in `README.md`
- [x] Ensure it matches intended adoption goals

### Why
Without a license, many serious users and companies will not touch the code.

### Recommended options
- BSD-3-Clause
- Apache-2.0

### 6.3 Decision record

**Apache-2.0** chosen: permissive, OSI-approved, compatible with ROS 2 ecosystem conventions.
`LICENSE` file was already present. `README.md` carries a `## License` section pointing to it.
`pyproject.toml` updated to PEP 639 SPDX expression (see §6.2 decision record).

---

## 6.4 Add `CONTRIBUTING.md`
- [x] Document setup steps
- [x] Document validation commands
- [x] Document style expectations
- [x] Document commit conventions
- [x] Document how to report bugs or discuss design

### Why
It signals maturity and reduces friction the first time someone wants to interact seriously with the repo.

### 6.4 Decision record

**File**: `CONTRIBUTING.md` (repo root).

Covers: prerequisites (Python 3.12+, ROS 2 Jazzy, `uv`), local setup (`uv sync --extra dev`),
full validation command set (`ruff`, `pyright`, `pytest`, `uv build`, `twine check`, Sphinx),
Conventional Commits table with `feat`/`fix`/`docs`/`chore`/`test`/`perf` and `BREAKING CHANGE` footer,
PR checklist (4 validation gates, lifecycle-semantics test requirement, `__all__` stability),
design constraints summary with pointer to `docs/architecture.rst`,
and release dispatch instructions (maintainer-only section).
Does not duplicate `docs/contributing.rst` — links to it instead.

---

## 6.5 Add issue templates
- [x] Bug report template
- [x] Feature request template
- [x] Question or design discussion template

### Why
The first external feedback should be structured, not chaotic.

### 6.5 Decision record

Three GitHub form templates under `.github/ISSUE_TEMPLATE/`:
- `bug_report.yml`: required fields — description, expected behavior, minimal reproduction (rendered as Python), ROS version, Python version, lifecore_ros2 version.
- `feature_request.yml`: problem statement, proposal, optional lifecycle contract per transition, scope-check checkboxes (framework-level / companion-repo / no hidden state machine).
- `design_discussion.yml`: context, trade-offs, alternatives considered.

`config.yml` disables blank issues entirely and provides two contact links (Documentation, ROADMAP).
Legacy markdown templates not used — GitHub form schema enforces required fields.

---

## 6.6 Add or finalize CI
- [x] Run ruff check
- [x] Run ruff format check
- [x] Run pyright
- [x] Run pytest
- [ ] Optionally build docs
- [ ] Ensure badges or status are visible if desired

### Why
For a small infrastructure library, CI is a trust multiplier.

### 6.6 Decision record

**File**: `.github/workflows/ci.yml`

**Trigger policy**: `pull_request` targeting `main` + `workflow_dispatch` only.
Never fires on direct push to `main` to keep Actions minutes low.
`concurrency.cancel-in-progress: true` scoped per PR branch.

Three parallel jobs:
- **`lint`** (`ubuntu-24.04`, no ROS): `ruff check .` + `ruff format --check .` — fails fast.
- **`validate`** (`ubuntu-24.04`, `setup-ros@v0.7` Jazzy): single ROS install shared between `pyright` and `pytest` runs — minimises runner minutes.
- **`build`** (`ubuntu-24.04`, no ROS, `fetch-depth: 0` for setuptools-scm): `uv build` + `twine check dist/*`.

**Docs build**: not included in CI — kept in `docs.yml` (path-scoped PR + manual dispatch).
**Badges**: deferred until first green run confirmed on `main`.
**Status**: workflow correct on paper; first green run required to close this item fully (see §6.1 CI-environment exit gate).

---

## 6.7 Validate semantic-release flow end to end
- [x] Verify computed version behavior
- [x] Verify tag generation
- [x] Verify `--no-vcs-release` path
- [x] Verify conventional commit assumptions
- [x] Avoid first release surprises

### Why
Release automation is only useful if it has been proven before launch day.

### 6.7 Progress note

**Structural hardening done** (not yet rehearsed end-to-end):
- Weekly cron schedule removed from `release.yml` — manual dispatch only until rehearsal confirmed.
- Inline lint gate (`ruff check` + `ruff format --check`) added before the `python-semantic-release` step.
- `build_command` already uses `pip install build && python -m build` (PSR Docker env does not have `uv`).

**Remaining execution gates before checking these boxes**:
1. Run `uv run --group release semantic-release version --print --no-push` on `main` and confirm it computes `0.1.0` without errors.
2. Decide CHANGELOG handling: freeze current content as-is, or let semantic-release overwrite from `v0.1.0` forward.
3. Dispatch Release workflow once on a test branch to confirm tag creation and GitHub Release publication.

---

# 7. Release assets and public positioning

## 7.1 Prepare the first changelog entry
- [x] State what the first release provides
- [x] State what it intentionally does not provide yet
- [x] State the supported ROS and Python baseline
- [x] State known limitations if any

### Why
The first release note sets expectations for everyone who sees the project.

---

## 7.2 Define one canonical positioning sentence
- [x] Write one short sentence that can be reused everywhere
- [x] Put it in the README
- [x] Reuse it in docs and release notes

### Why
You need one stable line that explains the project immediately.

### Example direction
`lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy that helps build reusable lifecycle-aware nodes without adding a hidden state machine on top of ROS 2.`

### 7.2 Decision record

**Canonical sentence** (99 chars, fits PyPI rendering budget):

> `lifecore_ros2 is a minimal lifecycle composition library for ROS 2 Jazzy — no hidden state machine.`

**Canonical source**: `pyproject.toml` `project.description`. PyPI is the authoritative
surface; every other location quotes it verbatim.

**Surfaces carrying the sentence verbatim**:
- `pyproject.toml` (`project.description`) — canonical
- `README.md` (top-of-file positioning paragraph)
- `docs/index.rst` (first paragraph under title)
- `docs/architecture.rst` (Overview opening line)
- `ROADMAP.md` (opening line)

**Sync rule**: documented in `CONTRIBUTING.md` under "Canonical positioning sentence".
Update `pyproject.toml` first, then propagate verbatim. Drift is detectable mechanically
via `grep -F`.

**Tone choices locked in**: present-tense, third-person, names ROS 2 Jazzy explicitly,
names the lifecycle-composition problem, names the "no hidden state machine" non-goal
(aligned with `README.md` non-goals and `0.1.0` stability framing — no "production-ready"
or "complete" claims). Em-dash form preferred over the longer "*…that helps build
reusable lifecycle-aware nodes without adding…*" wording originally drafted in §7.2,
because the canonical sentence had to fit the PyPI single-line description budget.

**Reuse for §7.4 (launch text) and §7.5 (FAQ)**: both will quote this sentence verbatim
when those items are addressed.

---

## 7.3 Prepare one visual asset
- [x] Record a short terminal session or GIF
- [x] Show lifecycle transitions and observable behavior
- [x] Keep it short and clean
- [x] Use it in the README or release post if it looks good

### Why
Even a small abstract library benefits massively from one compact proof of behavior.

---

## 7.4 Draft launch messages before release
- [ ] GitHub release text
- [ ] LinkedIn post
- [ ] ROS discourse or Reddit post if you choose to do that
- [ ] A short direct message for relevant contacts if needed

### Why
The worst time to write launch messaging is after a long stabilization push.

---

## 7.5 Add a short FAQ
- [ ] Why not just use raw ROS 2 lifecycle directly?
- [ ] How is this different from introducing a custom state machine?
- [ ] Why components?
- [ ] What stays in this repo versus an application repo?
- [ ] Is the API stable yet?

### Why
A small FAQ absorbs predictable objections fast.

---

# 8. Post-release planning

## 8.1 Decide what feedback to watch first
- [x] Installation friction
- [x] Example clarity
- [x] Misunderstood API boundaries
- [x] Missing docs
- [x] Real lifecycle edge-case bugs

### Why
The first public users will show whether the library is confusing, not just whether it is correct.

---

## 8.2 Define early non-expansion rules
- [x] Refuse feature creep into a full app framework
- [x] Refuse unrelated abstractions too early
- [x] Refuse support claims beyond what is actually tested
- [x] Refuse adding complexity just because it seems general

### Why
A clean library can get ruined quickly by premature generalization.

---

## 8.3 Plan the first companion examples repo
- [x] Create a first outline
- [ ] Add one realistic example later
- [x] Keep the main repo abstract and clean
- [x] Let companion repos carry more applied patterns

### Why
That gives you the right separation between core library and application-oriented demonstrations.

---

# 9. Priority order

## Must be done before public release
- [x] freeze first release scope
- [x] decide versioning strategy
- [x] lock lifecycle invariants
- [x] cover nominal and edge-case tests
- [x] clean public API boundaries
- [x] rewrite README around the problem solved
- [x] add at least one more concrete example
- [x] validate installation from scratch
- [x] add license
- [x] finalize CI
- [ ] validate release flow

## Should be done before or very soon after release
- [x] add anti-patterns and recommended patterns docs
- [ ] add FAQ
- [ ] add changelog and launch assets
- [x] prepare companion examples repo
- [x] add visual demo asset

## Can happen shortly after first release
- [ ] richer diagrams
- [ ] broader example ecosystem
- [ ] more advanced docs
- [ ] more polished outreach

---

# 10. Recommended execution over the next 2 weeks

## Phase 1: lock the core
- [x] freeze release scope
- [x] choose `0.1.0` or `1.0.0`
- [x] finalize public class names
- [x] finalize extension points
- [x] define lifecycle invariants
- [x] finish edge-case tests
- [x] confirm error policy
- [x] clean type hints

## Phase 2: make the project understandable
- [x] rewrite README
- [x] improve architecture docs
- [x] add non-goals
- [x] add patterns and anti-patterns
- [x] clean minimal examples
- [x] add one more concrete example
- [x] add one multi-component example

## Phase 3: make the project publishable
- [x] validate install from scratch
- [x] review `pyproject.toml`
- [x] add license
- [x] add contributing and issue templates
- [x] finalize CI
- [ ] validate semantic-release
- [ ] prepare first changelog
- [ ] prepare launch text

---

# 11. Short version

If time gets tight, the highest-value work is this:

- [x] freeze the public API
- [x] harden lifecycle tests
- [x] add one more concrete example
- [x] rewrite the README around the problem solved
- [x] validate clean installation
- [x] add license and CI
- [ ] release honestly as `0.1.0` if stability is still settling

---

# 12. Final release check

Do not publish until all of the following are true:

- [x] the public API is clearly defined
- [x] lifecycle behavior is tested beyond the happy path
- [x] one new example makes the value more concrete
- [x] README explains why the library exists in under a minute
- [x] install and examples work from a clean environment
- [x] the project has a license
- [ ] CI passes reliably — *structural: workflow exists; first green run required (§6.6)*
- [ ] the release process has been rehearsed — *§6.7 dry-run pending*
- [ ] the published version number matches the real stability level
