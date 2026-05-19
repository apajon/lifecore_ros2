# StateDescription defines a versioned collection of StateDescriptor entries.
#
# It represents a coherent schema/scope description. It is not one descriptor,
# runtime state, a state value, or a command. A consumer receives StateDescription
# to learn the schema and constraints for a related stream of StateSample and
# StateCommand messages.
#
# Fields are organized logically for readability (schema metadata, not high-frequency transport).

# Transport header carries the description publication event metadata.
std_msgs/Header header

# ============================================================================
# Schema and versioning group: identity and versioning of this description
# ============================================================================

# Stable identifier for the schema/scope.
# Identifies which state domain or registry scope this description covers.
unique_identifier_msgs/UUID schema_uuid

# Version number for this description.
# Increments when the descriptor set or descriptor meaning changes.
# Allows consumers to detect schema incompatibility and stale cached metadata.
uint64 description_version

# ============================================================================
# Descriptors group: collection of state field contracts
# ============================================================================

# Coherent collection of StateDescriptor entries.
# Each descriptor defines one state field or stream within this schema.
# The descriptors array is the primary payload and must not be empty
# when a valid StateDescription is published.
StateDescriptor[] descriptors
