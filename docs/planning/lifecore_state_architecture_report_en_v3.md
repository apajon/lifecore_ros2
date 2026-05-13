# Architectural Extraction Report for a Typed I/O Bus and Observable Values in ROS 2

## 0. Purpose of this report

This report summarizes the architectural ideas derived from an industrial ROS 2 system, without attempting to reproduce its implementation.

The goal is to prepare a clean foundation for a future independent module, for example in `lifecore_ros2`, by separating:

1. reusable general principles;
2. choices that should be corrected or simplified;
3. standard technical terminology to use;
4. elements to avoid in order to protect the new codebase;
5. a cleaner, more generic, more industrial-grade target architecture.

The goal is not to copy an existing system. The goal is to formalize general patterns discovered through field experience, then restart from a new design.

---

## 1. Executive summary

The system under review contains three strong architectural ideas:

1. **Typed observable values**
   A local abstraction that encapsulates a value, its type, timestamp, identity, and notification mechanisms.

2. **Typed I/O bus over ROS 2**
   A variant-like message capable of transporting heterogeneous values such as booleans, integers, unsigned integers, floats, strings, and similar primitive types.

3. **State synchronization managers**
   Components capable of publishing, receiving, synchronizing, and filtering distributed states through local registries.

These ideas are relevant for industrial robotics. They address a real gap in ROS 2: representing hundreds of heterogeneous industrial variables without creating 500 topics or anonymous arrays split by type.

However, the current architecture is organic. It emerged from field requirements, which is normal, but it also carries the typical weaknesses of a system built progressively:

- too many responsibilities in some classes;
- strong coupling between local model, ROS messages, and communication logic;
- missing or weak explicit data quality model;
- risk of confusion between static description and dynamic state;
- callbacks that may become too implicit or magical;
- personal or domain-specific naming that should not be reused in a new project.

The main recommendation is to restart with three separate modules:

```text
lifecore_io_msgs      # Stable ROS 2 ABI: .msg files
lifecore_io_core      # Pure Python model: registry, typed values, quality
lifecore_io_ros       # rclpy integration: publishers, subscribers, bridges
```

The target design should use standard terminology:

- `TypedValue`
- `ObservableValue`
- `DataPoint`
- `Signal`
- `IORegistry`
- `StatePublisher`
- `CommandSubscriber`
- `DescriptionPublisher`
- `StateMirror`
- `Quality`
- `Snapshot`
- `DeltaUpdate`
- `Schema`
- `Descriptor`

---

## 2. Vocabulary: personal naming vs standard terminology

A major part of protecting the future codebase is to abandon personal, domain-specific, or historical names and use standard technical vocabulary instead.

| Personal or informal concept | Recommended technical term | Comment |
|---|---|---|
| Smart value | Observable value, typed value, reactive value, data point | "SmartValue" is understandable, but can be replaced by a more generic term |
| Register | Registry, signal registry, data registry | "Registry" is the classic term for a set of indexed objects |
| Comm manager | State synchronizer, state bridge, state publisher, state mirror | More precise depending on the actual role |
| Big register | Full registry, complete signal registry | Avoid informal wording |
| Reduced register | Scoped registry, partial registry, projected registry | Key term for the future design |
| Natural filtering by registry | Registry-scoped synchronization, local schema projection | Important pattern to formalize |
| Current state | Observed state, measured state, feedback state | "Current state" is acceptable, but "observed" or "feedback" clarifies the source |
| Target state | Desired state, command state, setpoint state | "Target" is acceptable, "desired" or "setpoint" is more standard |
| IO description | Signal descriptor, IO descriptor, data schema | Very close to "schema" or "descriptor" |
| I/O message bus | Typed I/O state bus, signal state stream | More industrial terminology |
| Complete snapshot | Full snapshot | Standard |
| Partial update | Delta update, incremental update | Standard |
| Unknown received value | Unknown signal, orphan value | "Unknown signal" is clearer |
| UUID created from path | Path-derived identity, deterministic identity | Important term |
| Expired value | Stale value | Standard |
| Forced value | Forced value, overridden value | Classic industrial term |
| Simulated value | Simulated value | Standard |
| Value quality | Data quality, signal quality | Essential in industrial systems |

---

## 3. Industrial problem addressed

The field requirement is typical of an industrial cell:

```text
Industrial robot
+ EtherCAT
+ ros2_control
+ hundreds of I/O variables
+ bool/int/uint/float/string values
+ fast feedback and slower supervision
+ ROS 2 business logic
```

ROS 2 provides very good domain messages for known use cases:

```text
sensor_msgs/JointState
sensor_msgs/Imu
nav_msgs/Odometry
geometry_msgs/Pose
```

But ROS 2 does not provide a strong standard for:

```text
500 heterogeneous industrial variables
with identity, type, quality, timestamp, description, and commands
```

The usual alternatives all have drawbacks:

| Approach | Problem |
|---|---|
| 500 topics | DDS explosion, heavy maintenance |
| One topic per type | Artificial synchronization between bool/int/float streams |
| MultiArray | No semantics, fragile indexing |
| diagnostic_msgs/KeyValue | Everything is a string, no strong typing |
| Domain-specific messages for every group | A lot of code, painful evolution |
| JSON in String | Not ROS-native, fragile parsing |
| Direct OPC-UA | Very good industrially, but not always integrated with ROS 2 business logic |

A typed I/O bus is therefore justified for the slow or semantic layer:

```text
ros2_control fast loop
    ↓
I/O bridge / signal extractor
    ↓
typed I/O state bus
    ↓
ROS 2 business logic, UI, logging, supervision, AI
```

---

## 4. Principle 1: typed observable value

### 4.1 Pattern description

The existing system contains an idea close to:

```text
ObservableValue[T]
```

or:

```text
TypedDataPoint[T]
```

Such a value usually contains:

```text
key
type
value
timestamp
quality
source
metadata
dirty flag
optional callbacks
```

This pattern is known under several names depending on the field:

- observable value;
- reactive variable;
- typed data point;
- signal object;
- blackboard entry;
- data binding primitive;
- monitored value.

### 4.2 What is worth keeping

Conceptually worth keeping:

- explicit typing;
- timestamping;
- stable identity;
- conversion to and from a transport format;
- change detection;
- ability to publish only changes;
- callbacks or notifications;
- registry structure to group values;
- serializability to ROS 2.

### 4.3 Main risk

The danger is that this abstraction becomes too large.

A value must not become all of the following at once:

```text
local value
+ full description
+ ROS message
+ publisher
+ subscriber
+ validator
+ callback manager
+ logger
+ converter
+ configuration tool
```

That creates an overly central, tightly coupled class that is hard to test and hard to replace.

### 4.4 Recommendation

In a new architecture, keep a very simple class:

```python
@dataclass
class TypedValue(Generic[T]):
    key: str
    value: T
    quality: Quality
    stamp: Time
    metadata: ValueMetadata
```

Then move the other responsibilities elsewhere:

```text
TypedValue           = local state
ValueDescriptor      = static description
ValueMapper          = message <-> model conversion
IORegistry           = storage and access
StatePublisher       = ROS publication
CommandSubscriber    = command reception
```

---

## 5. Principle 2: signal registry

### 5.1 Role

The registry is the set of signals known locally.

Recommended term:

```text
IORegistry
```

or:

```text
SignalRegistry
```

The registry should contain:

```text
id -> signal
uuid -> signal
key -> signal
```

It should support:

- fast lookup;
- applying an update;
- generating a snapshot;
- generating a delta;
- checking missing signals;
- detecting unknown signals;
- mapping description to value.

### 5.2 Important pattern: registry-scoped synchronization

This is the most interesting idea in the system.

Two managers can share the same ROS 2 topics while using different registries.

Example:

```text
Full publisher
registry = A, B, C, D, E, F
topic = /robot/io_state

Reduced subscriber
registry = A, C, F
topic = /robot/io_state
```

When the subscriber receives:

```text
A, B, C, D, E, F
```

it applies only:

```text
A, C, F
```

and ignores:

```text
B, D, E
```

This is filtering by intersection:

```text
applied_values = incoming_values ∩ local_registry
```

Recommended term:

```text
registry-scoped synchronization
```

or:

```text
local schema projection
```

### 5.3 Why it is powerful

This pattern avoids multiplying topics:

```text
/io_state_safety
/io_state_welding
/io_state_ui
/io_state_debug
/io_state_motion
```

Instead, keep one wide bus:

```text
/io_state
```

and let each consumer define its own local view through its registry.

Example views:

```text
full_registry       -> complete driver
safety_registry     -> safety only
welding_registry    -> welding only
ui_registry         -> display only
logging_registry    -> signals to record
debug_registry      -> temporary subset
```

### 5.4 Policies to formalize

The registry must have explicit policies.

For received but unknown signals:

```text
UnknownSignalPolicy:
  IGNORE
  WARN_ONCE
  WARN_ALWAYS
  ERROR
  AUTO_REGISTER_DISABLED
```

For expected but missing signals:

```text
MissingSignalPolicy:
  KEEP_LAST
  MARK_STALE_AFTER_TIMEOUT
  SET_INVALID
  RAISE_ERROR
```

For incompatible types:

```text
TypeMismatchPolicy:
  REJECT
  CAST_IF_SAFE
  ERROR
```

For stale values:

```text
StalePolicy:
  KEEP_BUT_MARK_STALE
  REMOVE
  SET_DEFAULT
  ERROR
```

---

## 6. Principle 3: typed I/O bus

### 6.1 Role

The typed I/O bus transports heterogeneous values over ROS 2.

It replaces weaker approaches:

```text
Float64MultiArray
String JSON
diagnostic_msgs/KeyValue
```

with a structured message:

```text
IOState
  header
  sequence
  description_version
  values[]
```

where each value is:

```text
IOValue
  id
  uuid
  type
  quality
  timestamp
  bool_value
  int_value
  uint_value
  float_value
  string_value
```

### 6.2 Transport pattern: explicit variant

Since ROS 2 `.msg` files do not provide an ergonomic variant type directly, use an explicit variant.

Example:

```text
uint8 type
bool bool_value
int64 int_value
uint64 uint_value
float64 float_value
string string_value
```

The active field is selected by `type`.

This is simple, ROS 2 compatible, readable by tools, and interoperable between Python and C++.

### 6.3 Limitation

This model is less elegant than a true language-level variant, but it is practical in ROS 2.

Mandatory rule:

```text
type must define exactly which value field is valid
```

Never interpret multiple value fields at the same time.

---

## 7. Principle 4: static description separated from dynamic state

### 7.1 Problem

If each value always carries:

```text
name
unit
description
group
min
max
writable
safety_related
```

then the fast bus becomes heavy.

For 500 I/O variables, repeating metadata at 10, 50, or 100 Hz is unnecessary.

### 7.2 Recommended pattern

Separate:

```text
/io_description
/io_state
/io_command
```

With:

```text
/io_description  = stable metadata
/io_state        = observed values
/io_command      = setpoints or write requests
```

### 7.3 Recommended QoS

```text
/io_description
  reliability: reliable
  durability: transient_local
  history: keep_last(1)

/io_state
  reliability: best_effort or reliable depending on criticality
  durability: volatile
  history: keep_last(1)

/io_command
  reliability: reliable
  durability: volatile
  history: keep_last(N)
```

### 7.4 Classic ROS analogy

`/io_description` plays a role similar to:

```text
robot_description
controller description
joint mapping
```

but for industrial signals.

A late subscriber should receive the latest complete description automatically.

---

## 8. Principle 5: deterministic identity

### 8.1 Field requirement

The source of truth may be an Excel file or similar tool.

Observed problem:

```text
UUIDs stored in Excel may be unstable
or regenerated by mistake
or modified during file manipulations
```

Using path-derived identity enables:

```text
uuid = hash(namespace + canonical_key)
```

Advantages:

- idempotent;
- reproducible;
- compatible with reduced registries;
- no need to store a manually generated UUID;
- the same signals keep the same identity after copying a subset.

Recommended term:

```text
path-derived deterministic identity
```

### 8.2 Risk

If the path changes, the identity changes.

Example:

```text
safety.door_closed
```

becomes:

```text
safety.main_door_closed
```

Then the derived UUID changes too.

### 8.3 Recommendation

The framework should support multiple identity policies:

```text
IdentityPolicy:
  PATH_DERIVED
  CONFIG_UUID
  EXTERNAL_ID
  NUMERIC_ID
```

In a Lifecore project:

```yaml
identity:
  policy: path_derived
  namespace: lifecore.robot.cell_001
  source_field: key
```

For a more stable industrial system:

```yaml
identity:
  policy: config_uuid
```

or:

```yaml
identity:
  policy: external_id
  source: plc_tag_id
```

### 8.4 Strong recommendation

Keep all three:

```text
uint32 id
UUID uuid
string key
```

Role:

```text
id    = compact, fast, useful in frequent streams
uuid  = stable global identity
key   = human-readable name, useful for debugging and description
```

---

## 9. Data quality: major missing piece to fix

### 9.1 Why it is essential

In industrial robotics, the value alone is not enough.

You need to know whether the value is:

```text
valid
old
forced
simulated
lost
out of range
coming from a communication error
```

Example:

```text
safety.door_closed = true
```

does not mean the same thing depending on:

```text
quality = VALID
quality = STALE
quality = FORCED
quality = COMM_ERROR
```

### 9.2 Recommended enum

```text
uint8 QUALITY_UNKNOWN=0
uint8 QUALITY_VALID=1
uint8 QUALITY_STALE=2
uint8 QUALITY_INVALID=3
uint8 QUALITY_COMM_ERROR=4
uint8 QUALITY_OUT_OF_RANGE=5
uint8 QUALITY_FORCED=6
uint8 QUALITY_SIMULATED=7
uint8 QUALITY_DISABLED=8
uint8 QUALITY_NOT_AVAILABLE=9
```

### 9.3 Important distinction

`quality` does not replace alarms.

A value can be:

```text
quality = VALID
value = temperature too high
```

This means:

```text
the measurement is reliable, but the process is in fault
```

Conversely:

```text
quality = COMM_ERROR
```

means:

```text
the value itself is not reliable
```

---

## 10. Timestamps and latency

### 10.1 Problem

In an industrial robot system with EtherCAT, ros2_control, and an internal controller, the feedback received by ROS can be delayed.

The timestamp must therefore be explicit.

### 10.2 Recommendation

In `IOValue`:

```text
header.stamp = instant when the value was true at the source
```

In `IOState`:

```text
header.stamp = instant when the ROS batch was published
```

Therefore:

```text
IOValue.header.stamp != IOState.header.stamp
```

### 10.3 Why it matters

For:

- trajectory tracking;
- latency compensation;
- camera/robot fusion;
- stale value detection;
- supervision;
- post-mortem analysis;
- rosbag synchronization.

---

## 11. Snapshot and delta update

### 11.1 Requirement

An efficient system should support two modes:

```text
FULL_SNAPSHOT
DELTA_UPDATE
```

Snapshot:

```text
publishes the complete state
useful for startup, resynchronization, debugging
```

Delta:

```text
publishes only changed values
useful to reduce bandwidth and CPU usage
```

### 11.2 Recommended message design

In `IOState.msg`:

```text
uint8 update_mode
uint8 UPDATE_FULL=1
uint8 UPDATE_DELTA=2
```

Add:

```text
uint64 sequence
uint64 description_version
```

### 11.3 Usefulness of `sequence`

Detect:

- lost messages;
- inverted order;
- duplicate publications;
- stream breaks.

### 11.4 Usefulness of `description_version`

Detect:

```text
I am receiving a state based on a newer description than the one I know
```

---

## 12. Proposed target architecture

### 12.1 Packages

```text
lifecore_io_msgs/
  msg/
    IODescriptor.msg
    IODescription.msg
    IODescriptionArray.msg
    IOValue.msg
    IOState.msg
    IOCommand.msg
    IOQuality.msg      # optional if constants should not be embedded
    IOType.msg         # optional
    IODirection.msg    # optional

lifecore_io_core/
  lifecore_io_core/
    identity.py
    quality.py
    types.py
    descriptor.py
    typed_value.py
    registry.py
    policies.py
    mapper.py
    snapshot.py
    delta.py

lifecore_io_ros/
  lifecore_io_ros/
    qos.py
    description_publisher.py
    state_publisher.py
    command_subscriber.py
    state_subscriber.py
    state_mirror.py
    registry_bridge.py
```

### 12.2 Responsibility separation

```text
lifecore_io_msgs
  Defines the public ROS 2 ABI.

lifecore_io_core
  Works without rclpy.
  Contains models, registries, policies, and pure conversions.

lifecore_io_ros
  Contains nodes, publishers, subscribers, QoS, and ROS 2 integration.
```

This matters for:

- testing without ROS;
- protecting the design;
- avoiding overly coupled classes;
- enabling a future C++ implementation;
- keeping messages stable.

---

## 13. Proposed messages

### 13.1 `IODescription.msg`

```text
std_msgs/Header header

uint32 id
unique_identifier_msgs/UUID uuid

string key
string display_name
string description
string group

uint8 type
uint8 direction

string unit
float64 min_value
float64 max_value
float64 default_float_value

bool writable
bool safety_related
bool persistent

uint8 TYPE_UNKNOWN=0
uint8 TYPE_BOOL=1
uint8 TYPE_INT64=2
uint8 TYPE_UINT64=3
uint8 TYPE_FLOAT64=4
uint8 TYPE_STRING=5

uint8 DIR_UNKNOWN=0
uint8 DIR_INPUT=1
uint8 DIR_OUTPUT=2
uint8 DIR_INOUT=3
```

Note: `default_float_value` is insufficient if every type needs a default. A cleaner version would use an `IOValue default_value`.

### 13.2 `IODescriptionArray.msg`

```text
std_msgs/Header header
uint64 description_version
IODescription[] descriptions
```

QoS:

```text
transient_local
reliable
keep_last(1)
```

### 13.3 `IOValue.msg`

```text
std_msgs/Header header

uint32 id
unique_identifier_msgs/UUID uuid

uint8 type
uint8 quality
uint8 source

bool bool_value
int64 int_value
uint64 uint_value
float64 float_value
string string_value

uint8 QUALITY_UNKNOWN=0
uint8 QUALITY_VALID=1
uint8 QUALITY_STALE=2
uint8 QUALITY_INVALID=3
uint8 QUALITY_COMM_ERROR=4
uint8 QUALITY_OUT_OF_RANGE=5
uint8 QUALITY_FORCED=6
uint8 QUALITY_SIMULATED=7
uint8 QUALITY_DISABLED=8
uint8 QUALITY_NOT_AVAILABLE=9

uint8 SOURCE_UNKNOWN=0
uint8 SOURCE_HARDWARE=1
uint8 SOURCE_SOFTWARE=2
uint8 SOURCE_SIMULATION=3
uint8 SOURCE_OPERATOR=4
uint8 SOURCE_REPLAY=5
```

### 13.4 `IOState.msg`

```text
std_msgs/Header header

unique_identifier_msgs/UUID source_uuid
uint64 sequence
uint64 description_version
uint8 update_mode

IOValue[] values

uint8 UPDATE_FULL=1
uint8 UPDATE_DELTA=2
```

### 13.5 `IOCommand.msg`

```text
std_msgs/Header header

unique_identifier_msgs/UUID target_uuid
uint64 sequence
uint64 description_version

IOValue[] values
```

### 13.6 Stricter compact variant

To avoid carrying `uuid` in every `IOValue` at high frequency:

```text
IOValueCompact.msg
  uint32 id
  uint8 type
  uint8 quality
  value fields...
```

Then keep `uuid/key/unit` only in `IODescription`.

For a first implementation, `IOValue` with both `id + uuid` is simpler.

---

## 14. Target Python API

### 14.1 `TypedValue`

```python
@dataclass
class TypedValue(Generic[T]):
    id: int
    uuid: UUID
    key: str
    value: T
    value_type: IOType
    quality: Quality = Quality.UNKNOWN
    stamp: Time | None = None
```

### 14.2 `IODescriptor`

```python
@dataclass(frozen=True)
class IODescriptor:
    id: int
    uuid: UUID
    key: str
    value_type: IOType
    direction: Direction
    unit: str = ""
    group: str = ""
    description: str = ""
    writable: bool = False
    safety_related: bool = False
```

### 14.3 `IORegistry`

Responsibilities:

```text
register_descriptor()
register_value()
apply_state()
apply_command()
make_snapshot()
make_delta()
mark_stale()
resolve_by_id()
resolve_by_uuid()
resolve_by_key()
```

### 14.4 `StatePublisher`

Responsibilities:

```text
publish snapshot
publish delta
manage sequence
manage description_version
```

### 14.5 `DescriptionPublisher`

Responsibilities:

```text
publish complete description
use transient_local QoS
republish if version changes
```

### 14.6 `CommandSubscriber`

Responsibilities:

```text
receive IOCommand
validate type/direction/writable
apply to registry or hardware adapter
```

---

## 15. Managers: simplify them

### 15.1 Typical problem

A "manager" can easily become too large.

Avoid:

```text
BaseManager
  handles lifecycle
  handles ROS topics
  handles state
  handles serialization
  handles callbacks
  handles registry
  handles timers
  handles feedback
  handles errors
```

This creates a central class that is hard to test.

### 15.2 Recommendation

Compose smaller objects:

```text
IORegistry
DescriptionPublisher
StatePublisher
CommandSubscriber
StateMirror
StaleMonitor
```

Then optionally create a thin orchestrator:

```text
IOBridgeNode
```

or:

```text
IOStateManager
```

The orchestrator must stay thin.

### 15.3 Recommended names

Instead of `CommManager`, use names according to the role:

| Role | Recommended name |
|---|---|
| Publishes local state | `StatePublisher` |
| Receives remote state | `StateSubscriber` |
| Maintains a remote copy | `StateMirror` |
| Publishes the description | `DescriptionPublisher` |
| Receives commands | `CommandSubscriber` |
| Bridges hardware and ROS | `IOBridge` |
| Synchronizes two registries | `RegistrySynchronizer` |

---

## 16. Callbacks: useful but dangerous

### 16.1 What is useful

Callbacks enable:

- publishing on change;
- cache invalidation;
- event triggering;
- updating derived state.

### 16.2 Risks

Callbacks can create:

- recursive calls;
- invisible side effects;
- fragile execution order;
- hard-to-test behavior;
- deadlocks when combined with locks;
- publication during remote reception.

### 16.3 Recommendation

Prefer a more explicit model:

```text
set value
mark dirty
flush dirty values at controlled rate
publish delta
```

Instead of:

```text
set value
immediate callback
immediate publish
callback from another object
re-publish
```

### 16.4 Recommended pattern

```python
registry.set("safety.door_closed", True)
registry.mark_dirty("safety.door_closed")

publisher.publish_delta(registry.collect_dirty())
```

This gives clear control over rate, order, and side effects.

---

## 17. Protecting the new code

### 17.1 Principle

Even if the experience comes from a professional project, the new code must be an independent reimplementation.

Goal:

```text
reuse general ideas
do not reuse concrete expression
```

### 17.2 Do not reuse

Do not reuse:

- specific class names;
- file names;
- folder structure;
- comments;
- docstrings;
- business logic;
- internal conventions;
- specific topics;
- non-standard domain-specific enums;
- exact architecture;
- existing tests;
- examples tied to the industrial cell;
- code snippets;
- specific API signatures.

### 17.3 What to do

- start from an empty repository;
- write a functional specification first;
- define new and standard vocabulary;
- write `.msg` files from generic requirements;
- write a new minimal API;
- write tests from expected behavior, not from existing code;
- document concepts with generic examples;
- keep neutral names: `IORegistry`, `IOState`, `IODescription`, `TypedValue`.

### 17.4 Useful framing

The project should not be presented as:

```text
a rewrite of what I built at work
```

but as:

```text
a generic typed I/O state bus model for ROS 2, inspired by common industrial integration problems
```

### 17.5 Limit

This report is not legal advice. If the module is intended to be published or monetized, employment contracts, internal policies, and applicable intellectual property rules should be reviewed.

---

## 18. What should deliberately be improved compared to the existing system

### 18.1 Add `quality`

High priority.

Without `quality`, an industrial bus is incomplete.

### 18.2 Add `description_version`

High priority.

Required to verify that a received state matches the known description.

### 18.3 Add `sequence`

High priority.

Required for debugging, message loss, ordering, and replay.

### 18.4 Separate description and state

High priority.

Do not mix metadata and current values.

### 18.5 Simplify observable values

Medium priority.

Reduce inheritance, callbacks, and implicit behavior.

### 18.6 Centralized mapper

Medium priority.

Use one class or module for conversion:

```text
TypedValue <-> IOValue
IODescriptor <-> IODescription
```

Do not scatter conversions everywhere.

### 18.7 Configurable policies

Medium priority.

Add:

```text
UnknownSignalPolicy
MissingSignalPolicy
StalePolicy
TypeMismatchPolicy
```

### 18.8 Behavioral tests

High priority.

Test:

- full snapshot;
- delta update;
- unknown signal ignored;
- missing signal marked stale;
- type mismatch rejected;
- reduced registry applying only its intersection;
- path-derived UUID stability;
- description version mismatch detection.

---

## 19. Recommended tests

### 19.1 Registry-scoped synchronization test

```text
Given:
  full_registry = A, B, C
  partial_registry = A, C

When:
  partial_registry.apply(IOState[A, B, C])

Then:
  A updated
  C updated
  B ignored
```

### 19.2 Unknown signal policy test

```text
Given:
  registry = A
  policy = WARN_ONCE

When:
  receive B

Then:
  B ignored
  warning emitted once
```

### 19.3 Stale policy test

```text
Given:
  value A last updated at t0
  stale_timeout = 1.0 s

When:
  now > t0 + 1.0 s

Then:
  A.quality = STALE
```

### 19.4 Deterministic identity test

```text
Given:
  namespace = "lifecore.test"
  key = "safety.door_closed"

When:
  generate_uuid(namespace, key) twice

Then:
  uuid1 == uuid2
```

### 19.5 Description version mismatch test

```text
Given:
  local_description_version = 4

When:
  receive IOState.description_version = 5

Then:
  state rejected or warning emitted
  description refresh requested
```

---

## 20. Application to Lifecore ROS 2

### 20.1 Positioning

For Lifecore, this component could become:

```text
lifecore_io_msgs
lifecore_io_core
lifecore_io_ros
```

It would be useful for:

- robot state;
- industrial I/O;
- robotics blackboard;
- telemetry;
- UI;
- debugging;
- inter-node synchronization;
- structured memory;
- bridges between hardware and business logic.

### 20.2 Relationship with ros2_control

Do not put this system in the fast control loop.

Recommended architecture:

```text
EtherCAT / hardware
    ↓
ros2_control hardware_interface
    ↓
real-time or near-real-time controllers
    ↓
slow extractor
    ↓
lifecore_io_ros
    ↓
/io_description
/io_state
/io_command
```

The typed bus is a slow semantic layer, not a hard real-time control loop.

### 20.3 Relationship with Lifecore memory

The model can also serve as a structured state indexing layer:

```text
IODescription = structure of signals
IOState       = current observation
IORegistry    = local operational memory
```

This is close to a blackboard, but typed, timestamped, and synchronizable.

---

## 21. Recommended roadmap

### Phase 1: ROS ABI

Create only:

```text
lifecore_io_msgs
```

With:

```text
IODescription.msg
IODescriptionArray.msg
IOValue.msg
IOState.msg
IOCommand.msg
```

Goal: stabilize the messages.

### Phase 2: pure Python core

Create:

```text
IORegistry
TypedValue
IODescriptor
Quality
IdentityPolicy
```

Without ROS.

Goal: test the logic outside rclpy.

### Phase 3: ROS bridge

Create:

```text
DescriptionPublisher
StatePublisher
CommandSubscriber
StateSubscriber
```

Goal: integrate cleanly with ROS 2.

### Phase 4: tools

Add:

```text
io_state_echo
io_description_dump
io_command_send
io_registry_validate
```

Goal: make the system usable by humans.

### Phase 5: Lifecore integration

Connect to:

```text
ros2_control
robot state
business I/O
UI
logging
```

---

## 22. Recommended design decisions

| Topic | Recommended decision |
|---|---|
| Identity | `id + uuid + key` |
| UUID | support `path_derived`, but not only that |
| Description | separate topic, transient local |
| State | `IOState` topic, snapshot + delta |
| Commands | `IOCommand` topic, reliable |
| Quality | mandatory |
| Timestamp | source timestamp in `IOValue`, publish timestamp in `IOState` |
| Callbacks | limited, prefer dirty sets |
| Managers | small composed components |
| ROS hot path | avoid |
| Tests | behavioral and independent |
| Naming | standard, neutral, non-domain-specific terms |

---

## 23. Conclusion

The observed system emerged from real needs and contains good ideas. The most important part is not the existing code, but the patterns it reveals:

```text
typed observable values
signal registry
registry-scoped synchronization
typed I/O state bus
description/state separation
snapshot/delta synchronization
deterministic identity
```

For Lifecore, the right path is to restart from a new design that is simpler, better named, better separated, and more industrial-grade.

The core of the future module should be:

```text
IODescription
IOValue
IOState
IOCommand
IORegistry
TypedValue
Quality
StatePublisher
StateMirror
```

The strongest idea to keep is registry-based filtering:

```text
one shared topic
multiple local registries
each registry applies only the intersection with the signals it knows
```

This is a powerful, clean, reusable pattern. It avoids topic proliferation while keeping specialized views.

The first concrete step should be to create a minimal `lifecore_io_msgs` package, without a complex Python framework. The messages should become the stable contract. Everything else can evolve.


---

## 24. Naming strategy and terminology redesign

### 24.1 Why renaming matters

The original system emerged organically from field experience and industrial constraints. As a consequence, some names were:

- highly domain-specific;
- tied to a particular industrial context;
- influenced by personal naming habits;
- discovered through experimentation rather than formal software architecture training.

For a future independent project, terminology should intentionally move toward:

```text
standard software architecture vocabulary
+
generic reusable concepts
+
neutral naming
```

This serves several goals simultaneously:

- clearer architecture;
- easier onboarding for other developers;
- stronger conceptual coherence;
- reduced coupling to the original industrial context;
- stronger separation from any proprietary implementation.

The goal is not to hide ideas. The goal is to express them using industry-neutral terminology.

---

### 24.2 Why `io` is probably too narrow

At first glance, the system appears to model industrial I/O.

However, the architecture is already broader than that.

The system can represent:

- industrial signals;
- robot state;
- runtime configuration;
- telemetry;
- distributed synchronization;
- blackboard-like shared state;
- semantic runtime information;
- memory-like structures;
- UI-bound variables;
- simulation state.

Therefore:

```text
I/O
```

is likely too restrictive as a long-term public abstraction.

The real concept is closer to:

```text
distributed typed state space
```

or:

```text
semantic synchronized state model
```

than simple industrial I/O.

---

### 24.3 Why `value` is probably too vague

The original concept informally referred to "smart values".

However, the object is not merely a value.

It also carries:

- identity;
- type;
- timestamp;
- synchronization semantics;
- quality;
- metadata;
- projection capability;
- distributed update behavior.

Therefore:

```text
value
```

does not fully capture the abstraction.

---

## 24.4 Recommended naming direction

The recommended public terminology is to center the architecture around the concept of:

```text
State
```

rather than:

```text
IO
Value
Register
Manager
```

Recommended repository structure:

```text
lifecore_state
```

with:

```text
lifecore_state_msgs
lifecore_state_core
lifecore_state_ros
```

This wording is:

- more generic;
- more scalable;
- more future-proof;
- less domain-specific;
- less tied to industrial automation vocabulary;
- less coupled to the original implementation context.

---

## 24.5 Recommended object names

### Replace `SmartValue`

Recommended replacement:

```text
StateField
```

Rationale:

The object represents:

- a typed field;
- inside a distributed state space;
- with synchronization semantics;
- identity;
- metadata;
- quality.

Examples:

```python
StateField[bool]
StateField[float]
```

Alternative acceptable names:

```text
TypedField
ObservableField
StateVariable
DataPoint
SignalField
```

But `StateField` is considered the cleanest and most scalable option.

---

### Replace `Register`

Do not use:

```text
Register
```

because it is strongly associated with:

- hardware registers;
- CPU registers;
- PLC registers;
- Modbus registers.

The actual concept is:

```text
an indexed collection of state fields
```

Recommended term:

```text
Registry
```

Examples:

```text
StateRegistry
SignalRegistry
FieldRegistry
```

Recommended preferred name:

```text
StateRegistry
```

---

### Replace `CommManager`

Avoid generic manager terminology entirely.

The original concept was overloaded and too implementation-oriented.

Instead, name components according to their precise role.

Recommended replacements:

| Role | Recommended name |
|---|---|
| Publishes local state | `StatePublisher` |
| Receives remote state | `StateSubscriber` |
| Maintains remote copy | `StateMirror` |
| Synchronizes registries | `RegistrySynchronizer` |
| Bridges domains | `StateBridge` |
| Publishes descriptions | `DescriptionPublisher` |
| Receives commands | `CommandSubscriber` |

This improves:

- readability;
- separation of responsibilities;
- testability;
- architectural clarity.

---

## 24.6 The strongest architectural concept discovered

The most important concept discovered during the development process is likely not the typed value itself.

It is:

```text
registry-scoped synchronization
```

or equivalently:

```text
state-space projection
```

The idea is:

```text
one shared distributed state bus
+
multiple local registries
+
each registry applies only the subset of signals it knows
```

This creates:

- natural filtering;
- no topic explosion;
- scalable distributed synchronization;
- multiple semantic projections over the same transport stream.

This is a significantly stronger abstraction than a simple industrial I/O bus.

It moves the architecture toward:

```text
distributed semantic state synchronization
```

rather than simple signal transport.

---

## 24.7 Final naming recommendation

The recommended long-term public naming strategy is:

```text
lifecore_state
```

with concepts such as:

```text
StateField
StateRegistry
StateDescriptor
StateSnapshot
StateDelta
StateProjection
StateMirror
StatePublisher
StateSubscriber
StateBridge
StateQuality
```

This terminology:

- aligns with standard architecture language;
- avoids domain-specific industrial naming;
- avoids personal naming habits;
- avoids coupling to the original project context;
- creates a cleaner conceptual model;
- better supports future extensions toward cognition, memory, synchronization, and distributed semantic systems.


---

# 25. Modern architectural patterns relevant to Lifecore ROS 2

## 25.1 Context

Modern software architectures have evolved significantly over the last few years under the influence of:

- distributed systems;
- complex robotics;
- multi-agent systems;
- large-scale simulation;
- agentic AI;
- advanced observability;
- dynamic runtimes;
- strong decoupling requirements.

Modern Python (3.10+) now enables patterns that previously belonged mostly to:

- Rust;
- C#;
- Scala;
- Kotlin;
- game engines;
- modern backend architectures.

Lifecore ROS 2 is already naturally aligned with:

- composition;
- modular runtime design;
- data-driven architecture;
- registries;
- lifecycle/behavior separation.

The following concepts can strengthen the architecture without breaking the ROS 2 model.

---

## 25.2 Event Bus

### Concept

An Event Bus allows components to communicate without direct knowledge of each other.

Instead of:

```python
navigation.stop_motor()
ui.show_warning()
logger.log()
```

a component emits an event:

```python
events.emit(
    ObstacleDetected(distance=0.3)
)
```

Then multiple systems may react independently:

```python
@events.on(ObstacleDetected)
def stop_robot(event):
    ...
```

```python
@events.on(ObstacleDetected)
def ui_warning(event):
    ...
```

### Benefits

#### Decoupling

The producer does not know:

- who is listening;
- how many listeners exist;
- what they do.

#### Extensibility

New systems can be added without modifying business logic:

- logging;
- monitoring;
- replay;
- diagnostics;
- analytics.

#### Observability

Events naturally support:

- audit trails;
- replay;
- postmortem debugging;
- timeline reconstruction.

---

### Recommended usage in Lifecore

Very relevant for:

- internal errors;
- diagnostics;
- metrics;
- lifecycle events;
- business events;
- safety;
- monitoring.

Examples:

```python
BatteryLow
EmergencyStop
ComponentError
MissionStarted
ObstacleDetected
```

---

### What to avoid

Do NOT turn every mutation into an event:

```python
ValueChanged
CounterIncremented
FloatUpdated
```

Otherwise the system degenerates into:

- event spaghetti;
- excessive noise;
- unreadable causality chains.

---

### Recommended architecture

```text
ROS2 topics/services
    distributed communication

EventBus
    intra-process communication
```

The internal bus does NOT replace ROS.

---

## 25.3 Event-Driven Architecture

### Concept

An architecture where reactions are triggered by domain events.

---

### Fundamental distinction

#### Command

Intent:

```python
StartMission(goal)
```

#### Event

Observed fact:

```python
MissionStarted(id=42)
```

---

### Benefits

Enables:

- decoupled workflows;
- multiple reactions;
- composable architecture;
- natural monitoring.

---

### Recommended usage

Very useful for:

- safety;
- supervision;
- diagnostics;
- UI;
- telemetry;
- lightweight orchestration.

---

### Risks

Making everything event-driven leads to:

- reduced readability;
- complex causal chains;
- difficult debugging.

---

### Good rule

```text
Commands -> intent
State -> truth
Events -> observed facts
```

---

## 25.4 ECS (Entity Component System)

### Concept

A data-oriented paradigm.

Strict separation between:

- entities;
- data;
- logic.

---

### Traditional OO model

```python
class Robot:
    pose
    battery
    navigation
    lidar
```

Everything is merged together.

---

### ECS model

#### Entity

Simple identifier:

```python
robot_1
```

---

#### Components

Pure data:

```python
Pose
Battery
Velocity
MissionState
```

---

#### Systems

Processing logic:

```python
navigation_system
battery_system
safety_system
```

---

### Benefits

#### Strong decoupling

Data does not depend on behavior.

#### Scalability

Very effective for:

- multi-robot systems;
- simulation;
- swarm robotics;
- digital twins.

#### Performance

Architecture becomes:

- cache-friendly;
- SIMD-friendly;
- parallelizable.

---

### Positioning inside Lifecore

Do NOT transform:

```text
LifecycleComponent -> ECS Component
```

That would be a conceptual mistake.

`LifecycleComponent` objects are closer to:

```text
lifecycle-aware systems
```

---

### Recommended mapping

```text
LifecycleComponentNode
    ROS2 lifecycle runtime

LifecycleComponent
    systems

StateField / Registry entries
    ECS-like component data

StateRegistry / StateStore
    ECS-world-like storage
```

---

### Recommended architecture

```text
lifecore_state
lifecore_registry
```

as a separate layer from the lifecycle core.

---

## 25.5 State Store / Data-Oriented Runtime

### Concept

Create a centralized runtime source of truth.

---

### Example

```python
robot_1:
    Pose
    Battery
    MissionState
```

Systems read and modify shared state.

---

### Benefits

#### Consistency

One place owns the real runtime state.

#### Introspection

Very useful for:

- debugging;
- monitoring;
- UI;
- replay;
- remote inspection.

#### Distributed synchronization

Naturally compatible with:

- registries;
- replication;
- partial views;
- filtered runtime.

---

### Strong alignment with Lifecore

The existing registry and observable-state concepts are already close to this model.

---

## 25.6 Domain Driven Design (DDD)

### Concept

Code should reflect the business domain.

Not only technical implementation.

---

### Bad example

```python
DataManager
Processor
Utils
```

---

### Better example

```python
BatteryMonitor
ElevatorMission
ObstacleSafety
HumanPresenceTracker
```

---

### Benefits

#### Business readability

The code speaks the language of the domain.

#### Human scalability

Extremely important in:

- robotics;
- complex systems;
- multidisciplinary teams.

---

### Lifecore application

Components should express:

- business role;
- not implementation detail.

---

## 25.7 DSL (Domain Specific Language)

### Concept

A specialized mini-language for a specific domain.

---

### Known examples

SQL:

```sql
SELECT * FROM users
```

Regex:

```python
r"\d+"
```

---

### Potential robotics usage

Example:

```yaml
WHEN obstacle < 0.5m
THEN stop
```

or:

```yaml
components:
  battery_monitor:
    threshold: 15
```

---

### Benefits

- less code;
- business-oriented configuration;
- automatic generation;
- accessibility for non-developers.

---

### Recommended positioning

Not in the immediate core.

But highly interesting later for:

- registries;
- diagnostics;
- workflows;
- orchestration;
- safety rules.

---

## 25.8 Code Generation (Codegen)

### Concept

Automatically generate code from schemas or models.

---

### Examples

From YAML:

```yaml
motor:
  max_speed: 2.0
```

generate:

- dataclasses;
- validators;
- documentation;
- ROS parameters;
- bindings;
- interfaces.

---

### Benefits

#### Duplication reduction

#### Automatic synchronization

#### Structural safety

#### Strongly typed APIs

---

### Strong relevance for Lifecore

Huge potential for:

- registries;
- state descriptors;
- diagnostics;
- distributed interfaces;
- parameters;
- runtime schemas.

---

## 25.9 Recommended modern architecture

```text
lifecore_ros2.core
    minimal lifecycle runtime

lifecore_events
    event bus
    diagnostics
    observers

lifecore_state
    state store
    registries
    ECS-like runtime

lifecore_diagnostics
    monitoring
    traces
    replay

lifecore_codegen
    schema -> code generation
```

---

## 25.10 Critical point

The existing lifecycle core must NOT become:

- an ECS framework;
- a giant orchestrator;
- a fully event-driven runtime engine.

The lifecycle layer must remain:

- minimal;
- explicit;
- stable;
- ROS-native.

---

## 25.11 Recommended layered architecture

```text
ROS2
    distributed communication

LifecycleComponentNode
    lifecycle runtime

LifecycleComponents
    systems / behaviors

StateStore
    runtime truth

EventBus
    decoupled reactions

Diagnostics
    observability

Codegen
    structural generation
```

---

## 25.12 Final summary

### Introduce relatively early

#### Intra-process EventBus

Very relevant.

#### Event-based diagnostics

Extremely useful.

#### Lightweight StateStore

Very coherent with the existing registry concepts.

---

### Introduce progressively

#### Lightweight ECS-inspired data model

Yes, but separate from lifecycle.

#### DDD

As an architectural discipline.

---

### Consider later

#### DSL
#### Advanced code generation

Very strong long-term potential.

---

## 25.13 Golden rule

```text
Lifecycle drives systems.
Systems modify state.
State is the source of truth.
Events describe what just happened.
ROS2 exposes what must leave the process.
```
