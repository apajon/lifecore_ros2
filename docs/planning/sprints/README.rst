Sprint planning
===============

Structured sprints for extending lifecore_ros2 without architectural drift.

Each sprint = **concrete + stable + testable deliverable**.

Sprint cards stay at framing level: they document decisions already made,
constraints, risks, and success criteria. Exact signatures, commit breakdown,
final internal names, and execution details are decided at the beginning of the
sprint during planning.

---

Principles
----------

- **No sprint mixing.** Each sprint stays isolated, reviewable, and backportable.
- **No premature coupling.** ServiceComponent does not know Factory; Factory knows Registry.
- **Definition of Done.** Each sprint has a clear definition: code + tests + docs.
- **Named risks.** Pitfalls are identified and mitigated before coding.
- **No premature design.** A card may name an agreed direction, but it does not
   freeze an API that still needs sprint planning.

---

Sprint roadmap
--------------

.. toctree::
   :maxdepth: 1

   sprint_1_service_client
   sprint_2_error_handling
   sprint_3_testing_infrastructure
   sprint_4_lifecycle_comparison
   sprint_4_5_state_component_example
   sprint_5_internal_cascade
   sprint_5_1_composition_surface
   sprint_6_callback_gating
   sprint_7_cleanup_api
   sprint_8_concurrency
   sprint_9_observability
   sprint_10_health_status
   sprint_11_watchdog_light
   sprint_12_lifecycle_policies
   sprint_13_parameters
   sprint_14_factory
   sprint_15_tooling_generation

---

Condensed View
--------------

::

   S1: Service/Client components (ROS 2 primitives)
   S2: Solid error handling (lifecycle reliability)
   S3: Testing infrastructure (acceleration)
   S4: Lifecycle comparison example (product proof)
   S4.5: State-only component example (core teaching pattern)
   S5: Internal component cascade (deterministic ordering)
   S5.1: Composition surface (API and teaching follow-up)
   S6: Centralized callback gating (consistency)
   S7: Cleanup and ownership API (explicit resources)
   S8: Clean concurrency (multi-threaded use)
   S9: Minimal observability (debugging)
   S10: Health status API (readable observability)
   S11: Lightweight watchdog (observer/report)
   S12: Lifecycle policies (ordering and activation)
   S13: Parameters (runtime configuration)
   S14: Minimal factory (dynamic instantiation)
   S15: Tooling and generated nodes (scaffolding)

---

Outside the Immediate Roadmap
-----------------------------

**Do not include in these sprints:**

- SpecModel / AppSpec
- ActionComponent (after S1)
- Binding layer (if ever needed)
- Advanced robot control (outside core scope)
- MCP runtime or direct AI behavior in the library

---

Sprint Dependencies
-------------------

::

   S1-S3 (foundation)
      v
   S4 (comparison example)
      v
   S4.5 (state-only component example)
      v
   S5 (internal cascade)
      v
   S5.1 (composition surface)
      v
   S6 (callback gating)
      v
   S7 (cleanup ownership)
      v
   S8 (concurrency)
      v
   S9 (observability)
      v
   S10 (health status)
      v
   S11 (watchdog light)
      v
   S12-S14 (policies, parameters, factory)
      v
   S15 (tooling / generation)

**Recommended sequencing:**

1. S4 before any major new API - prove the product value.
2. S5 next - deliver the main internal differentiator.
3. S5.1 immediately after S5 - API and teaching follow-up for composition.
4. S6-S9 harden runtime behavior before diagnostic-facing surfaces.
5. S10 then S11 expose health before observing it automatically.
6. S12-S14 remain advanced surfaces, after the deterministic core.
7. S15 only after stabilization - generate code from solid conventions.

---

Definition of Done (All Sprints)
--------------------------------

Each sprint must satisfy:

- ✓ Code with Google-style docstrings
- ✓ Unit tests (nominal + edge cases)
- ✓ Integration tests (with other components when applicable)
- ✓ Regression tests for bug fixes
- ✓ Ruff + Pyright + Pytest green
- ✓ Documentation (docstrings + design notes for architecture changes)
- ✓ CONTRIBUTING.md updated for new patterns
- ✓ Example(s) for user-facing surfaces

---

Sprint Card Format
------------------

Each sprint file contains:

- **Objective** - what should be true at the end
- **Decisions already made** - invariants, limits, agreed behavior
- **To decide during planning** - exact API, breakdown, implementation order
- **Validation** - observable criteria and expected tests
- **Risks** - named pitfalls and mitigations
- **Dependencies** - what must be done first
- **Scope boundaries** - what is intentionally excluded
- **Success signal** - how to validate that the sprint worked

---

Execution Notes
---------------

- Each sprint = one branch or a logical set of commits.
- Review by sprint, not line by line in isolation.
- If a sprint reveals a needed decoupling, schedule a small refactor before or
   after the sprint instead of hiding it inside the sprint.
- Do not add incidental architecture improvements to a sprint; record them for a dedicated sprint.
