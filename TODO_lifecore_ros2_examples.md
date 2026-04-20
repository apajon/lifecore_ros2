# TODO — `lifecore_ros2_examples`

Planning artifact for the companion examples repository.
This file lives inside the core repo until the companion repository is created.
At that point it will move to `apajon/lifecore_ros2_examples` and be removed from here.

See `ROADMAP_lifecore_ros2_examples.md` for scope, boundary, and category outline.

---

## Phase 0 — Repository bootstrap

- [ ] Create `apajon/lifecore_ros2_examples` on GitHub
- [ ] Add `LICENSE` (Apache-2.0)
- [ ] Add `README.md` with:
  - one-line positioning
  - relationship to core `lifecore_ros2`
  - scope boundary (copied from `ROADMAP_lifecore_ros2_examples.md`)
  - install and run instructions
  - link back to the core repo and docs
- [ ] Add `pyproject.toml`:
  - Python 3.12+
  - dependency on `lifecore_ros2` from PyPI (current core release)
  - dev extras: `ruff`, `pyright`, `pytest`
- [ ] Add `.gitignore`, `.editorconfig` aligned with core repo conventions
- [ ] Add `.pre-commit-config.yaml` mirroring core (ruff, ruff-format)

---

## Phase 1 — First applied example: sensor-fusion pipeline

- [ ] Create `examples/sensor_fusion/sensor_fusion_pipeline.py`
- [ ] Two simulated heterogeneous sensors as `LifecyclePublisherComponent` instances
- [ ] Fusion `LifecycleComponent` with two subscriptions and one publisher
- [ ] Downstream `LifecycleSubscriberComponent` for logging
- [ ] Module docstring with:
  - one-line teaching axis
  - CLI commands to run it
  - expected log output per lifecycle transition
- [ ] Demonstrate the warm-up window (one input active, peer not yet delivering) with
      explicit inbound-drop behavior, no raised exceptions
- [ ] Demonstrate state reset on deactivate (rolling-average buffer cleared)
- [ ] Add a short `examples/sensor_fusion/README.md` explaining the topology and what to
      observe

---

## Phase 2 — Quality gates

- [ ] CI workflow: `ruff check`, `ruff format --check`, `pyright`, `pytest`
- [ ] Smoke test that imports each example module without invoking `rclpy.spin`
- [ ] Document validation commands in the repo `README.md`
- [ ] Confirm install-from-scratch on a clean ROS 2 Jazzy environment

---

## Phase 3 — Signposting back to core

- [ ] Update `lifecore_ros2/README.md` to link to the live companion repo URL
- [ ] Update `lifecore_ros2/docs/examples.rst` to link to the live companion repo URL
- [ ] Remove the *(planned — not yet published)* markers from the core repo
- [ ] Move `ROADMAP_lifecore_ros2_examples.md` and `TODO_lifecore_ros2_examples.md` from
      the core repo into the companion repo
- [ ] Update `lifecore_ros2/ROADMAP.md` to mark the companion repo as published

---

## Phase 4 — Second example (post-Phase-3)

- [ ] Choose between *lifecycle-aware diagnostics* and *multi-node orchestration* based
      on early user feedback on the sensor-fusion example
- [ ] Apply the same module-docstring discipline (one teaching axis, expected output)
- [ ] Avoid expanding into a domain framework — each example must remain followable in
      isolation

---

## Non-goals (do not add to this list)

- a regression test suite mirroring the core repo
- production-grade reference architectures
- a PyPI package
- documentation that supersedes the core docs
- backward-compatibility guarantees for example APIs across versions
