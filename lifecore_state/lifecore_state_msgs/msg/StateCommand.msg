# StateCommand v0 represents a single-target requested mutation.
#
# It expresses intent: "I request this target descriptor to change to this
# desired value." It is not observed truth. StateCommand does not claim that
# the requested value is already true or has been accepted.
#
# Batched command semantics (multiple targets in one message) are explicitly
# deferred until a concrete future need reopens the decision.
#
# Acceptance or rejection is not encoded by StateCommand itself. Future
# feedback may be represented through StateUpdate reflecting an observed
# change, service responses, action feedback, or a dedicated command status
# message. None of these feedback paths are implemented in Sprint 18.
#
# Fields are organized logically for readability (command metadata, not
# high-frequency transport).

# Transport header carries the command request event metadata.
std_msgs/Header header

# ============================================================================
# Command identity and scoping group
# ============================================================================

# Stable identity of the requester issuing this command.
# Used to correlate commands with a specific source for authorization and audit.
unique_identifier_msgs/UUID source_uuid

# Intended owner or receiver for this command.
# When the command is not broadcast to a scoped authority, target_uuid
# identifies the expected receiver.
unique_identifier_msgs/UUID target_uuid

# Schema used to interpret the target descriptor and value type.
# Must match StateDescription.schema_uuid for the declared description_version.
unique_identifier_msgs/UUID schema_uuid

# ============================================================================
# Ordering and versioning group
# ============================================================================

# Monotonically increasing sequence number per source_uuid stream.
# Used to detect lost, duplicated, or out-of-order commands.
uint64 sequence

# StateDescription version used to interpret the target descriptor identity,
# type, and semantics. Must match StateDescription.description_version for the
# declared schema_uuid. Receivers must not blindly apply commands against a
# different description version.
uint64 description_version

# ============================================================================
# Target descriptor identity group
# ============================================================================

# Compact numeric identifier of the target descriptor within the schema scope.
# Matches StateDescriptor.id.
uint32 target_descriptor_id

# Stable persistent identifier for the target descriptor.
# Matches StateDescriptor.uuid.
unique_identifier_msgs/UUID target_descriptor_uuid

# Canonical path or logical name, e.g., "drive/linear_velocity/setpoint".
# Matches StateDescriptor.key. Human-reviewable identity anchor.
string target_key

# ============================================================================
# Requested value group
# ============================================================================

# Declared value type for the requested mutation.
# Selects exactly one active value field below.
# TYPE_* constants are identical to StateDescriptor.msg and StateSample.msg
# for consistency. Sprint 18.8 may extract a shared StateType.msg.
uint8 type

# Desired value as explicit variant fields.
# Exactly one field is active, selected by type.
bool    bool_value
int64   int_value
uint64  uint_value
float64 float_value
string  string_value

# ============================================================================
# Type constants: identical to StateDescriptor.msg and StateSample.msg
# (v0 duplication, see Sprint 18.8)
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
