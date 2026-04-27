# TODO `lifecore_ros2`

The first public release scope is implemented (core, components, examples, tests, docs,
license, CI workflow, packaging). What remains is split into pre-release follow-ups
and post-1.0 backlog.

See `ROADMAP.md` for the public-facing scope and `CHANGELOG.md` for shipped changes.

---

## 1. Pre-release follow-ups

Items still required before tagging the first public release.

### Release flow rehearsal

* [x] Run `uv run --group release semantic-release version --print --no-push` on `main`
      and confirm it computes the expected next version without errors (v0.3.0 shipped;
      next release will be `0.4.0` given the `feat:` commits on `main`)
* [x] Decide CHANGELOG handling: preamble frozen as the permanent first-release statement,
      semantic-release appends versioned entries below the `<!-- version list -->` marker
* [x] Dispatch the release workflow once on a test branch to confirm tag creation and
      GitHub Release publication
* [x] Confirm first green CI run on `main` and add status badge to `README.md`

### Launch assets

* [x] Draft GitHub release text for `v0.4.0` (canonical sentence verbatim, supported
      Python/ROS versions, included scope, known limitations, links to README and docs)
      — drafted in `docs/release_notes/v0.4.0.md`
* [x] Add a short FAQ covering: why not raw ROS 2 lifecycle directly, how this differs
      from a custom state machine, why components, what stays in this repo vs an
      application repo, current API stability level — `docs/faq.rst`, wired into
      `docs/index.rst`

### Final release gate

* [x] Confirm the published version number matches the real stability level (shipped as
      `v0.4.0` on the `0.x` beta track; promotion to `1.0.0` only when the API is judged
      stable) — released at https://github.com/apajon/lifecore_ros2/releases/tag/v0.4.0

---

## 2. Post-1.0 backlog

Deliberately deferred. Do not implement until there is a concrete user need.

### Config and specs

* [ ] `SpecModel`
* [ ] `AppSpec`
* [ ] `ComponentSpec`
* [ ] Topic component specs
* [ ] Add `pydantic>=2.0` to `dependencies` in `pyproject.toml` when `spec_model.py` is implemented (removed in a6280fd because unused at the time)

### Factory and registry

* [ ] `ComponentRegistry`
* [ ] `ComponentFactory`
* [ ] `SpecLoader`

### Callback group management

* [ ] Helper for `LifecycleComponentNode` to create and track `CallbackGroup` instances
      per component (tracking via a registry keyed by component name or ID; currently
      applications create callback groups manually via `node.create_callback_group(...)`)
* [ ] Optional: provide convenience constructors for common patterns
      (e.g., `create_exclusive_group_for_component(name)`)

### Additional components

* [ ] `TimerComponent`
* [ ] `ServiceComponent`
* [ ] `ActionComponent`
* [ ] `ParameterComponent`

### Binding layer

* [ ] Decide whether a dedicated binding layer is needed
* [ ] Add it only if components become overloaded

### Companion examples repo

* [ ] Add a first realistic applied example (see
      `ROADMAP_lifecore_ros2_examples.md` and `TODO_lifecore_ros2_examples.md`)

### README badges (post-release)

* [ ] Add PyPI version badge (`shields.io/pypi/v/lifecore-ros2`) once published on PyPI
* [ ] Add Python versions badge (`shields.io/pypi/pyversions/lifecore-ros2`) once on PyPI
* [ ] Add GitHub latest release badge (`shields.io/github/v/release/apajon/lifecore_ros2`) after first tagged release

---

## 3. Design constraints — do not violate

These are not tasks; they are guardrails for any future change.

* Do not recreate a parallel application state machine
* Do not reintroduce a vague "manager" abstraction
* Do not turn `TopicComponent` into a catch-all class
* Do not introduce magical configuration too early
* Do not introduce dynamic plugin loading too early
* Stay lifecycle-native to ROS 2
* Keep the node light
* Keep components specialised and bounded
