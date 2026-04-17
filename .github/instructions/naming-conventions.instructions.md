---
name: "Lifecycle Framework Naming Conventions"
description: "Use when naming classes, modules, or types in lifecore_ros2. Enforces stable framework type names, business-oriented application node names, and intentional component naming."
applyTo: "src/lifecore_ros2/**/*.py, tests/**/*.py, examples/**/*.py"
---
# Lifecycle Framework Naming Conventions

## Framework Type Names — Stable and Minimal

These names are fixed and must not be changed or aliased:

- `LifecycleComponent` — the core reusable abstraction for a lifecycle-aware modular unit.
- `LifecycleComponentNode` — the framework base node that owns and drives registered `LifecycleComponent` instances.

**Forbidden alternatives for `LifecycleComponent`:**
- `LifecycleCoreComponent`
- `LifecycleAbstractComponent`
- `BaseLifecycleComponent`
- Any mechanical variant that adds a redundant qualifier.

**Forbidden alternatives for `LifecycleComponentNode`:**
- `ComposedLifecycleNode`
- `ComponentLifecycleNode`
- `Lifecycle<Something>ComponentNode`
- Any application-specific or compound name applied to the base class itself.

## Application Node Names — Business-Oriented

Concrete application nodes must inherit from `LifecycleComponentNode` and use domain/business names, not framework names.

```python
# Correct
class CameraNode(LifecycleComponentNode): ...
class NavigationNode(LifecycleComponentNode): ...
class DiagnosticsNode(LifecycleComponentNode): ...

# Wrong — do not embed framework terms in application names
class LifecycleCameraNode(LifecycleComponentNode): ...
class CameraLifecycleComponentNode(LifecycleComponentNode): ...
```

The node name should communicate the domain or responsibility, not the framework mechanism.

## Component Names — Capability-Oriented

Framework-provided components follow the pattern `Lifecycle<Capability>Component`:

- `LifecyclePublisherComponent`
- `LifecycleSubscriberComponent`
- `LifecycleTimerComponent`
- `LifecycleServiceComponent`

Custom application-specific components should use the same pattern if they are reusable framework extensions. If they are specific to a single node, a shorter descriptive name is acceptable, but they must still inherit from `LifecycleComponent`.

## Naming Intent

- Keep framework type names stable and minimal so they remain usable as import targets without churn.
- Put technical framework semantics in base class names.
- Put business/domain meaning in concrete node class names.
- Avoid redundant, overly long, or mechanically generated names (e.g., appending `Base`, `Abstract`, `Core`, `Impl`).

## Review Triggers

- A base framework class is renamed without an explicit migration plan.
- An application node name contains `Lifecycle`, `Component`, or `Node` as a prefix/suffix beyond what is necessary.
- A new component class does not follow the `Lifecycle<Capability>Component` pattern.
- A class name embeds the framework mechanism when the domain meaning is available.
