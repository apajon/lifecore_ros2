Lifecycle and State Separation
==============================

Purpose
-------

This document will explain how ``lifecore_state`` stays separate from
``lifecore_ros2`` lifecycle orchestration. Sprint 17.5 will complete the
separation rules before any integration design is considered.

Separation principles
---------------------

- lifecycle activation is not proof that a state value is valid;
- a valid state value is not proof that a lifecycle component is active;
- lifecycle transitions remain owned by ``lifecore_ros2`` components and nodes;
- state truth must not be hidden inside lifecycle transition machinery;
- optional future integration must be explicit and reviewed.

Current scope
-------------

This document does not change configure, activate, deactivate, cleanup,
shutdown, or error behavior. It is a planning artifact for architecture review.

Review questions
----------------

- Which lifecycle concepts are safe to reference from state documentation?
- Which state concepts must never become implicit lifecycle behavior?
- What integration points, if any, should be deferred beyond Sprint 17?

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.
