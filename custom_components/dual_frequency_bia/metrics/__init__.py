"""DAG-based body composition metrics handler.

Manages dependency graph between metrics, recalculates in topological order
when inputs change, and notifies subscribed sensor entities.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from ..models import Metric, UserProfile
from .body_composition import calculate_all

_LOGGER = logging.getLogger(__name__)

# Dependency graph: metric -> set of metrics it depends on.
# "input" dependencies are weight, impedance_high, impedance_low, heart_rate.
DEPENDENCIES: dict[Metric, set[str]] = {
    Metric.WEIGHT: {"weight"},
    Metric.BMI: {"weight"},
    Metric.IDEAL_WEIGHT: set(),  # only needs profile (height, gender)
    Metric.BASAL_METABOLISM: {"weight"},
    Metric.TOTAL_BODY_WATER: {"weight", "impedance_high"},
    Metric.EXTRACELLULAR_WATER: {"weight", "impedance_low"},
    Metric.INTRACELLULAR_WATER: {"weight", "impedance_high", "impedance_low"},
    Metric.FAT_FREE_MASS: {"weight", "impedance_high"},
    Metric.BODY_FAT: {"weight", "impedance_high"},
    Metric.LEAN_BODY_MASS: {"weight", "impedance_high"},
    Metric.WATER_PERCENTAGE: {"weight", "impedance_high"},
    Metric.BONE_MASS: {"weight"},
    Metric.VISCERAL_FAT: {"weight"},
    Metric.MUSCLE_MASS: {"weight", "impedance_high"},
    Metric.METABOLIC_AGE: {"weight"},
    Metric.PROTEIN: {"weight", "impedance_high"},
    Metric.BODY_SCORE: {"weight", "impedance_high", "impedance_low"},
    Metric.ECW_TBW_RATIO: {"weight", "impedance_high", "impedance_low"},
    Metric.ECW_TBW_STATUS: {"weight", "impedance_high", "impedance_low"},
    Metric.HEART_RATE: {"heart_rate"},
}

# All required inputs for a full calculation
REQUIRED_INPUTS = {"weight", "impedance_high", "impedance_low"}


class BodyCompositionMetricsHandler:
    """Coordinates metric calculation and notifies subscribers."""

    def __init__(self, profile: UserProfile) -> None:
        """Initialize with user profile."""
        self._profile = profile
        self._inputs: dict[str, float | None] = {
            "weight": None,
            "impedance_high": None,
            "impedance_low": None,
            "heart_rate": None,
        }
        self._results: dict[str, Any] = {}
        self._subscribers: dict[Metric, list[Callable[[], None]]] = {
            m: [] for m in Metric
        }

    @property
    def profile(self) -> UserProfile:
        """Return the user profile."""
        return self._profile

    @property
    def results(self) -> dict[str, Any]:
        """Return current metric results."""
        return self._results

    def subscribe(self, metric: Metric, callback: Callable[[], None]) -> None:
        """Subscribe to updates for a specific metric."""
        self._subscribers[metric].append(callback)

    def update_input(self, key: str, value: float | None) -> None:
        """Update an input value. Does not trigger recalculation."""
        if key in self._inputs:
            self._inputs[key] = value

    def has_required_inputs(self) -> bool:
        """Check if all required inputs are available."""
        return all(self._inputs[k] is not None for k in REQUIRED_INPUTS)

    def recalculate(self) -> None:
        """Recalculate all metrics and notify subscribers.

        Only runs if all required inputs (weight, impedance_high, impedance_low)
        are available.
        """
        if not self.has_required_inputs():
            _LOGGER.debug(
                "Skipping recalculation for %s: missing required inputs",
                self._profile.name,
            )
            return

        weight = self._inputs["weight"]
        impedance_high = self._inputs["impedance_high"]
        impedance_low = self._inputs["impedance_low"]
        heart_rate = self._inputs["heart_rate"]

        assert weight is not None
        assert impedance_high is not None
        assert impedance_low is not None

        self._results = calculate_all(
            profile=self._profile,
            weight=weight,
            impedance_high=impedance_high,
            impedance_low=impedance_low,
            heart_rate=heart_rate,
        )

        _LOGGER.debug(
            "Recalculated metrics for %s: weight=%.1f, impedance_high=%.0f, "
            "impedance_low=%.0f, body_fat=%.1f%%, tbw=%.2fL",
            self._profile.name,
            weight,
            impedance_high,
            impedance_low,
            self._results.get("body_fat", 0),
            self._results.get("total_body_water", 0),
        )

        # Notify all subscribers
        for metric in Metric:
            metric_key = metric.value
            if metric_key in self._results and self._results[metric_key] is not None:
                for callback in self._subscribers[metric]:
                    callback()

    def get_value(self, metric: Metric) -> Any:
        """Get the current value of a metric."""
        return self._results.get(metric.value)
