# TODO `lifecore_ros2`

The first public release scope is implemented (core, components, examples, tests, docs,
license, CI workflow, packaging). What remains is split into pre-release follow-ups
and post-1.0 backlog.

See `ROADMAP.md` for the public-facing scope and `CHANGELOG.md` for shipped changes.

---

## 1. Pre-release follow-ups

Items still required before tagging the first public release.

### Release flow rehearsal

* [ ] Run `uv run --group release semantic-release version --print --no-push` on `main`
      and confirm it computes `0.1.0` without errors
* [ ] Decide CHANGELOG handling: freeze current content as-is, or let semantic-release
      overwrite from `v0.1.0` forward
* [x] Dispatch the release workflow once on a test branch to confirm tag creation and
      GitHub Release publication
* [ ] Confirm first green CI run on `main` and add status badge to `README.md`

### Launch assets

* [ ] Draft GitHub release text for `v0.1.0` (canonical sentence verbatim, supported
      Python/ROS versions, included scope, known limitations, links to README and docs)
* [ ] Add a short FAQ covering: why not raw ROS 2 lifecycle directly, how this differs
      from a custom state machine, why components, what stays in this repo vs an
      application repo, current API stability level

### Final release gate

* [ ] Confirm the published version number matches the real stability level (default:
      `0.1.0` beta unless API is judged defensible as `1.0.0`)

---

## 2. Post-1.0 backlog

Deliberately deferred. Do not implement until there is a concrete user need.

### Config and specs

* [ ] `SpecModel`
* [ ] `AppSpec`
* [ ] `ComponentSpec`
* [ ] Topic component specs

### Factory and registry

* [ ] `ComponentRegistry`
* [ ] `ComponentFactory`
* [ ] `SpecLoader`

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
