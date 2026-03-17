"""Trade-specific inspection checklists."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from sitecheck.models import Trade


class CheckResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NA = "na"
    NOT_CHECKED = "not_checked"


@dataclass
class CheckItem:
    """A single item on an inspection checklist."""

    id: str
    description: str
    standard_ref: str = ""
    result: CheckResult = CheckResult.NOT_CHECKED
    notes: str = ""
    photo_id: Optional[str] = None


# ------------------------------------------------------------------
# Trade-specific checklist templates
# ------------------------------------------------------------------

CONCRETE_CHECKLIST: list[dict[str, str]] = [
    {"id": "CON-01", "desc": "Formwork dimensions match drawings", "ref": "ACI 117-10 Sec 4.1"},
    {"id": "CON-02", "desc": "Formwork bracing and shoring adequate", "ref": "ACI 347R-14 Sec 3.2"},
    {"id": "CON-03", "desc": "Reinforcement size, grade, and spacing per plans", "ref": "ACI 318-19 Sec 25.2"},
    {"id": "CON-04", "desc": "Rebar cover meets minimum requirements", "ref": "ACI 318-19 Table 20.6.1.3.1"},
    {"id": "CON-05", "desc": "Rebar tied and supported properly", "ref": "ACI 301-20 Sec 3.3"},
    {"id": "CON-06", "desc": "Concrete mix design approved and verified", "ref": "ACI 318-19 Sec 26.4"},
    {"id": "CON-07", "desc": "Slump test within specified range", "ref": "ASTM C143"},
    {"id": "CON-08", "desc": "Air content within specified range", "ref": "ASTM C231"},
    {"id": "CON-09", "desc": "Concrete temperature within limits", "ref": "ACI 305R / ACI 306R"},
    {"id": "CON-10", "desc": "No visible honeycombing or bugholes > 15 mm", "ref": "ACI 301-20 Sec 5.3"},
    {"id": "CON-11", "desc": "Curing method applied within specified time", "ref": "ACI 308R-16"},
    {"id": "CON-12", "desc": "Cylinder samples taken for compressive testing", "ref": "ASTM C31"},
]

MASONRY_CHECKLIST: list[dict[str, str]] = [
    {"id": "MAS-01", "desc": "Mortar type and proportions per specification", "ref": "ASTM C270"},
    {"id": "MAS-02", "desc": "Block/brick units meet specification", "ref": "ASTM C90 / ASTM C216"},
    {"id": "MAS-03", "desc": "Wall plumbness within tolerance", "ref": "ACI 530-13 Sec 3.3F"},
    {"id": "MAS-04", "desc": "Horizontal coursing level within 6 mm per 3 m", "ref": "ACI 530-13 Sec 3.3F"},
    {"id": "MAS-05", "desc": "Grout placed per specification (lifts, vibration)", "ref": "ACI 530.1-13 Sec 3.6"},
    {"id": "MAS-06", "desc": "Reinforcement placed and tied per plans", "ref": "ACI 530-13 Sec 3.4"},
    {"id": "MAS-07", "desc": "Joint width uniform and within tolerance", "ref": "ACI 530-13 Sec 3.3B"},
    {"id": "MAS-08", "desc": "Flashing and weep holes installed correctly", "ref": "TMS 402-16 Sec 6.1"},
]

STEEL_CHECKLIST: list[dict[str, str]] = [
    {"id": "STL-01", "desc": "Steel member sizes match drawings", "ref": "AISC 360-22 Sec M2"},
    {"id": "STL-02", "desc": "Bolt type, size, and grade verified", "ref": "AISC 360-22 Sec J3"},
    {"id": "STL-03", "desc": "Bolt tightening method verified (turn-of-nut / TC)", "ref": "RCSC Sec 8"},
    {"id": "STL-04", "desc": "Weld size and length match AWS D1.1 requirements", "ref": "AWS D1.1 Sec 5"},
    {"id": "STL-05", "desc": "Visual weld inspection -- no cracks, porosity, undercut", "ref": "AWS D1.1 Table 6.1"},
    {"id": "STL-06", "desc": "Fireproofing applied to specified thickness", "ref": "ASTM E119 / UL Assembly"},
    {"id": "STL-07", "desc": "Column base plates grouted and levelled", "ref": "AISC Design Guide 1"},
    {"id": "STL-08", "desc": "Structural connections match approved shop drawings", "ref": "AISC 303-22 Sec 4"},
]

WOOD_CHECKLIST: list[dict[str, str]] = [
    {"id": "WOD-01", "desc": "Lumber species and grade per specification", "ref": "NDS 2024 Sec 4.1"},
    {"id": "WOD-02", "desc": "Moisture content within acceptable range", "ref": "NDS 2024 Table 4.1.4"},
    {"id": "WOD-03", "desc": "Connections (nails, screws, bolts) per plans", "ref": "NDS 2024 Ch. 12"},
    {"id": "WOD-04", "desc": "Joist hangers and hold-downs installed correctly", "ref": "Manufacturer specs / IRC R502.6"},
    {"id": "WOD-05", "desc": "Treated lumber used where required", "ref": "AWPA U1 / IRC R317"},
    {"id": "WOD-06", "desc": "Sheathing nailing pattern correct", "ref": "IRC Table R602.3(1)"},
    {"id": "WOD-07", "desc": "No visible decay, splits, or insect damage", "ref": "NDS 2024 Sec 2.3"},
]

PLUMBING_CHECKLIST: list[dict[str, str]] = [
    {"id": "PLB-01", "desc": "Pipe material and size per plans", "ref": "IPC 2021 Ch. 6"},
    {"id": "PLB-02", "desc": "Proper slope on drain lines (1/4 in. per ft min)", "ref": "IPC 2021 Sec 704"},
    {"id": "PLB-03", "desc": "Pressure test passed (no leaks)", "ref": "IPC 2021 Sec 312"},
    {"id": "PLB-04", "desc": "Backflow prevention devices installed", "ref": "IPC 2021 Sec 608"},
    {"id": "PLB-05", "desc": "Fixture rough-in dimensions correct", "ref": "IPC 2021 Table 405.3.1"},
    {"id": "PLB-06", "desc": "Venting system properly connected and sized", "ref": "IPC 2021 Ch. 9"},
    {"id": "PLB-07", "desc": "Clean-outs accessible and properly located", "ref": "IPC 2021 Sec 708"},
]

ELECTRICAL_CHECKLIST: list[dict[str, str]] = [
    {"id": "ELC-01", "desc": "Wire gauge matches circuit breaker rating", "ref": "NEC 2023 Table 310.16"},
    {"id": "ELC-02", "desc": "Ground-fault circuit interrupters where required", "ref": "NEC 2023 Sec 210.8"},
    {"id": "ELC-03", "desc": "Arc-fault circuit interrupters where required", "ref": "NEC 2023 Sec 210.12"},
    {"id": "ELC-04", "desc": "Outlet and switch box fill calculations met", "ref": "NEC 2023 Sec 314.16"},
    {"id": "ELC-05", "desc": "Panel labelling complete and accurate", "ref": "NEC 2023 Sec 408.4"},
    {"id": "ELC-06", "desc": "Grounding and bonding per specification", "ref": "NEC 2023 Art. 250"},
    {"id": "ELC-07", "desc": "Conduit fill within allowed capacity", "ref": "NEC 2023 Ch. 9 Table 1"},
    {"id": "ELC-08", "desc": "Conductor insulation type suitable for environment", "ref": "NEC 2023 Table 310.4(1)"},
]

TRADE_CHECKLISTS: dict[Trade, list[dict[str, str]]] = {
    Trade.CONCRETE: CONCRETE_CHECKLIST,
    Trade.MASONRY: MASONRY_CHECKLIST,
    Trade.STEEL: STEEL_CHECKLIST,
    Trade.WOOD: WOOD_CHECKLIST,
    Trade.PLUMBING: PLUMBING_CHECKLIST,
    Trade.ELECTRICAL: ELECTRICAL_CHECKLIST,
}


@dataclass
class InspectionChecklist:
    """A trade-specific inspection checklist.

    Use :meth:`for_trade` to create a checklist pre-populated with the
    standard items for a given trade.
    """

    trade: Trade
    items: list[CheckItem] = field(default_factory=list)
    inspector: str = ""
    date: datetime = field(default_factory=datetime.now)

    @classmethod
    def for_trade(cls, trade: Trade, inspector: str = "") -> "InspectionChecklist":
        """Create a checklist pre-loaded with standard items for *trade*."""
        template = TRADE_CHECKLISTS.get(trade, [])
        items = [
            CheckItem(id=item["id"], description=item["desc"], standard_ref=item["ref"])
            for item in template
        ]
        return cls(trade=trade, items=items, inspector=inspector)

    def check(self, item_id: str, result: CheckResult, notes: str = "") -> None:
        """Record a check result for the item with the given ID."""
        for item in self.items:
            if item.id == item_id:
                item.result = result
                item.notes = notes
                return
        raise KeyError(f"Item '{item_id}' not found in checklist")

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def checked_items(self) -> int:
        return sum(1 for i in self.items if i.result != CheckResult.NOT_CHECKED)

    @property
    def passed_items(self) -> int:
        return sum(1 for i in self.items if i.result == CheckResult.PASS)

    @property
    def failed_items(self) -> int:
        return sum(1 for i in self.items if i.result == CheckResult.FAIL)

    @property
    def completion_pct(self) -> float:
        if self.total_items == 0:
            return 100.0
        return (self.checked_items / self.total_items) * 100.0

    @property
    def is_complete(self) -> bool:
        return self.checked_items == self.total_items

    def failures(self) -> list[CheckItem]:
        return [i for i in self.items if i.result == CheckResult.FAIL]
