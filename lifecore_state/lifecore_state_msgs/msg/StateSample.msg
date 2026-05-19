# StateSample defines one observed state value at a source timestamp.
#
# It represents runtime truth as observed by a source for one descriptor field.
# It is not metadata, a descriptor, or a command.
#
# header.stamp is the source timestamp: the time when the value was observed
# at the source, not the publication time of the containing StateUpdate.

# Transport header carries source timestamp metadata.
std_msgs/Header header

# ============================================================================
# Descriptor identity group: references to the source StateDescriptor
# ============================================================================

# Compact numeric identifier within the declared StateDescription scope.
# Matches StateDescriptor.id for the containing schema.
uint32 descriptor_id

# Stable persistent identifier for the descriptor across launches and bridges.
# Matches StateDescriptor.uuid.
unique_identifier_msgs/UUID descriptor_uuid

# Canonical path or logical name, e.g., "battery/pack/main/voltage".
# Matches StateDescriptor.key.
string key

# ============================================================================
# Value type and context group
# ============================================================================

# Declared active value type for this sample.
# Selects exactly one active value field below.
# TYPE_* constants are identical to StateDescriptor.msg to ensure consistency.
# Sprint 18.8 may extract a shared StateType.msg; until then, constants are duplicated.
uint8 type

# Reliability and validity state of the observed value.
# Describes value reliability, not lifecycle state.
uint8 quality

# Semantic identity of the observation source.
# Must not be inferred solely from the ROS node relaying the message.
# Reports observed truth; SOURCE_COMMANDED is not included (belongs to StateCommand).
uint8 source

# ============================================================================
# Variant value group: exactly one field is active, selected by type
# ============================================================================

bool    bool_value
int64   int_value
uint64  uint_value
float64 float_value
string  string_value

# ============================================================================
# Type constants: identical to StateDescriptor.msg (v0 duplication, see Sprint 18.8)
# ============================================================================

uint8 TYPE_UNKNOWN=0
uint8 TYPE_BOOL=1
uint8 TYPE_INT8=2
uint8 TYPE_INT16=3
uint8 TYPE_INT32=4
uint8 TYPE_INT64=5
uint8 TYPE_UINT8=6
uint8 TYPE_UINT16=7
uint8 TYPE_UINT32=8
uint8 TYPE_UINT64=9
uint8 TYPE_FLOAT32=10
uint8 TYPE_FLOAT64=11
uint8 TYPE_STRING=12
uint8 TYPE_BYTES=13

# ============================================================================
# Quality constants: value reliability and validity states
# ============================================================================

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

# ============================================================================
# Source constants: semantic identity of the observation origin
# ============================================================================

uint8 SOURCE_UNKNOWN=0
uint8 SOURCE_HARDWARE=1
uint8 SOURCE_SOFTWARE=2
uint8 SOURCE_SIMULATION=3
uint8 SOURCE_OPERATOR=4
uint8 SOURCE_REPLAY=5
