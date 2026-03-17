"""ACI and ASTM quality-standards tolerance references for construction."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class StandardCode(str, Enum):
    ACI_318 = "ACI 318-19"
    ACI_301 = "ACI 301-20"
    ACI_117 = "ACI 117-10"
    ACI_224R = "ACI 224R-01"
    ACI_546R = "ACI 546R-14"
    ACI_562 = "ACI 562-19"
    ASTM_C150 = "ASTM C150"
    ASTM_E119 = "ASTM E119"
    ASTM_C33 = "ASTM C33"
    ASTM_C42 = "ASTM C42"
    ASTM_E514 = "ASTM E514"


@dataclass
class ToleranceSpec:
    """A single tolerance specification from a standard."""

    code: StandardCode
    section: str
    parameter: str
    nominal_value: Optional[float]
    tolerance_plus: Optional[float]
    tolerance_minus: Optional[float]
    unit: str
    description: str

    def is_within_tolerance(self, measured: float) -> bool:
        """Check whether a measurement falls within the specified tolerance."""
        if self.nominal_value is None:
            return True
        lower = self.nominal_value - (self.tolerance_minus or 0.0)
        upper = self.nominal_value + (self.tolerance_plus or 0.0)
        return lower <= measured <= upper


# ------------------------------------------------------------------
# Built-in tolerance database (real ACI/ASTM values)
# ------------------------------------------------------------------

_TOLERANCES: list[ToleranceSpec] = [
    # ACI 318-19 -- Concrete cover to reinforcement
    ToleranceSpec(
        code=StandardCode.ACI_318,
        section="Table 20.6.1.3.1",
        parameter="Concrete cover - cast against earth",
        nominal_value=75.0,
        tolerance_plus=12.0,
        tolerance_minus=12.0,
        unit="mm",
        description=(
            "Minimum concrete cover for reinforcement cast directly against "
            "and permanently in contact with ground. ACI 318-19 requires 75 mm "
            "(3 in.) with +/- 12 mm (1/2 in.) tolerance per ACI 117."
        ),
    ),
    ToleranceSpec(
        code=StandardCode.ACI_318,
        section="Table 20.6.1.3.1",
        parameter="Concrete cover - exposed to weather (#19 and larger)",
        nominal_value=50.0,
        tolerance_plus=12.0,
        tolerance_minus=12.0,
        unit="mm",
        description=(
            "Cover for #19 through #57 bars exposed to weather or in "
            "contact with ground. 50 mm (2 in.) per ACI 318-19."
        ),
    ),
    ToleranceSpec(
        code=StandardCode.ACI_318,
        section="Table 20.6.1.3.1",
        parameter="Concrete cover - not exposed (#36 and smaller)",
        nominal_value=40.0,
        tolerance_plus=10.0,
        tolerance_minus=10.0,
        unit="mm",
        description="Cover for slabs and walls not exposed to weather: 40 mm (1.5 in.).",
    ),
    # ACI 318-19 -- Compressive strength
    ToleranceSpec(
        code=StandardCode.ACI_318,
        section="Table 19.3.2.1",
        parameter="Concrete compressive strength f'c",
        nominal_value=28.0,
        tolerance_plus=None,
        tolerance_minus=3.5,
        unit="MPa",
        description=(
            "Standard specified compressive strength of concrete. "
            "No individual test (average of two cylinders) shall be more than "
            "3.5 MPa (500 psi) below f'c. ACI 318-19 Section 19.3.2."
        ),
    ),
    # ACI 301-20 -- Surface finish tolerances
    ToleranceSpec(
        code=StandardCode.ACI_301,
        section="Section 5.3.3.2",
        parameter="Surface defects (bugholes) max diameter",
        nominal_value=0.0,
        tolerance_plus=15.0,
        tolerance_minus=0.0,
        unit="mm",
        description=(
            "For formed surfaces of class B or better, bugholes shall not "
            "exceed 15 mm (5/8 in.) in any dimension (ACI 301-20)."
        ),
    ),
    ToleranceSpec(
        code=StandardCode.ACI_301,
        section="Section 5.3.4",
        parameter="Honeycombing depth limit",
        nominal_value=0.0,
        tolerance_plus=25.0,
        tolerance_minus=0.0,
        unit="mm",
        description=(
            "Honeycombing deeper than 25 mm shall be chipped out and repaired "
            "per ACI 301-20 Section 5.3.4."
        ),
    ),
    # ACI 117-10 -- Dimensional tolerances
    ToleranceSpec(
        code=StandardCode.ACI_117,
        section="Section 4.3.1",
        parameter="Column plumbness per 3 m",
        nominal_value=0.0,
        tolerance_plus=6.0,
        tolerance_minus=0.0,
        unit="mm",
        description=(
            "Columns and walls: variation from plumb shall not exceed 6 mm "
            "in any 3 m (10 ft) of length. ACI 117-10."
        ),
    ),
    ToleranceSpec(
        code=StandardCode.ACI_117,
        section="Section 4.4.1",
        parameter="Slab thickness tolerance",
        nominal_value=None,
        tolerance_plus=10.0,
        tolerance_minus=10.0,
        unit="mm",
        description=(
            "Cast-in-place slab thickness: +/- 10 mm (3/8 in.) tolerance "
            "per ACI 117-10 for slabs <= 300 mm thick."
        ),
    ),
    # ACI 224R-01 -- Crack width limits
    ToleranceSpec(
        code=StandardCode.ACI_224R,
        section="Table 4.1",
        parameter="Crack width - dry air or protective membrane",
        nominal_value=0.0,
        tolerance_plus=0.41,
        tolerance_minus=0.0,
        unit="mm",
        description=(
            "Reasonable crack width for dry air exposure or with protective "
            "membrane: 0.41 mm (0.016 in.) per ACI 224R-01 Table 4.1."
        ),
    ),
    ToleranceSpec(
        code=StandardCode.ACI_224R,
        section="Table 4.1",
        parameter="Crack width - humidity / moist air / soil",
        nominal_value=0.0,
        tolerance_plus=0.30,
        tolerance_minus=0.0,
        unit="mm",
        description=(
            "Reasonable crack width for humidity, moist air, or soil "
            "exposure: 0.30 mm (0.012 in.) per ACI 224R-01 Table 4.1."
        ),
    ),
    ToleranceSpec(
        code=StandardCode.ACI_224R,
        section="Table 4.1",
        parameter="Crack width - seawater / wetting-drying",
        nominal_value=0.0,
        tolerance_plus=0.15,
        tolerance_minus=0.0,
        unit="mm",
        description=(
            "Reasonable crack width for seawater, spray, and wetting/drying "
            "cycles: 0.15 mm (0.006 in.) per ACI 224R-01 Table 4.1."
        ),
    ),
    # ASTM C150 -- Portland cement
    ToleranceSpec(
        code=StandardCode.ASTM_C150,
        section="Table 1",
        parameter="Type I cement - MgO content",
        nominal_value=None,
        tolerance_plus=6.0,
        tolerance_minus=0.0,
        unit="%",
        description=(
            "ASTM C150 Type I portland cement: maximum MgO content 6.0%. "
            "Excess magnesia can cause unsound concrete."
        ),
    ),
    ToleranceSpec(
        code=StandardCode.ASTM_C150,
        section="Table 1",
        parameter="Type I cement - SO3 content",
        nominal_value=None,
        tolerance_plus=3.0,
        tolerance_minus=0.0,
        unit="%",
        description="ASTM C150 Type I: maximum SO3 content 3.0%.",
    ),
    # ASTM E119 -- Fire resistance
    ToleranceSpec(
        code=StandardCode.ASTM_E119,
        section="Section 8",
        parameter="1-hour fire-rated wall temperature rise",
        nominal_value=None,
        tolerance_plus=181.0,
        tolerance_minus=0.0,
        unit="deg_C",
        description=(
            "ASTM E119 endpoint: average unexposed surface temperature "
            "shall not rise more than 139 deg C (250 deg F) above initial, and "
            "no single thermocouple shall exceed 181 deg C (325 deg F) rise."
        ),
    ),
    # ASTM C33 -- Concrete aggregates
    ToleranceSpec(
        code=StandardCode.ASTM_C33,
        section="Table 2",
        parameter="Fine aggregate - passing No. 200 sieve",
        nominal_value=None,
        tolerance_plus=3.0,
        tolerance_minus=0.0,
        unit="%",
        description=(
            "ASTM C33 fine aggregate: material passing the No. 200 (75-um) "
            "sieve shall not exceed 3.0% for concrete subject to abrasion."
        ),
    ),
    ToleranceSpec(
        code=StandardCode.ASTM_C33,
        section="Table 1",
        parameter="Coarse aggregate - max flat/elongated particles",
        nominal_value=None,
        tolerance_plus=10.0,
        tolerance_minus=0.0,
        unit="%",
        description=(
            "Flat and elongated particles (5:1 ratio) shall not exceed 10% "
            "by mass for structural concrete per ASTM C33 supplementary "
            "requirements."
        ),
    ),
]


@dataclass
class QualityStandards:
    """Reference database for ACI and ASTM construction tolerances.

    Provides look-up by standard code, parameter name, and compliance
    checking against measured values.
    """

    _specs: list[ToleranceSpec] = field(default_factory=lambda: list(_TOLERANCES))

    def by_code(self, code: StandardCode) -> list[ToleranceSpec]:
        """Return all tolerance specs for a given standard code."""
        return [s for s in self._specs if s.code == code]

    def by_parameter(self, keyword: str) -> list[ToleranceSpec]:
        """Search tolerances whose parameter or description contains *keyword*."""
        kw = keyword.lower()
        return [
            s for s in self._specs
            if kw in s.parameter.lower() or kw in s.description.lower()
        ]

    def check_compliance(
        self, code: StandardCode, parameter: str, measured: float
    ) -> Optional[tuple[bool, ToleranceSpec]]:
        """Check a measurement against the first matching spec.

        Returns
        -------
        (bool, ToleranceSpec) or None if no matching spec found.
        """
        for s in self._specs:
            if s.code == code and parameter.lower() in s.parameter.lower():
                return (s.is_within_tolerance(measured), s)
        return None

    def all_specs(self) -> list[ToleranceSpec]:
        return list(self._specs)

    def summary(self) -> dict[str, int]:
        """Return count of specs per standard code."""
        counts: dict[str, int] = {}
        for s in self._specs:
            counts[s.code.value] = counts.get(s.code.value, 0) + 1
        return counts
