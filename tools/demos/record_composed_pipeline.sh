#!/usr/bin/env bash
# Deterministic walk-through of examples/composed_pipeline.py for asciinema capture.
#
# Drives the full lifecycle (configure → activate → deactivate → cleanup → shutdown)
# and inspects topics + data flow at each step.  The KEY frame is between deactivate
# and cleanup: /pipeline/* topics are still listed after deactivate, then disappear
# only after cleanup.
#
# Designed to run unattended in ≤ 60 s of wall time.

set -euo pipefail

# Stable, host-independent prompt for the recording.
export PS1='$ '

NODE_NAME="/pipeline_node"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXAMPLE="${REPO_ROOT}/examples/composed_pipeline.py"

NODE_PID=""
cleanup() {
    if [[ -n "${NODE_PID}" ]] && kill -0 "${NODE_PID}" 2>/dev/null; then
        kill -INT "${NODE_PID}" 2>/dev/null || true
        wait "${NODE_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

step() {
    echo
    echo "### $* ###"
    echo
}

run() {
    echo "\$ $*"
    "$@" || true
}

# ---------------------------------------------------------------------------
step "Launch the composed pipeline node in the background"
# Suppress node stdout/stderr in the recording so the lifecycle CLI dialogue stays readable.
python "${EXAMPLE}" >/dev/null 2>&1 &
NODE_PID=$!
# Allow rclpy + ROS graph discovery to settle.
sleep 3

# ---------------------------------------------------------------------------
step "[before configure] node is unconfigured, no /pipeline/* topics"
run ros2 lifecycle get "${NODE_NAME}"
echo "\$ ros2 topic list | grep ^/pipeline/ || echo '(no /pipeline/* topics)'"
ros2 topic list | grep '^/pipeline/' || echo '(no /pipeline/* topics)'

# ---------------------------------------------------------------------------
step "[configure] resources created, but data flow is gated"
run ros2 lifecycle set "${NODE_NAME}" configure
sleep 1
run ros2 lifecycle get "${NODE_NAME}"
echo "\$ ros2 topic list | grep ^/pipeline/"
ros2 topic list | grep '^/pipeline/' || true
echo "\$ timeout 3 ros2 topic echo /pipeline/avg   # gated → no output expected"
timeout 3 ros2 topic echo /pipeline/avg || true

# ---------------------------------------------------------------------------
step "[activate] data flows on /pipeline/avg"
run ros2 lifecycle set "${NODE_NAME}" activate
sleep 1
echo "\$ timeout 4 ros2 topic echo /pipeline/avg"
timeout 4 ros2 topic echo /pipeline/avg || true

# ---------------------------------------------------------------------------
step "[deactivate] data flow stops — but /pipeline/* topics REMAIN (deactivate ≠ cleanup)"
run ros2 lifecycle set "${NODE_NAME}" deactivate
sleep 1
echo "\$ timeout 3 ros2 topic echo /pipeline/avg   # silent again"
timeout 3 ros2 topic echo /pipeline/avg || true
echo "\$ ros2 topic list | grep ^/pipeline/         # topics STILL present"
ros2 topic list | grep '^/pipeline/' || true

# ---------------------------------------------------------------------------
step "[cleanup] resources released — /pipeline/* topics disappear"
run ros2 lifecycle set "${NODE_NAME}" cleanup
sleep 1
echo "\$ ros2 topic list | grep ^/pipeline/ || echo '(no /pipeline/* topics)'"
ros2 topic list | grep '^/pipeline/' || echo '(no /pipeline/* topics)'

# ---------------------------------------------------------------------------
step "[shutdown] clean exit"
kill -INT "${NODE_PID}" 2>/dev/null || true
wait "${NODE_PID}" 2>/dev/null || true
NODE_PID=""
echo "node stopped."
