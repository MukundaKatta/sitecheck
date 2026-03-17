"""Tests for the inspector modules: checklist, report_gen, photo."""

import pytest

from sitecheck.models import (
    DefectFinding,
    DefectType,
    Inspection,
    InspectionStatus,
    SeverityLevel,
    Trade,
)
from sitecheck.inspector.checklist import (
    InspectionChecklist,
    CheckResult,
    TRADE_CHECKLISTS,
)
from sitecheck.inspector.report_gen import InspectionReportGenerator
from sitecheck.inspector.photo import PhotoDocumentor


class TestInspectionChecklist:
    @pytest.mark.parametrize("trade", list(Trade))
    def test_for_trade(self, trade):
        cl = InspectionChecklist.for_trade(trade)
        assert cl.total_items > 0
        assert cl.trade == trade

    def test_check_pass(self):
        cl = InspectionChecklist.for_trade(Trade.CONCRETE)
        first_id = cl.items[0].id
        cl.check(first_id, CheckResult.PASS, notes="OK")
        assert cl.passed_items == 1
        assert cl.checked_items == 1

    def test_check_fail(self):
        cl = InspectionChecklist.for_trade(Trade.STEEL)
        first_id = cl.items[0].id
        cl.check(first_id, CheckResult.FAIL, notes="Out of tolerance")
        assert cl.failed_items == 1

    def test_check_unknown_raises(self):
        cl = InspectionChecklist.for_trade(Trade.CONCRETE)
        with pytest.raises(KeyError):
            cl.check("DOES_NOT_EXIST", CheckResult.PASS)

    def test_completion(self):
        cl = InspectionChecklist.for_trade(Trade.WOOD)
        for item in cl.items:
            cl.check(item.id, CheckResult.PASS)
        assert cl.is_complete is True
        assert cl.completion_pct == 100.0

    def test_failures(self):
        cl = InspectionChecklist.for_trade(Trade.ELECTRICAL)
        cl.check(cl.items[0].id, CheckResult.FAIL)
        cl.check(cl.items[1].id, CheckResult.PASS)
        assert len(cl.failures()) == 1


class TestInspectionReportGenerator:
    def test_generate_report(self):
        findings = [
            DefectFinding(
                id="F-001", defect_type=DefectType.CRACKING,
                severity=SeverityLevel.MAJOR, confidence=0.9,
                location="Column A1", remediation="Epoxy injection",
            ),
            DefectFinding(
                id="F-002", defect_type=DefectType.HONEYCOMBING,
                severity=SeverityLevel.MINOR, confidence=0.8,
                location="Wall B2",
            ),
        ]
        inspection = Inspection(
            id="INS-001", project_name="Test", inspector="Smith",
            trade=Trade.CONCRETE, status=InspectionStatus.COMPLETED,
            findings=findings,
        )
        gen = InspectionReportGenerator(project_name="Test", inspector="Smith")
        report = gen.generate(inspection)

        assert report.total_findings > 0
        assert report.quality_score is not None
        assert len(report.recommendations) > 0

    def test_report_with_checklist(self):
        inspection = Inspection(
            id="INS-002", project_name="Test", inspector="Smith",
            trade=Trade.CONCRETE, status=InspectionStatus.COMPLETED,
        )
        cl = InspectionChecklist.for_trade(Trade.CONCRETE)
        gen = InspectionReportGenerator()
        report = gen.generate(inspection, checklist=cl)
        section_titles = [s.title for s in report.sections]
        assert "Checklist Summary" in section_titles


class TestPhotoDocumentor:
    def test_add_photo(self):
        doc = PhotoDocumentor(project_name="Test")
        photo = doc.add_photo(
            "IMG_001.jpg",
            location="Column A1",
            defect_type=DefectType.CRACKING,
            severity=SeverityLevel.MAJOR,
        )
        assert photo.photo_id == "PHT-0001"
        assert doc.total_photos == 1

    def test_by_defect_type(self):
        doc = PhotoDocumentor()
        doc.add_photo("a.jpg", defect_type=DefectType.CRACKING)
        doc.add_photo("b.jpg", defect_type=DefectType.HONEYCOMBING)
        doc.add_photo("c.jpg", defect_type=DefectType.CRACKING)
        assert len(doc.by_defect_type(DefectType.CRACKING)) == 2

    def test_by_finding(self):
        doc = PhotoDocumentor()
        doc.add_photo("a.jpg", finding_id="F-001")
        doc.add_photo("b.jpg", finding_id="F-001")
        doc.add_photo("c.jpg", finding_id="F-002")
        assert len(doc.by_finding("F-001")) == 2

    def test_directory_structure(self):
        doc = PhotoDocumentor()
        doc.add_photo(
            "a.jpg",
            defect_type=DefectType.CRACKING,
            severity=SeverityLevel.MAJOR,
        )
        structure = doc.generate_directory_structure()
        assert "photos/cracking/major" in structure
        assert "a.jpg" in structure["photos/cracking/major"]

    def test_summary(self):
        doc = PhotoDocumentor()
        doc.add_photo("a.jpg", defect_type=DefectType.CRACKING)
        doc.add_photo("b.jpg", defect_type=DefectType.CRACKING)
        doc.add_photo("c.jpg")
        s = doc.summary()
        assert s["cracking"] == 2
        assert s["unclassified"] == 1
