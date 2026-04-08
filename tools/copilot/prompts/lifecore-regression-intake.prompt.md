---
name: "lifecore | Regression Intake"
description: "Use when reporting a ROS 2 Jazzy lifecycle regression to structure the report before handing off to the Regression Hunter orchestrator."
argument-hint: "Describe what broke, what was expected, what was observed, and where you suspect the issue."
agent: "Orchestrator | ROS 2 Regression Hunter"
---
Structure the regression report for this ROS 2 Jazzy lifecycle repository before delegating to the Regression Hunter.

Context:
- Repository: lifecore_ros2 (ROS 2 Jazzy, Python 3.12+, lifecycle-driven components)
- Core modules: src/lifecore_ros2/core/, src/lifecore_ros2/components/
- Tests: tests/test_core.py, tests/test_lifecycle.py, tests/test_components.py

Your task:
1. Rewrite the observed issue as a precise regression statement:
   - expected behavior (what passed before)
   - observed behavior (what fails or changed)
   - affected lifecycle phase: configure / activate / deactivate / cleanup / shutdown / error
2. Identify the most likely boundary where the regression lives:
   - lifecycle transition propagation
   - activation gating (callback fired while inactive)
   - resource ownership or cleanup (pub/sub not released)
   - topic behavior (publisher/subscriber component)
   - typing contract or __all__ drift
   - API naming or import change
3. Assess reproducibility:
   - Is it reliably reproducible? (yes / intermittent / unknown)
   - Is there an existing failing test, or does one need to be written?
   - Can a minimal deterministic example in examples/ demonstrate it?
4. List suspected files (core, components, tests, examples).
5. Define what "fixed" looks like as a concrete, testable criterion.
6. Identify explicit non-goals to prevent scope creep during repair.

If information is missing, ask targeted clarification questions before finalizing.

Output format:
- Regression statement
- Affected lifecycle phase and boundary
- Reproducibility assessment
- Suspected files
- Definition of fixed
- Non-goals
- Clarifications needed
