# StateDescriptor defines one state field contract.
#
# It describes what state exists, how it is identified, how it is typed,
# and whether it can be commanded. It must not contain the current runtime value.
#
# Fields are organized logically for readability (schema metadata, not high-frequency transport).

# Transport header carries the descriptor publication event metadata.
std_msgs/Header header

# ============================================================================
# Identity group: stable identifiers for this descriptor
# ============================================================================

# Compact numeric identifier within the description/registry scope.
# Useful for compact updates but not globally meaningful by itself.
uint32 id

# Stable identifier for the descriptor across launches, exports, or bridges.
# Derived from stable semantic paths rather than generated at runtime.
unique_identifier_msgs/UUID uuid

# Canonical path or logical name, e.g., "battery/pack/main/voltage".
# The human-reviewable identity anchor.
string key

# ============================================================================
# Type system group: semantic value type and flow direction
# ============================================================================

# Declared value type. Selects the active value field in future StateSample.
uint8 type

# Direction of allowed flow: OUT (observed), IN (commandable), or INOUT (bidirectional).
uint8 direction

# ============================================================================
# Metadata group: human-readable and semantic context
# ============================================================================

# Display name for user interfaces and documentation.
string display_name

# Description explaining the purpose and semantics of this descriptor.
string description

# Logical group or category for organizational purposes.
string group

# Physical or semantic unit, e.g., "V", "A", "degC", "m/s", "".
# Empty string means unitless or unspecified.
string unit

# ============================================================================
# Behavioral flags: how the descriptor can be used and its relevance
# ============================================================================

# True if a future StateCommand may request mutation for this descriptor.
# Does not guarantee that every command will be accepted.
bool writable

# True if misuse can affect safety policy, operator review, or validation.
# Metadata flag, not a runtime safety implementation.
bool safety_related

# True if this descriptor represents persistent or durably stored state.
# Descriptive metadata only; does not implement persistence semantics.
bool persistent

# ============================================================================
# Constraints group: numeric bounds only (non-numeric constraints deferred)
# ============================================================================

# Minimum allowed value for numeric types. Only meaningful if has_min_value is true.
float64 min_value

# Maximum allowed value for numeric types. Only meaningful if has_max_value is true.
float64 max_value

# True if min_value is defined and should be enforced or validated.
bool has_min_value

# True if max_value is defined and should be enforced or validated.
bool has_max_value

# ============================================================================
# Type constants: semantic type identifiers (embedded in v0 ABI)
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
# Direction constants: state flow direction identifiers (embedded in v0 ABI)
# ============================================================================

uint8 DIR_OUT=0
uint8 DIR_IN=1
uint8 DIR_INOUT=2
