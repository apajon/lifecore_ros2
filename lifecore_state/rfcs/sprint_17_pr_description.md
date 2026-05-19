# Sprint 17: lifecore_state architecture RFC

## Summary

This PR adds architecture documentation for the future `lifecore_state` direction. It is intentionally limited to RFC, terminology, review, and planning material.

Key facts:

- No implementation
- No new ROS 2 package
- No new message compilation
- No runtime behavior change
- Documentation only

## Context

`lifecore_state` is a future direction for distributed typed state. Sprint 17 clarifies the architecture before any implementation work begins, so reviewers can discuss the model, terminology, lifecycle boundaries, package responsibilities, and anti-goals while the cost of change is still low.

This matters because the future state model must remain separate from the existing `lifecore_ros2` lifecycle framework. The RFC-style approach protects against scope creep, keeps `lifecore_ros2` behavior unchanged, and gives Sprint 18+ a reviewed foundation before message ABI or runtime package work starts.

## What Changed

- Repository audit
- Documentation-only `lifecore_state/` structure
- RFC 001 principal architecture document
- Terminology glossary
- Lifecycle/state separation clarification
- Package boundaries
- Message semantics
- Anti-goals
- Consistency review
- Final review checklist
- Static verification report
- This PR description draft

## What Did Not Change

- `lifecore_ros2` has no code changes
- No packages were created
- No build configuration changed
- No dependencies were added
- No runtime behavior was modified
- Public APIs are untouched

## Architecture Decisions

- `lifecore_state` is the chosen architecture name; `lifecore_io` is rejected as too narrow.
- `lifecore_state/` is a logical documentation folder during Sprint 17, not a ROS 2 package or Python runtime package.
- The parent `lifecore_state/` folder must not contain `package.xml`.
- Future package boundaries are `lifecore_state_msgs`, `lifecore_state_core`, and `lifecore_state_ros`.
- Lifecycle readiness and state validity remain cleanly separated.
- Anti-patterns such as hidden orchestration, giant managers, EventBus design, ECS runtime design, magical observable values, codegen-first design, and hidden synchronization are explicitly rejected.

## Critical Lifecycle Decision

StateDescription Lifecycle Behavior:

- `StateDescription` subscriber can receive `transient_local` messages while the node is inactive, during configure.
- Descriptions may be cached while inactive.
- `StateUpdate` deltas are NOT applied while inactive.
- `StateCommand` requires active lifecycle.

This semantic gating, per message type, is critical and differs from a global "ignore all callbacks while inactive" approach.

## Package Boundary Decision

Future package separation ensures:

- `lifecore_state_msgs`: ABI and message contracts only
- `lifecore_state_core`: pure Python, no ROS 2 dependencies
- `lifecore_state_ros`: ROS 2 integration only

Dependency rule: `lifecore_ros2` must remain independent of all `lifecore_state` packages.

## Anti-goals

Rejected patterns:

- No giant `StateManager`
- No magical observable values
- No auto-register unknown fields
- No orchestration runtime
- No codegen-first design
- No ECS framework
- No hidden synchronization

## Review Focus

**Key areas for review:**

1. Architectural boundaries, especially RFC sections 3-6
   Are the goals and non-goals clear and acceptable?

2. Lifecycle/state separation
   Is the `StateDescription` caching rule justified?
   Is semantic gating the right approach?

3. Package boundaries
   Are the three packages clearly separated?
   Are dependencies acyclic?

4. Message semantics
   Do the five message types cover the scope?
   Are QoS recommendations justified?

5. Terminology
   Are all terms accessible and consistent?

6. Anti-patterns
   Do the anti-goals protect against known risks?

## Acceptance Checklist

- [ ] No implementation added
- [ ] No package.xml under lifecore_state/
- [ ] No .msg files added
- [ ] No runtime behavior changed
- [ ] RFC is complete and reviewable
- [ ] Terminology is consistent
- [ ] Lifecycle/state separation is sound
- [ ] Package boundaries are clear
- [ ] Message semantics are complete
- [ ] Anti-goals protect the architecture
- [ ] All documents end with mandatory review phrase
- [ ] No architectural contradictions

## File Listing

New files:

- `lifecore_state/README.rst`
- `lifecore_state/rfcs/README.rst`
- `lifecore_state/rfcs/rfc_001_lifecore_state_architecture.rst`
- `lifecore_state/terminology.rst`
- `lifecore_state/message_semantics.rst`
- `lifecore_state/lifecycle_state_separation.rst`
- `lifecore_state/anti_goals.rst`
- `lifecore_state/package_boundaries.rst`
- `lifecore_state/rfcs/sprint_17_consistency_review.rst`
- `lifecore_state/rfcs/sprint_17_final_review_checklist.rst`
- `lifecore_state/rfcs/sprint_17_static_check.rst`
- `lifecore_state/rfcs/sprint_17_pr_description.md`
- `docs/planning/sprints/sprint_17_substeps/` with 13 sub-sprint files

Modified files:

- `docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst`
- `docs/planning/sprints/active/sprint_17_13_pr_description.rst`

## Open Questions

The remaining open questions are design questions for review and Sprint 18 planning, not contradictions in Sprint 17 documentation. They are deferred because Sprint 17 is documentation-only and should not settle ABI or runtime details without a focused follow-up review.

**Decided: StateCommand ABI shape.** Initial `StateCommand` semantics are single-target: one `StateCommand` targets one descriptor. Batched commands are deferred until a concrete need is established. Sprint 18 must not assume batched command semantics without explicitly reopening this decision.

- Minimal descriptor identity across launches, including UUIDs versus compact descriptor IDs
- ABI message fields versus pure Python validation helper fields
- Need for compact samples in high-rate streams
- Command feedback shape: message, service, or action
- Quality representation: fixed enum, extensible flags, or structured status
- Delta continuity, sequence recovery, and resynchronization in ROS messages
- Compatibility rules for `description_version` and descriptor versioning
- Timestamp naming for source time versus publish time
- Projection declaration through descriptors, policy objects, or separate documents
- Whether Sprint 18 needs accepted terminology for `StateStore` or `StateMirror`

Decision timeline: resolve the message ABI questions before or during Sprint 18 entry review. Keep pure Python semantics, ROS integration, lifecycle integration, tools, examples, and generated workflows deferred unless explicitly approved by follow-up planning.

## Related Issues/PRs

- Sprint 17 planning: `docs/planning/sprints/active/sprint_17_lifecore_state_rfc.rst`
- Sprint 17.13 planning card: `docs/planning/sprints/active/sprint_17_13_pr_description.rst`
- Sprint 18 candidate planning: `docs/planning/sprints/planned/sprint_18_lifecore_state_msgs_abi.rst`
- Original Sprint 17 issue: not linked in the current planning documents
- Related architecture discussions: captured in the Sprint 17 RFC and review documents listed above

## Final Notes

This PR is intentionally documentation-only and proposes no code.

It is designed for architectural review and discussion before any implementation commitment.

Sprint 18 will evaluate implementation of the message ABI first, pending acceptance of this RFC.

ChatGPT ou Codex relira et contrôlera ces livrables avant validation finale du Sprint 17.