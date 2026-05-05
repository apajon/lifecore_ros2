Lifecycle policies
==================

**Status**: Design note (pre-implementation placeholder).

**Purpose**: Define explicit policies for component startup ordering, full-activation semantics, and optional bootstrap automation.

---

Background
----------

As applications grow, the question of "component ordering" emerges:

- Should component A configure before component B?
- Should the node be considered "fully active" only when all components have activated?
- Can startup be automated, or is explicit orchestration required?

The framework now enforces deterministic intra-node ordering through explicit
``dependencies``, ``priority``, and registration order as the stable fallback.
This design note reserves the remaining design space for higher-level policies
so order-based behavior does not become implicit again.

---

Key questions
--------------

1. **Configure order**: Should components configure sequentially in the existing resolved order or in parallel? Can one component's configure block a sibling's?
2. **Activate order**: Same question for activate.
3. **Full-activation semantics**: Is the node considered "active" as soon as it enters the ``active`` state, or only after all components are active?
4. **Deactivate order**: Reverse-order deactivation (last-registered first) or same order as activate?
5. **Bootstrap automation**: Should the node offer ``auto_configure()`` and ``auto_activate()`` helpers, or leave it to the application?

---

Policy dimensions
-----------------

- **Ordering**: Sequential (deterministic, slower) vs. parallel (faster, complex debugging)
- **Full-activation**: Loose (node-level state only) vs. strict (all components must confirm)
- **Reverse deactivation**: Yes (safer cleanup) vs. no (explicit orchestration)
- **Auto-bootstrap**: Opt-in helper vs. manual orchestration only

---

Success criteria
----------------

- [ ] Write a decision matrix: (policy choice) → (code examples, tradeoffs, failure modes)
- [ ] Document one recommended policy for common use cases
- [ ] Document how to implement alternative policies for specialized cases
- [ ] Add test cases for each policy variant

---

Related backlog items
---------------------

- Component dependencies (declarative ordering)
- Error handling contract (cascading failure on partial activation)
- Execution and timing (callback ordering)
