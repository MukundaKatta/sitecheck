"""Inspection report generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from sitecheck.models import (
    DefectFinding,
    Inspection,
    QualityScore,
    SeverityLevel,
    Trade,
    InspectionStatus,
)
from sitecheck.inspector.checklist import InspectionChecklist


@dataclass
class ReportSection:
    """A section within an inspection report."""

    title: str
    content: str
    findings: list[DefectFinding] = field(default_factory=list)


@dataclass
class InspectionReport:
    """A complete inspection report document."""

    title: str
    project_name: str
    inspector: str
    date: datetime = field(default_factory=datetime.now)
    sections: list[ReportSection] = field(default_factory=list)
    quality_score: Optional[QualityScore] = None
    recommendations: list[str] = field(default_factory=list)

    @property
    def total_findings(self) -> int:
        return sum(len(s.findings) for s in self.sections)


@dataclass
class InspectionReportGenerator:
    """Generates structured inspection reports from checklists and findings.

    Parameters
    ----------
    project_name : str
    inspector : str
    """

    project_name: str = "Unnamed Project"
    inspector: str = "Inspector"

    def generate(
        self,
        inspection: Inspection,
        checklist: Optional[InspectionChecklist] = None,
    ) -> InspectionReport:
        """Build a full :class:`InspectionReport` from an inspection record."""
        report = InspectionReport(
            title=f"Inspection Report -- {inspection.trade.value.title()}",
            project_name=self.project_name,
            inspector=self.inspector,
        )

        # Executive summary
        summary = self._executive_summary(inspection)
        report.sections.append(
            ReportSection(title="Executive Summary", content=summary)
        )

        # Findings by severity
        for severity in SeverityLevel:
            matched = [f for f in inspection.findings if f.severity == severity]
            if matched:
                section_content = self._findings_narrative(matched, severity)
                report.sections.append(
                    ReportSection(
                        title=f"{severity.value.title()} Findings",
                        content=section_content,
                        findings=matched,
                    )
                )

        # Checklist summary
        if checklist is not None:
            cl_content = self._checklist_summary(checklist)
            report.sections.append(
                ReportSection(title="Checklist Summary", content=cl_content)
            )

        # Quality score
        report.quality_score = QualityScore.compute(
            project_name=self.project_name,
            inspections=[inspection],
        )

        # Recommendations
        report.recommendations = self._recommendations(inspection)

        return report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _executive_summary(self, inspection: Inspection) -> str:
        lines = [
            f"Project: {self.project_name}",
            f"Trade: {inspection.trade.value.title()}",
            f"Date: {inspection.date:%Y-%m-%d}",
            f"Inspector: {inspection.inspector}",
            f"Status: {inspection.status.value}",
            f"Total defects found: {inspection.defect_count}",
            f"Critical defects: {inspection.critical_count}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _findings_narrative(
        findings: list[DefectFinding], severity: SeverityLevel
    ) -> str:
        lines: list[str] = []
        for f in findings:
            line = (
                f"[{f.id}] {f.defect_type.value} at {f.location} -- "
                f"{f.description}"
            )
            if f.standard_reference:
                line += f" (Ref: {f.standard_reference})"
            if f.remediation:
                line += f"\n  Remediation: {f.remediation}"
            lines.append(line)
        return "\n\n".join(lines)

    @staticmethod
    def _checklist_summary(checklist: InspectionChecklist) -> str:
        return (
            f"Trade: {checklist.trade.value.title()}\n"
            f"Items checked: {checklist.checked_items}/{checklist.total_items} "
            f"({checklist.completion_pct:.0f}%)\n"
            f"Passed: {checklist.passed_items}\n"
            f"Failed: {checklist.failed_items}"
        )

    @staticmethod
    def _recommendations(inspection: Inspection) -> list[str]:
        recs: list[str] = []
        if inspection.critical_count > 0:
            recs.append(
                "URGENT: Address all critical defects before proceeding. "
                "Stop work in affected areas until structural review is complete."
            )
        major_count = sum(
            1 for f in inspection.findings if f.severity == SeverityLevel.MAJOR
        )
        if major_count > 0:
            recs.append(
                f"Schedule repair for {major_count} major defect(s) within "
                "the next 5 working days."
            )
        minor_count = sum(
            1 for f in inspection.findings if f.severity == SeverityLevel.MINOR
        )
        if minor_count > 0:
            recs.append(
                f"Monitor {minor_count} minor defect(s); include in next "
                "scheduled maintenance."
            )
        if not recs:
            recs.append("No significant defects found. Continue as planned.")
        return recs
