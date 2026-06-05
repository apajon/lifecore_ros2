# StateUpdate represents a published batch of observed StateSample values.
#
# It reports observed truth. It does not express requested mutation,
# and it is not a command or descriptor list.
#
# header.stamp is the publish/batch timestamp — the time when this update
# was assembled and sent. Each contained StateSample.header.stamp is the
# source observation timestamp. These timestamps may differ.

# Transport header carries publish/batch timestamp metadata.
std_msgs/Header header

# ============================================================================
# Source and schema identity group
# ============================================================================

# Stable identity of the source, owner, or publisher scope for this update.
# Used to correlate updates with a specific state producer or registry scope.
unique_identifier_msgs/UUID source_uuid

# Identity of the schema or StateDescription used to interpret the samples.
# Must match StateDescription.schema_uuid for the description version declared below.
unique_identifier_msgs/UUID schema_uuid

# ============================================================================
# Ordering and versioning group
# ============================================================================

# Monotonically increasing sequence number per source_uuid stream.
# Used to detect lost, duplicated, out-of-order, or discontinuous updates.
uint64 sequence

# StateDescription version used to interpret descriptor ids, types, and semantics.
# Must match StateDescription.description_version for the declared schema_uuid.
# Receivers must not blindly apply updates against a different description version.
uint64 description_version

# ============================================================================
# Update mode group
# ============================================================================

# Declares whether this update is a full snapshot or a partial delta.
uint8 update_mode

# ============================================================================
# Payload group: array of observed StateSample values
# ============================================================================

# Batch of observed state values. Each sample carries its own source timestamp.
# For UPDATE_FULL, samples represent a complete snapshot for the publisher scope.
# For UPDATE_DELTA, samples represent only changed values since the prior update.
StateSample[] samples

# ============================================================================
# Update mode constants
# ============================================================================

uint8 UPDATE_UNKNOWN=0
uint8 UPDATE_FULL=1
uint8 UPDATE_DELTA=2
