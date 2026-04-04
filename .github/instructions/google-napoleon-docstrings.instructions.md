---
name: "Google Napoleon Docstrings"
description: "Use when writing or updating Python docstrings for lifecore_ros2, especially lifecycle classes, ROS 2 Jazzy components, hooks, public APIs, and examples. Enforce concise Google-style docstrings compatible with Sphinx Napoleon."
applyTo: "src/lifecore_ros2/**/*.py"
---
# Google Napoleon Docstrings

- Use concise Google-style docstrings that work with Sphinx Napoleon.
- Document implemented behavior only. Do not invent lifecycle semantics, side effects, or guarantees.
- Prioritize public classes, public methods, properties, extension points, and non-obvious internal hooks.
- For lifecycle hooks, state when the hook is called, what resources it should manage, and which return behavior is expected when that meaning is not already obvious from the signature.
- Use sections such as Args, Returns, Raises, Attributes, and Examples only when they add information beyond the type hints.
- Keep docstrings aligned with ROS 2 Jazzy terminology used by the repository: lifecycle node, managed entity, configure, activate, deactivate, cleanup, shutdown, error.
- For thin wrappers and obvious property accessors, prefer short summary docstrings over repeated prose.
- When behavior is ambiguous in code, surface the ambiguity in chat instead of encoding a guess in the docstring.
