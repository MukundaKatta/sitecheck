"""Pydantic data models for SiteCheck."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DefectType(str, Enum):
    CRACKING = "cracking"
    MISALIGNMENT = "misalignment"
    WATER_DAMAGE = "water_damage"
    REBAR_EXPOSURE = "rebar_exposure"
    HONEYCOMBING = "honeycombing"


class SeverityLevel(str, Enum):
    COSMETIC = "cosmetic"      # Aesthetic only, no structural concern
    MINOR = "minor"            # Requires monitoring or minor repair
    MAJOR = "major"            # Requires prompt repair
    CRITICAL = "critical"      # Safety hazard, requires immediate action


class Trade(str, Enum):
    CONCRETE = "concrete"
    MASONRY = "masonry"
    STEEL = "steel"
    WOOD = "wood"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"


class InspectionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DefectFinding(BaseModel):
    """A single defect identified during inspection."""

    id: str = Field(..., description="Unique finding identifier")
    defect_type: DefectType
    severity: SeverityLevel
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    location: str = Field(..., description="Location on site, e.g. 'Column C3, Level 2'")
    description: str = Field(default="")
    dimensions_mm: Optional[dict[str, float]] = Field(
        default=None,
        description="Measured dimensions, e.g. {'width': 0.3, 'length': 150}",
    )
    photo_ids: list[str] = Field(default_factory=list)
    standard_reference: Optional[str] = Field(
        default=None,
        description="Applicable standard, e.g. 'ACI 318-19 Table 19.3.2.1'",
    )
    remediation: Optional[str] = Field(
        default=None,
        description="Recommended repair action",
    )
    timestamp: datetime = Field(default_factory=datetime.now)

    def is_actionable(self) -> bool:
        """True if the defect requires repair (not just cosmetic)."""
        return self.severity in (SeverityLevel.MINOR, SeverityLevel.MAJOR, SeverityLevel.CRITICAL)


class Inspection(BaseModel):
    """A complete site inspection record."""

    id: str = Field(..., description="Inspection ID")
    project_name: str
    inspector: str
    trade: Trade
    date: datetime = Field(default_factory=datetime.now)
    status: InspectionStatus = Field(default=InspectionStatus.PENDING)
    findings: list[DefectFinding] = Field(default_factory=list)
    notes: str = Field(default="")
    checklist_completed: bool = Field(default=False)

    @property
    def defect_count(self) -> int:
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == SeverityLevel.CRITICAL)

    @property
    def pass_rate(self) -> float:
        """Fraction of findings that are cosmetic (pass)."""
        if not self.findings:
            return 1.0
        cosmetic = sum(1 for f in self.findings if f.severity == SeverityLevel.COSMETIC)
        return cosmetic / len(self.findings)


class QualityScore(BaseModel):
    """Overall quality assessment for a project or section."""

    project_name: str
    section: str = Field(default="Overall")
    score: float = Field(..., ge=0.0, le=100.0, description="Quality score 0-100")
    grade: str = Field(..., description="Letter grade: A, B, C, D, F")
    total_inspections: int = Field(default=0)
    total_defects: int = Field(default=0)
    critical_defects: int = Field(default=0)
    compliance_pct: float = Field(
        default=100.0,
        ge=0.0, le=100.0,
        description="Percentage of items meeting standards",
    )
    timestamp: datetime = Field(default_factory=datetime.now)

    @classmethod
    def compute(
        cls,
        project_name: str,
        inspections: list[Inspection],
        section: str = "Overall",
    ) -> "QualityScore":
        """Compute a quality score from a list of inspections."""
        total_defects = sum(i.defect_count for i in inspections)
        critical = sum(i.critical_count for i in inspections)

        # Score: start at 100, deduct for defects
        score = 100.0
        score -= critical * 15.0
        major = sum(
            1 for i in inspections
            for f in i.findings if f.severity == SeverityLevel.MAJOR
        )
        score -= major * 8.0
        minor = sum(
            1 for i in inspections
            for f in i.findings if f.severity == SeverityLevel.MINOR
        )
        score -= minor * 3.0
        score = max(score, 0.0)

        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        total_items = max(total_defects, 1)
        cosmetic = sum(
            1 for i in inspections
            for f in i.findings if f.severity == SeverityLevel.COSMETIC
        )
        compliance_pct = (cosmetic / total_items) * 100 if total_defects > 0 else 100.0

        return cls(
            project_name=project_name,
            section=section,
            score=round(score, 1),
            grade=grade,
            total_inspections=len(inspections),
            total_defects=total_defects,
            critical_defects=critical,
            compliance_pct=round(compliance_pct, 1),
        )
