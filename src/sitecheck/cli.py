"""Command-line interface for SiteCheck."""

from __future__ import annotations

import click
from rich.console import Console

from sitecheck.models import DefectType, SeverityLevel, Trade, QualityScore
from sitecheck.simulator import DefectSimulator
from sitecheck.detector.classifier import DefectClassifier
from sitecheck.detector.standards import QualityStandards, StandardCode
from sitecheck.inspector.checklist import InspectionChecklist
from sitecheck.inspector.report_gen import InspectionReportGenerator
from sitecheck.report import SiteCheckReport

console = Console()


@click.group()
@click.version_option(package_name="sitecheck")
def main() -> None:
    """SiteCheck -- Construction Defect Detector."""


@main.command()
@click.option("--defects", default=8, help="Number of defects to generate.")
@click.option(
    "--trade",
    type=click.Choice([t.value for t in Trade]),
    default="concrete",
)
def simulate(defects: int, trade: str) -> None:
    """Run a defect simulation."""
    sim = DefectSimulator()
    inspection = sim.generate_inspection(
        trade=Trade(trade), defect_count=defects
    )
    rpt = SiteCheckReport()
    rpt.findings_table(inspection.findings)

    qs = QualityScore.compute("Simulated Project", [inspection])
    rpt.quality_panel(qs)


@main.command()
@click.option(
    "--type",
    "defect_type",
    type=click.Choice([d.value for d in DefectType]),
    required=True,
)
@click.option("--measurement", type=float, required=True, help="Measurement in mm.")
@click.option("--location", default="Unspecified")
def classify(defect_type: str, measurement: float, location: str) -> None:
    """Classify a defect and get severity + remediation."""
    classifier = DefectClassifier()
    finding = classifier.classify_finding(
        defect_type=DefectType(defect_type),
        measurement_mm=measurement,
        location=location,
    )
    rpt = SiteCheckReport()
    rpt.findings_table([finding])


@main.command()
@click.option(
    "--code",
    type=click.Choice([c.value for c in StandardCode]),
    default=None,
    help="Filter by standard code.",
)
@click.option("--search", default=None, help="Search by keyword.")
def standards(code: str | None, search: str | None) -> None:
    """Look up ACI/ASTM standards tolerances."""
    qs = QualityStandards()
    if code:
        specs = qs.by_code(StandardCode(code))
    elif search:
        specs = qs.by_parameter(search)
    else:
        specs = qs.all_specs()

    from rich.table import Table

    table = Table(title="Quality Standards", show_lines=True)
    table.add_column("Code", style="bold")
    table.add_column("Section")
    table.add_column("Parameter")
    table.add_column("Tolerance", justify="right")
    table.add_column("Unit")
    table.add_column("Description", max_width=50)

    for s in specs:
        tol_str = ""
        if s.tolerance_plus is not None:
            tol_str = f"+{s.tolerance_plus}"
        if s.tolerance_minus is not None:
            tol_str += f" / -{s.tolerance_minus}"
        table.add_row(
            s.code.value,
            s.section,
            s.parameter,
            tol_str.strip(),
            s.unit,
            s.description[:80],
        )
    console.print(table)


@main.command()
@click.option(
    "--trade",
    type=click.Choice([t.value for t in Trade]),
    default="concrete",
)
def checklist(trade: str) -> None:
    """Display the inspection checklist for a trade."""
    cl = InspectionChecklist.for_trade(Trade(trade))
    rpt = SiteCheckReport()
    rpt.checklist_table(cl)


@main.command()
@click.option("--defects", default=6, help="Number of defects to simulate.")
def report(defects: int) -> None:
    """Generate a full inspection report."""
    sim = DefectSimulator()
    inspection = sim.generate_inspection(defect_count=defects)
    cl = InspectionChecklist.for_trade(Trade.CONCRETE, inspector="J. Smith")

    gen = InspectionReportGenerator(project_name="Demo Project", inspector="J. Smith")
    full_report = gen.generate(inspection, checklist=cl)

    rpt = SiteCheckReport()
    rpt.full_report(full_report)


if __name__ == "__main__":
    main()
