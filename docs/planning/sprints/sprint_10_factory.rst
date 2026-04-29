Sprint 10 — Minimal factory and registry
========================================

**Objectif.** Enable dynamic component instantiation; prepare foundation for future config-driven setup.

**Livrable.** "Components can be instantiated dynamically from a registry."

---

Content
-------

ComponentRegistry
^^^^^^^^^^^^^^^^^

- Class to register component types by name
- API:

  - ``register(name: str, component_class: Type[LifecycleComponent])`` — register a component type
  - ``is_registered(name: str) -> bool`` — check if type exists
  - ``get(name: str) -> Type[LifecycleComponent]`` — retrieve registered type

- Singleton pattern: ``ComponentRegistry.instance()`` or global registry

ComponentFactory
^^^^^^^^^^^^^^^^

- Class to instantiate components from registry
- API:

  - ``create(node: LifecycleComponentNode, component_type: str, component_name: str, **kwargs) -> LifecycleComponent`` — instantiate and register with node
  - ``create_batch(node, specifications: List[Dict]) -> Dict[str, LifecycleComponent]`` — create multiple components from list

- Factory uses registry to look up component type
- Pass ``**kwargs`` to component constructor

SpecLoader (optional, minimal)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Light-weight loader for component specifications (future use)
- For this sprint: just return parsed dict (no schema validation yet)
- API: ``load_spec(spec_file: str) -> Dict`` — load and parse YAML/JSON spec

Example use case:

.. code-block:: python

   registry = ComponentRegistry.instance()
   registry.register("my_service", MyServiceComponent)

   factory = ComponentFactory(registry)
   component = factory.create(node, "my_service", "svc1")
   node.add_component("svc1", component)

---

Tests to write
--------------

Registry tests
^^^^^^^^^^^^^^

- [x] Register component type by name
- [x] Retrieve registered type
- [x] Duplicate registration (overwrite or error? Pick one, document it)
- [x] Unregister component type (optional)
- [x] ``is_registered`` returns True/False correctly

Factory tests
^^^^^^^^^^^^^

- [x] Create component instance from registry
- [x] Pass kwargs to component constructor
- [x] Create batch of components from list
- [x] Error if component type not registered (raise ``ComponentNotRegisteredError``)
- [x] Factory instance integrates with node

SpecLoader tests (minimal)
^^^^^^^^^^^^^^^^^^^^^^^^^^

- [x] Load YAML spec file (basic dict parsing, no schema yet)
- [x] Load JSON spec file
- [x] Error on missing file or parse error
- [x] Return parsed dict

Integration tests
^^^^^^^^^^^^^^^^^

- [x] Register, create, and lifecycle all components (nominal path)
- [x] Multiple components created from specs
- [x] Specs drive component creation; no hardcoding

---

Risks and mitigation
--------------------

**Risk 1: Premature schema binding**

- **Problem**: Over-specifying component specs too early constrains future flexibility.
- **Mitigation**:
  - SpecLoader is minimal (just dict parsing, no validation)
  - No Pydantic model or schema for this sprint
  - Specs are free-form dicts; application validates as needed
  - Schema (if needed) is post-1.0 SpecModel effort

**Risk 2: Tight coupling between registry and factory**

- **Problem**: Factory is hard to extend if registry changes.
- **Mitigation**:
  - Factory accepts registry as a parameter (dependency injection)
  - Registry is simple and stable (unlikely to change)
  - Factory is a thin wrapper; easy to subclass if needed

**Risk 3: Duplicate registrations**

- **Problem**: Registering same type twice (e.g., in different modules).
- **Mitigation**:
  - Document behavior: overwrite (latest wins) or error (first wins)?
  - Pick one, enforce in tests, document in docstring

**Risk 4: Component constructor kwargs are unchecked**

- **Problem**: Passing invalid kwargs to component constructor silently fails or raises unhelpful error.
- **Mitigation**:
  - Documented contract: kwargs must match component ``__init__`` signature
  - Let Python raise TypeError if mismatch (clear error)
  - Factory does not validate (that's component's job)

---

Dependencies
------------

- Requires: All components (Sprints 1–9)
- Requires: Testing utilities (Sprint 3) — fixtures for registry/factory testing
- Requires: No external dependencies (dict parsing with stdlib)

---

Scope boundaries
----------------

**In-scope:**

- ``ComponentRegistry`` — register and retrieve component types
- ``ComponentFactory`` — create component instances dynamically
- ``SpecLoader`` (minimal) — parse YAML/JSON specs into dicts
- Batch creation — create multiple components from spec list
- Error handling — clear exceptions for missing types, etc.

**Out-of-scope:**

- Schema validation (deferred to SpecModel sprint, post-1.0)
- Config-driven activation policies (separate concern)
- Dynamic component removal at runtime (deferred, complex)
- Plugin loading from external files (out of scope)

---

Success signal
--------------

- [x] ``ComponentRegistry`` and ``ComponentFactory`` are exported
- [x] Register component type, create instance, add to node (nominal path works)
- [x] All tests pass (unit + integration + edge cases)
- [x] Batch creation works: ``factory.create_batch(node, specs_list)``
- [x] SpecLoader parses YAML and JSON specs
- [x] Error messages are clear (missing type, parse error, etc.)
- [x] Example: ``examples/factory_demo.py`` (demonstrates registry + factory + specs)
- [x] Ruff, Pyright, Pytest all green
- [x] Docstrings complete (Google style, Napoleon-ready)
- [x] Documentation: how to use registry/factory for dynamic setup

---

Location
--------

- Module: ``src/lifecore_ros2/factory.py`` (or ``src/lifecore_ros2/factory/__init__.py``)
- Exports: ``src/lifecore_ros2/__init__.py``
- Tests: ``tests/test_factory.py`` (new)
- Examples: ``examples/factory_demo.py`` (new)

---

Example spec file
-----------------

``examples/specs.yaml``:

.. code-block:: yaml

   components:
     - name: publisher1
       type: my_publisher_component
       kwargs:
         topic: "/sensor/data"
         msg_type: sensor_msgs.msg.Temperature

     - name: subscriber1
       type: my_subscriber_component
       kwargs:
         topic: "/sensor/data"

     - name: service1
       type: my_service_component
       kwargs:
         service_name: "/process_data"

Usage:

.. code-block:: python

   loader = SpecLoader()
   specs = loader.load("examples/specs.yaml")

   factory = ComponentFactory()
   components = factory.create_batch(node, specs["components"])

---

Related post-1.0 work
---------------------

- SpecModel (post-1.0) — formalize component specifications with Pydantic
- AppSpec (post-1.0) — application-level specification schema
