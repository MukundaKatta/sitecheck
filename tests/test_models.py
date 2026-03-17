"""Tests for SiteCheck pydantic models."""

import pytest
from sitecheck.models import (
    DefectFinding,
    DefectType,
    Inspection,
    InspectionStatus,
    QualityScore,
    SeverityLevel,
    Trade,
)


class TestDefectFinding:
    def test_create(self):
        f = DefectFinding(
            id="F-001",
            defect_type=DefectType.CRACKING,
            severity=SeverityLevel.MINOR,
            confidence=0.85,
            location="Column A1",
        )
        assert f.id == "F-001"
        assert f.is_actionable() is True

    def test_cosmetic_not_actionable(self):
        f = DefectFinding(
            id="F-002",
            defect_type=DefectType.CRACKING,
            severity=SeverityLevel.COSMETIC,
            confidence=0.9,
            location="Wall B2",
        )
        assert f.is_actionable() is False


class TestInspection:
    def test_counts(self):
        findings = [
            DefectFinding(
                id="F-001", defect_type=DefectType.CRACKING,
                severity=SeverityLevel.CRITICAL, confidence=0.9, location="A",
            ),
            DefectFinding(
                id="F-002", defect_type=DefectType.HONEYCOMBING,
                severity=SeverityLevel.MINOR, confidence=0.8, location="B",
            ),
        ]
        insp = Inspection(
            id="INS-001", project_name="Test", inspector="X", trade=Trade.CONCRETE,
            findings=findings,
        )
        assert insp.defect_count == 2
        assert insp.critical_count == 1

    def test_pass_rate_no_findings(self):
        insp = Inspection(
            id="INS-002", project_name="Test", inspector="X", trade=Trade.STEEL,
        )
        assert insp.pass_rate == 1.0


class TestQualityScore:
    def test_compute_perfect(self):
        insp = Inspection(
            id="INS-001", project_name="Test", inspector="X", trade=Trade.CONCRETE,
        )
        qs = QualityScore.compute("Test", [insp])
        assert qs.score == 100.0
        assert qs.grade == "A"

    def test_compute_with_critical(self):
        findings = [
            DefectFinding(
                id="F-001", defect_type=DefectType.REBAR_EXPOSURE,
                severity=SeverityLevel.CRITICAL, confidence=0.95, location="C3",
            ),
        ]
        insp = Inspection(
            id="INS-003", project_name="Test", inspector="X", trade=Trade.CONCRETE,
            findings=findings,
        )
        qs = QualityScore.compute("Test", [insp])
        assert qs.score < 100.0
        assert qs.critical_defects == 1
