from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass

from rclpy.lifecycle import TransitionCallbackReturn
from rclpy.lifecycle.node import LifecycleState


@dataclass(slots=True)
class TransitionThreadResult:
    """Result container returned by ``spawn_transition_thread``."""

    transition_name: str
    thread: threading.Thread
    result: TransitionCallbackReturn | None = None
    exception: BaseException | None = None

    def join(self, timeout: float | None = None) -> TransitionCallbackReturn:
        """Join the thread and re-raise any exception captured from the transition."""
        self.thread.join(timeout)
        if self.thread.is_alive():
            raise TimeoutError(f"Transition thread '{self.transition_name}' did not finish")
        if self.exception is not None:
            raise self.exception
        if self.result is None:
            raise RuntimeError(f"Transition thread '{self.transition_name}' finished without a result")
        return self.result


def spawn_transition_thread(node: object, transition_name: str) -> TransitionThreadResult:
    """Start a thread that calls ``trigger_<transition_name>`` on a lifecycle node-like object."""
    trigger_name = f"trigger_{transition_name}"
    trigger = getattr(node, trigger_name, None)
    if not callable(trigger):
        raise ValueError(f"Unknown lifecycle transition '{transition_name}'")

    result = TransitionThreadResult(
        transition_name=transition_name,
        thread=threading.Thread(name=f"lifecore-{transition_name}-transition", target=lambda: None),
    )

    def run_transition() -> None:
        try:
            result.result = trigger()
        except BaseException as exc:
            result.exception = exc

    result.thread = threading.Thread(name=f"lifecore-{transition_name}-transition", target=run_transition)
    result.thread.start()
    return result


def assert_no_race(test_fn: Callable[[], None], *, attempts: int = 20) -> None:
    """Run a deterministic race probe repeatedly."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    for _attempt in range(attempts):
        test_fn()


def barrier_hook(
    barrier: threading.Barrier,
    *,
    result: TransitionCallbackReturn = TransitionCallbackReturn.SUCCESS,
) -> Callable[[LifecycleState], TransitionCallbackReturn]:
    """Create a lifecycle hook that blocks on ``barrier`` before returning ``result``."""

    def hook(state: LifecycleState) -> TransitionCallbackReturn:
        barrier.wait()
        return result

    return hook
