from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HealthLevel(Enum):
    """Severity levels for component health, ordered from least to most severe."""

    UNKNOWN = "unknown"
    OK = "ok"
    DEGRADED = "degraded"
    ERROR = "error"


# Ordering used for worst-of aggregation: UNKNOWN=0 < OK=1 < DEGRADED=2 < ERROR=3
_HEALTH_SEVERITY: dict[HealthLevel, int] = {
    HealthLevel.UNKNOWN: 0,
    HealthLevel.OK: 1,
    HealthLevel.DEGRADED: 2,
    HealthLevel.ERROR: 3,
}


def _worst_health(a: HealthStatus, b: HealthStatus) -> HealthStatus:
    """Return the more severe of two HealthStatus values."""
    if _HEALTH_SEVERITY[b.level] > _HEALTH_SEVERITY[a.level]:
        return b
    return a


@dataclass(frozen=True)
class HealthStatus:
    """Immutable health snapshot for a lifecycle component."""

    level: HealthLevel
    reason: str
    last_error: str | None = None


#: Sentinel returned before any transition has occurred.
HEALTH_UNKNOWN: HealthStatus = HealthStatus(level=HealthLevel.UNKNOWN, reason="")
