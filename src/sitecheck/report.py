"""Rich-formatted reports for SiteCheck."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from sitecheck.models import (
    DefectFinding,
    Inspection,
    QualityScore,
    SeverityLevel,
)
from sitecheck.inspector.checklist import InspectionChecklist, CheckResult
from sitecheck.inspector.report_gen import InspectionReport


SEVERITY_COLOURS: dict[SeverityLevel, str] = {
    SeverityLevel.COSMETIC: "dim",
    SeverityLevel.MINOR: "yellow",
    SeverityLevel.MAJOR: "red",
    SeverityLevel.CRITICAL: "bold red",
}


@dataclass
class SiteCheckReport:
    """Renders SiteCheck data to the terminal using Rich."""

    console: Console = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.console is None:
            self.console = Console()

    # ------------------------------------------------------------------
    # Findings table
    # ------------------------------------------------------------------
    def findings_table(self, findings: list[DefectFinding]) -> None:
        table = Table(title="Defect Findings", show_lines=True)
        table.add_column("ID", style="bold")
        table.add_column("Type")
        table.add_column("Severity")
        table.add_column("Location")
        table.add_column("Confidence", justify="right")
        table.add_column("Standard Ref")
        table.add_column("Remediation", max_width=40)

        for f in findings:
            colour = SEVERITY_COLOURS.get(f.severity, "white")
            table.add_row(
                f.id,
                f.defect_type.value,
                Text(f.severity.value, style=colour),
                f.location,
                f"{f.confidence:.0%}",
                f.standard_reference or "",
                f.remediation or "",
            )
        self.console.print(table)

    # ------------------------------------------------------------------
    # Quality score
    # ------------------------------------------------------------------
    def quality_panel(self, qs: QualityScore) -> None:
        grade_colour = {
            "A": "green", "B": "cyan", "C": "yellow", "D": "red", "F": "bold red",
        }.get(qs.grade, "white")

        text = (
            f"Project: {qs.project_name}\n"
            f"Section: {qs.section}\n"
            f"Score: {qs.score:.1f}/100\n"
            f"Grade: [{grade_colour}]{qs.grade}[/{grade_colour}]\n"
            f"Inspections: {qs.total_inspections}\n"
            f"Total defects: {qs.total_defects}\n"
            f"Critical: {qs.critical_defects}\n"
            f"Compliance: {qs.compliance_pct:.1f}%"
        )
        self.console.print(Panel(text, title="Quality Score", border_style="blue"))

    # ------------------------------------------------------------------
    # Checklist
    # ------------------------------------------------------------------
    def checklist_table(self, checklist: InspectionChecklist) -> None:
        table = Table(
            title=f"Inspection Checklist -- {checklist.trade.value.title()}",
            show_lines=True,
        )
        table.add_column("ID", style="bold")
        table.add_column("Description", max_width=50)
        table.add_column("Standard", max_width=30)
        table.add_column("Result")
        table.add_column("Notes", max_width=30)

        result_colours = {
            CheckResult.PASS: "green",
            CheckResult.FAIL: "red",
            CheckResult.NA: "dim",
            CheckResult.NOT_CHECKED: "yellow",
        }
        for item in checklist.items:
            colour = result_colours.get(item.result, "white")
            table.add_row(
                item.id,
                item.description,
                item.standard_ref,
                Text(item.result.value, style=colour),
                item.notes,
            )
        self.console.print(table)
        self.console.print(
            f"Completion: {checklist.completion_pct:.0f}% "
            f"({checklist.checked_items}/{checklist.total_items})"
        )

    # ------------------------------------------------------------------
    # Full report
    # ------------------------------------------------------------------
    def full_report(self, report: InspectionReport) -> None:
        self.console.print(
            Panel(
                f"[bold]{report.title}[/bold]\n"
                f"Project: {report.project_name}\n"
                f"Inspector: {report.inspector}\n"
                f"Date: {report.date:%Y-%m-%d}",
                border_style="blue",
            )
        )

        for section in report.sections:
            self.console.print(f"\n[bold underline]{section.title}[/bold underline]")
            self.console.print(section.content)
            if section.findings:
                self.findings_table(section.findings)

        if report.quality_score:
            self.quality_panel(report.quality_score)

        if report.recommendations:
            self.console.print("\n[bold underline]Recommendations[/bold underline]")
            for i, rec in enumerate(report.recommendations, 1):
                self.console.print(f"  {i}. {rec}")

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def dashboard(
        self,
        inspection: Optional[Inspection] = None,
        checklist: Optional[InspectionChecklist] = None,
        quality: Optional[QualityScore] = None,
    ) -> None:
        self.console.print(
            Panel("[bold]SiteCheck Dashboard[/bold]", border_style="blue")
        )
        if inspection:
            self.findings_table(inspection.findings)
        if checklist:
            self.checklist_table(checklist)
        if quality:
            self.quality_panel(quality)
