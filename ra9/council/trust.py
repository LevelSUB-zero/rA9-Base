from __future__ import annotations

from typing import Dict, Tuple


class TrustService:
    def __init__(self) -> None:
        # councilId -> axis -> (alpha, beta)
        self._council_axis_beta: Dict[str, Dict[str, Tuple[float, float]]] = {}
        # workerId -> trust
        self._worker_trust: Dict[str, float] = {}

    def get_council_axis_trust(self) -> Dict[str, Dict[str, float]]:
        trust: Dict[str, Dict[str, float]] = {}
        for council, axis_map in self._council_axis_beta.items():
            trust[council] = {}
            for axis, (a, b) in axis_map.items():
                denom = a + b
                trust[council][axis] = (a / denom) if denom > 0 else 0.5
        return trust

    def get_worker_trust(self) -> Dict[str, float]:
        return dict(self._worker_trust)

    def update_council_axis(self, council_id: str, axis: str, correct: bool, decay: float = 1.0) -> None:
        axis_map = self._council_axis_beta.setdefault(council_id, {})
        a, b = axis_map.get(axis, (1.0, 1.0))
        a *= decay
        b *= decay
        if correct:
            a += 1.0
        else:
            b += 1.0
        axis_map[axis] = (a, b)

    def set_worker_trust(self, worker_id: str, value: float) -> None:
        self._worker_trust[worker_id] = value

    def ema_worker_update(self, worker_id: str, success_signal: float, gamma: float = 0.05) -> None:
        old = self._worker_trust.get(worker_id, 1.0)
        new = gamma * success_signal + (1.0 - gamma) * old
        self._worker_trust[worker_id] = new


