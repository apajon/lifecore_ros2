# Contributing to lifecore_ros2

## Scope

This is a small, abstract lifecycle composition library for ROS 2 Jazzy.
Contributions should remain narrow and reviewable.

A change belongs here if it is **framework-level and message-type-agnostic**.
Domain-specific patterns (sensors, actuators, multi-node orchestration) belong in
the companion repository `lifecore_ros2_examples` instead.

## Canonical positioning sentence

The project's positioning sentence is the single source of truth for how
`lifecore_ros2` is described to users. The canonical copy lives in
`pyproject.toml` under `project.description`. It is reused **verbatim** in:

- `README.md` (top of file)
- `docs/index.rst` (first paragraph)
- `docs/architecture.rst` (Overview)
- `ROADMAP.md` (top of file)
- future release notes, FAQ, and launch assets

When updating the sentence, edit `pyproject.toml` first, then propagate the
exact same string to every surface above. A `grep -F` of the sentence across
the repository must return matches in all listed files.

## Prerequisites

- Python 3.12+
- ROS 2 Jazzy installed on the system (`source /opt/ros/jazzy/setup.bash`)
- [`uv`](https://docs.astral.sh/uv/) available in the workspace

`rclpy` comes from the system ROS installation and is **not** declared in
`pyproject.toml`.

## Local setup

```bash
source /opt/ros/jazzy/setup.bash
uv sync --extra dev
```

Add the docs toolchain when touching documentation:

```bash
uv sync --extra dev --group docs
```

## Validation commands

Run all checks before opening a pull request:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

Build and verify distribution metadata:

```bash
uv build
uv run --with twine twine check dist/*
```

Build documentation locally:

```bash
uv run --group docs python -m sphinx -b html docs docs/_build/html
```

## Commit conventions

This repository uses [Conventional Commits](https://www.conventionalcommits.org/).
`python-semantic-release` derives the next version and changelog from commit
messages — non-conforming messages are silently ignored at release time.

Common prefixes:

| Prefix | When to use |
|--------|-------------|
| `feat:` | New public behavior or API addition |
| `fix:` | Bug fix in existing behavior |
| `docs:` | Documentation-only change |
| `chore:` | Tooling, CI, packaging, refactor with no behavior change |
| `test:` | Test additions or corrections |
| `perf:` | Performance improvement |

Breaking changes: add `BREAKING CHANGE:` in the commit footer.

## Pull request checklist

- [ ] All four validation commands pass
- [ ] `uv build` + `twine check` pass
- [ ] New behavior has at least one focused pytest test
- [ ] If lifecycle semantics change, an example in `examples/` is added or updated
- [ ] Public `__all__` and type annotations are unchanged unless explicitly intended
- [ ] Commit messages follow Conventional Commits

## Design constraints

See [`docs/architecture.rst`](docs/architecture.rst) for the full member-convention
taxonomy and lifecycle invariants. Short version:

- preserve native ROS 2 lifecycle semantics — no parallel state machine
- create topic resources in `_on_configure`, release them in `_on_cleanup`
- gate runtime behavior with activation state (`_is_active` / `@when_active`)
- keep `_on_*` hooks focused and deterministic
- raise `LifecoreError` subclasses for boundary violations; drop inbound callbacks silently

## Running the release pipeline (maintainer only)

Releases are triggered manually via the **Release** workflow in GitHub Actions.
Before dispatching:

1. Confirm CI is green on `main` (run the CI workflow from the Actions tab if needed).
2. Preview the computed version: `uv run --group release semantic-release version --print`
3. Dispatch the Release workflow from the GitHub UI.

See [`docs/contributing.rst`](docs/contributing.rst) for additional context on the
documentation toolchain and style expectations.
