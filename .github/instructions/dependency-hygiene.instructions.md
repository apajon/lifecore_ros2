---
name: "Dependency Hygiene"
description: "Use when adding, updating, or reviewing Python dependencies, build tooling, or packaging metadata in lifecore_ros2. Keep dependencies minimal, justified, and current."
applyTo: "pyproject.toml, requirements*.txt, .pre-commit-config.yaml, .github/workflows/**/*.yml"
---
# Dependency Hygiene

- Keep dependencies minimal and up to date. Prefer fewer, well-maintained libraries.
- Add a new dependency only when standard library or existing project dependencies cannot solve the problem clearly.
- For each new dependency, document the reason in the PR summary or commit message.
- Prefer mature libraries with active maintenance and clear versioning policy.
- Avoid overlapping dependencies that solve the same problem.
- Remove transitive or direct dependencies that are no longer used.
- Do not add `rclpy` as a normal PyPI dependency; it is provided by the system ROS installation.
- Use project command policy with `uv` workflows (no direct `pip` usage).

## Update Policy

- Prefer constrained, reviewable version updates over bulk upgrades without validation.
- After dependency changes, run lint, type-check, tests, and build checks.
