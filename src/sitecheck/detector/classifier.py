"""Defect severity classification and grading."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from sitecheck.models import DefectType, SeverityLevel, DefectFinding


# Severity thresholds by defect type.
# Each entry maps (defect_type) -> list of (max_dimension_mm, severity).
# The first matching threshold (where the measured value <= max) applies.
SEVERITY_THRESHOLDS: dict[DefectType, list[tuple[float, SeverityLevel]]] = {
    DefectType.CRACKING: [
        # ACI 224R-01 guidance on crack width tolerances
        (0.1, SeverityLevel.COSMETIC),    # hairline: < 0.1 mm
        (0.3, SeverityLevel.MINOR),       # 0.1 - 0.3 mm (dry exposure)
        (1.0, SeverityLevel.MAJOR),       # 0.3 - 1.0 mm
        (float("inf"), SeverityLevel.CRITICAL),  # > 1.0 mm structural concern
    ],
    DefectType.MISALIGNMENT: [
        # ACI 117-10 tolerances for cast-in-place concrete
        (6.0, SeverityLevel.COSMETIC),     # <= 6 mm offset
        (12.0, SeverityLevel.MINOR),       # 6 - 12 mm
        (25.0, SeverityLevel.MAJOR),       # 12 - 25 mm
        (float("inf"), SeverityLevel.CRITICAL),
    ],
    DefectType.WATER_DAMAGE: [
        # Area of discoloration / staining in mm^2 (simplified)
        (500.0, SeverityLevel.COSMETIC),
        (5000.0, SeverityLevel.MINOR),
        (25000.0, SeverityLevel.MAJOR),
        (float("inf"), SeverityLevel.CRITICAL),
    ],
    DefectType.REBAR_EXPOSURE: [
        # Exposed rebar length in mm
        (0.0, SeverityLevel.CRITICAL),  # any rebar exposure is at least major
    ],
    DefectType.HONEYCOMBING: [
        # Depth of honeycombing in mm
        (5.0, SeverityLevel.COSMETIC),   # surface bugholes
        (15.0, SeverityLevel.MINOR),
        (40.0, SeverityLevel.MAJOR),
        (float("inf"), SeverityLevel.CRITICAL),
    ],
}

# Remediation recommendations by (defect_type, severity)
REMEDIATION: dict[tuple[DefectType, SeverityLevel], str] = {
    (DefectType.CRACKING, SeverityLevel.COSMETIC): "Monitor; no repair needed.",
    (DefectType.CRACKING, SeverityLevel.MINOR): "Seal with epoxy injection per ACI 224.1R.",
    (DefectType.CRACKING, SeverityLevel.MAJOR): (
        "Epoxy injection and structural review per ACI 318-19 Ch. 26."
    ),
    (DefectType.CRACKING, SeverityLevel.CRITICAL): (
        "Immediate structural assessment; possible member reinforcement per ACI 562."
    ),
    (DefectType.MISALIGNMENT, SeverityLevel.COSMETIC): "Acceptable per ACI 117-10.",
    (DefectType.MISALIGNMENT, SeverityLevel.MINOR): "Grind or patch to restore alignment.",
    (DefectType.MISALIGNMENT, SeverityLevel.MAJOR): "Demolish and reconstruct affected section.",
    (DefectType.MISALIGNMENT, SeverityLevel.CRITICAL): "Stop work; structural review required.",
    (DefectType.WATER_DAMAGE, SeverityLevel.COSMETIC): "Clean and apply sealer.",
    (DefectType.WATER_DAMAGE, SeverityLevel.MINOR): (
        "Identify moisture source; apply waterproof membrane."
    ),
    (DefectType.WATER_DAMAGE, SeverityLevel.MAJOR): (
        "Major waterproofing repair; check reinforcement for corrosion."
    ),
    (DefectType.WATER_DAMAGE, SeverityLevel.CRITICAL): (
        "Structural assessment for corrosion-induced section loss."
    ),
    (DefectType.REBAR_EXPOSURE, SeverityLevel.CRITICAL): (
        "Cover exposed rebar immediately; patch with repair mortar per ACI 546R. "
        "Verify cover depth per ACI 318-19 Table 20.6.1.3.1."
    ),
    (DefectType.REBAR_EXPOSURE, SeverityLevel.MAJOR): (
        "Restore concrete cover; verify reinforcement is not corroded."
    ),
    (DefectType.HONEYCOMBING, SeverityLevel.COSMETIC): "Fill bugholes with grout.",
    (DefectType.HONEYCOMBING, SeverityLevel.MINOR): "Remove loose aggregate; patch with repair mortar.",
    (DefectType.HONEYCOMBING, SeverityLevel.MAJOR): (
        "Core test for compressive strength per ASTM C42; repair per ACI 546R."
    ),
    (DefectType.HONEYCOMBING, SeverityLevel.CRITICAL): (
        "Structural review; possible demolition and replacement."
    ),
}


@dataclass
class DefectClassifier:
    """Assigns a severity grade to a defect based on measured dimensions
    and ACI/ASTM references.
    """

    custom_thresholds: Optional[dict[DefectType, list[tuple[float, SeverityLevel]]]] = None

    def __post_init__(self) -> None:
        self._thresholds = dict(SEVERITY_THRESHOLDS)
        if self.custom_thresholds:
            self._thresholds.update(self.custom_thresholds)

    def classify(
        self,
        defect_type: DefectType,
        measurement_mm: float,
    ) -> SeverityLevel:
        """Classify the severity of a defect given its primary measurement.

        Parameters
        ----------
        defect_type : DefectType
        measurement_mm : float
            The critical dimension in millimetres (crack width, offset, etc.).

        Returns
        -------
        SeverityLevel
        """
        thresholds = self._thresholds.get(defect_type, [])

        # Rebar exposure is always at least MAJOR
        if defect_type == DefectType.REBAR_EXPOSURE:
            if measurement_mm > 50:
                return SeverityLevel.CRITICAL
            return SeverityLevel.MAJOR

        for max_val, severity in thresholds:
            if measurement_mm <= max_val:
                return severity

        return SeverityLevel.CRITICAL

    def classify_finding(
        self,
        defect_type: DefectType,
        measurement_mm: float,
        location: str = "",
        finding_id: str = "F-001",
    ) -> DefectFinding:
        """Classify and return a full :class:`DefectFinding`."""
        severity = self.classify(defect_type, measurement_mm)
        remediation = REMEDIATION.get((defect_type, severity), "Consult structural engineer.")
        standard_ref = self._standard_reference(defect_type, severity)

        return DefectFinding(
            id=finding_id,
            defect_type=defect_type,
            severity=severity,
            confidence=1.0,
            location=location,
            description=f"{defect_type.value} ({measurement_mm:.2f} mm)",
            dimensions_mm={"primary": measurement_mm},
            standard_reference=standard_ref,
            remediation=remediation,
        )

    @staticmethod
    def _standard_reference(defect_type: DefectType, severity: SeverityLevel) -> str:
        """Return the most relevant ACI/ASTM reference for a given defect."""
        refs: dict[DefectType, str] = {
            DefectType.CRACKING: "ACI 224R-01 / ACI 318-19 Table 24.3.2",
            DefectType.MISALIGNMENT: "ACI 117-10 Section 4",
            DefectType.WATER_DAMAGE: "ACI 515.2R / ASTM E514",
            DefectType.REBAR_EXPOSURE: "ACI 318-19 Table 20.6.1.3.1",
            DefectType.HONEYCOMBING: "ACI 301-20 Section 5.3 / ASTM C42",
        }
        return refs.get(defect_type, "Consult applicable code")
