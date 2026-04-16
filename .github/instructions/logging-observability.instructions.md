---
name: "Logging and Observability Discipline"
description: "Use when implementing or reviewing Python lifecycle/component behavior, diagnostics, or error handling in lifecore_ros2. Enforce actionable logging and observability-first design."
applyTo: "src/lifecore_ros2/**/*.py, examples/**/*.py"
---
# Logging and Observability Discipline

- Log what matters for diagnosis and operations. Prefer high-signal logs over frequent status noise.
- For lifecycle transitions, log only meaningful state changes and failures.
- Include concise operational context in log messages (component, transition, reason, relevant identifier).
- Keep message templates stable so operators can filter and alert reliably.
- Treat errors as actionable events: include enough context to debug without reading source code.
- Avoid duplicate logs for the same event across multiple layers.
- Avoid heavy or repeated logging in hot paths (callbacks, high-frequency loops).
- Build features with observability in mind: expose measurable state and decision points where it helps incident triage.

## Anti-patterns

- Logs that restate obvious control flow on every iteration.
- Error logs without cause, context, or affected component.
- Mixed message styles that make production filtering unreliable.
