"""Tests for the defect simulator."""

import pytest

from sitecheck.models import DefectType, SeverityLevel, Trade
from sitecheck.simulator import DefectSimulator


class TestDefectSimulator:
    def test_generate_finding(self):
        sim = DefectSimulator(random_seed=0)
        finding = sim.generate_finding()
        assert finding.id.startswith("F-")
        assert finding.defect_type in DefectType
        assert finding.severity in SeverityLevel
        assert 0 < finding.confidence <= 1.0

    def test_generate_findings_count(self):
        sim = DefectSimulator()
        findings = sim.generate_findings(15)
        assert len(findings) == 15

    def test_generate_inspection(self):
        sim = DefectSimulator()
        inspection = sim.generate_inspection(trade=Trade.CONCRETE, defect_count=5)
        assert inspection.defect_count == 5
        assert inspection.trade == Trade.CONCRETE
        assert inspection.checklist_completed is True

    def test_reproducibility(self):
        sim1 = DefectSimulator(random_seed=99)
        sim2 = DefectSimulator(random_seed=99)
        f1 = sim1.generate_finding()
        f2 = sim2.generate_finding()
        assert f1.defect_type == f2.defect_type
        assert f1.location == f2.location
