"""Construction defect simulation engine for testing and demos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from sitecheck.models import (
    DefectFinding,
    DefectType,
    Inspection,
    InspectionStatus,
    SeverityLevel,
    Trade,
)
from sitecheck.detector.classifier import DefectClassifier


# Probability distribution of defect types on a typical concrete site
DEFECT_DISTRIBUTION: dict[DefectType, float] = {
    DefectType.CRACKING: 0.35,
    DefectType.HONEYCOMBING: 0.25,
    DefectType.MISALIGNMENT: 0.15,
    DefectType.WATER_DAMAGE: 0.15,
    DefectType.REBAR_EXPOSURE: 0.10,
}

# Measurement ranges (mm) for generating realistic dimensions per defect type
MEASUREMENT_RANGES: dict[DefectType, tuple[float, float]] = {
    DefectType.CRACKING: (0.05, 2.0),       # crack width in mm
    DefectType.MISALIGNMENT: (2.0, 40.0),    # offset in mm
    DefectType.WATER_DAMAGE: (100.0, 50000.0),  # stain area in mm^2
    DefectType.REBAR_EXPOSURE: (10.0, 200.0),   # exposed length in mm
    DefectType.HONEYCOMBING: (2.0, 60.0),    # depth in mm
}

LOCATIONS: list[str] = [
    "Column A1, Level 1",
    "Column B3, Level 2",
    "Beam C2-C3, Level 3",
    "Slab Panel D4, Level 2",
    "Wall Grid E, Level 1",
    "Foundation Footing F2",
    "Shear Wall G1, Level 1",
    "Column H5, Level 4",
    "Beam J2-J3, Level 2",
    "Slab Panel K1, Roof",
    "Retaining Wall, North Side",
    "Stairwell S1, Level 2-3",
]


@dataclass
class DefectSimulator:
    """Generates synthetic construction defect data for testing.

    Parameters
    ----------
    random_seed : int | None
        Seed for reproducibility.
    """

    random_seed: Optional[int] = 42
    _rng: np.random.Generator = field(init=False, repr=False)
    _classifier: DefectClassifier = field(init=False, repr=False)
    _finding_counter: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        self._rng = np.random.default_rng(self.random_seed)
        self._classifier = DefectClassifier()

    def generate_finding(self) -> DefectFinding:
        """Generate a single random defect finding."""
        self._finding_counter += 1

        # Pick defect type from distribution
        types = list(DEFECT_DISTRIBUTION.keys())
        probs = list(DEFECT_DISTRIBUTION.values())
        defect_type = self._rng.choice(types, p=probs)

        # Generate measurement
        lo, hi = MEASUREMENT_RANGES[defect_type]
        measurement = float(self._rng.uniform(lo, hi))

        # Pick location
        location = self._rng.choice(LOCATIONS)

        # Classify
        finding = self._classifier.classify_finding(
            defect_type=defect_type,
            measurement_mm=measurement,
            location=location,
            finding_id=f"F-{self._finding_counter:04d}",
        )

        # Simulate a detection confidence
        finding.confidence = float(self._rng.uniform(0.6, 0.99))

        return finding

    def generate_findings(self, count: int = 10) -> list[DefectFinding]:
        """Generate multiple defect findings."""
        return [self.generate_finding() for _ in range(count)]

    def generate_inspection(
        self,
        trade: Trade = Trade.CONCRETE,
        defect_count: int = 5,
        project_name: str = "Sample Project",
        inspector: str = "J. Smith",
    ) -> Inspection:
        """Generate a complete inspection with synthetic defects."""
        findings = self.generate_findings(defect_count)
        return Inspection(
            id=f"INS-{self._rng.integers(1000, 9999)}",
            project_name=project_name,
            inspector=inspector,
            trade=trade,
            status=InspectionStatus.COMPLETED,
            findings=findings,
            checklist_completed=True,
        )
